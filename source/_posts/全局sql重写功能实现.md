---
title: 全局sql重写功能实现
date: 2021-01-20 20:16:11
tags:
---

### sql重写策略类型枚举：RebuildType

```java
public enum RebuildType {
    /**
     *重写sql
     */
    REBUILD_SQL,
    /**
     * 重置memberId参数
     */
    RESET_PARAM,
    /**
     * 跳过sql重写
     */
    SKIP_REBUILD
}
```

### sql重写配置注解类：RebuildMemberData

```java
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 〈一句话功能简述〉<br>
 * ibatis/mybatis 添加数据权限(全局sql重写)控制：
 * 1.在sql中拼接memberId查询条件或insert中添加插入字段
 * 2.直接sql中重置memberId参数值为当前线程memberId
 * 3.忽略rebuild功能，直接执行原生的sql
 *
 * 注意：
 *    a)当没有被该注释注解的dao方法默认执行SKIP_REBUILD(跳过sql重写)策略
 *    b)该注释可以加在dao实现类(mapper接口)或dao(mapper)方法上
 *    c)注释如果加在dao实现类(mapper接口),默认对所有的方法指定统一的rebuild策略
 *    d)可以通过配置value参数指定的sql(ibatis)或mapper方法(mybatis)进行选择添加rebuild功能
 *    e)注释如果加在方法上,则只对该方法添加rebuild功能
 *    f)在方法上配置的rebuild策略的优先级高于在类或接口上配置的rebuild策略
 *    g)在父类或父接口上指定策rebuild策略对于子类或子接口不生效
 *    h)在父类或父接口的方法上指定策rebuild策略对于子类或子接口生效,如果需要在子类上修改策略,则必须重载方法或通过类注解中指定特定策略
 */
@Target({ElementType.TYPE,ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface RebuildMemberData {
    /**
     * 指定的sql(ibatis)或mapper方法(mybatis)进行选择添加rebuild功能
     *
     * 注意：
     *    该参数只有当注释加在dao实现类(mapper接口)才生效
     * @return
     */
    String[] value()  default {};

    /**
     * 配置指定的sql重写策略：默认为sql重写
     * @return
     */
    RebuildType rebuildType() default RebuildType.REBUILD_SQL;
}
```

### dao方法执行aop拦截器：RebuildMemberDataDaoAspect

```java
import com.banksteel.openerp.commons.filter.SaasParameter;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.*;
import org.aspectj.lang.reflect.MethodSignature;
import java.lang.reflect.Method;

/**
 * 〈一句话功能简述〉<br>
 * ibatis风格的dao实现中，不能在mybaits拦截中获取到当前调用执行sql的具体dao方法,
 * 所以需要通过该aop拦截器拦截dao方法,在执行前将该dao方法存放到线程级变量中,
 * 以备在后续的mybatis拦截器中能够获取到当前执行sql的具体dao方法
 */
@Aspect
public class RebuildMemberDataDaoAspect {

    @Around(value = "@annotation(com.banksteel.openerp.commons.interceptor.RebuildMemberData)")
    public Object interceptorCorsReq(ProceedingJoinPoint joinPoint) throws Throwable {
        Object object = joinPoint.getTarget();
        Class targetClazz = object.getClass();

        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        // 获取当前执行的方法签名,并在执行方法前存放到线程级变量中
        // 方法签名一般会获取到接口或父类中的方法签名,所以需要重写从目标代理类中重新获取一次
        Method method = signature.getMethod();

        Method daoMethod = targetClazz.getMethod(method.getName(),method.getParameterTypes());
        if(daoMethod != null){
            method = daoMethod;
        }
        SaasParameter.setCurrentDaoMethod(method);

        Object objResult = joinPoint.proceed();

        // 在执行完dao方法后清除掉该线程级变量
        SaasParameter.setCurrentDaoMethod(null);
        return objResult;
    }
}
```

### mybatis全局sql重写拦截器：RebuildSqlInterceptor 获取sql rebuild策略的主方法

```java
import java.lang.reflect.Method;
import java.sql.Connection;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import net.sf.jsqlparser.JSQLParserException;
import org.apache.commons.lang.StringUtils;
import org.apache.ibatis.executor.statement.StatementHandler;
import org.apache.ibatis.mapping.BoundSql;
import org.apache.ibatis.mapping.MappedStatement;
import org.apache.ibatis.mapping.ParameterMapping;
import org.apache.ibatis.plugin.Interceptor;
import org.apache.ibatis.plugin.Intercepts;
import org.apache.ibatis.plugin.Invocation;
import org.apache.ibatis.plugin.Plugin;
import org.apache.ibatis.plugin.Signature;
import org.apache.ibatis.reflection.MetaObject;
import org.apache.ibatis.reflection.SystemMetaObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.CollectionUtils;
import org.springframework.util.ReflectionUtils;

/**
 * 重建SQL语句拦截器
 */
@Intercepts({ @Signature(method = "prepare", type = StatementHandler.class, args = { Connection.class }) })
public class RebuildSqlInterceptor implements Interceptor {
	static Logger logger = LoggerFactory.getLogger(RebuildSqlInterceptor.class);

	private ConcurrentHashMap<String,Class> daoSqlClazzs = new ConcurrentHashMap<>();
	private ConcurrentHashMap<String,Method> mybatisMethods = new ConcurrentHashMap<>();
	private final String pageContSqlSuffix = "_COUNT";

	@Override
	public Object intercept(Invocation invocation) throws Throwable {
		StatementHandler statementHandler = (StatementHandler) invocation.getTarget();
		// 创建反射工具类，用于获取和设置SQL语句
		MetaObject metaStatementHandler = SystemMetaObject.forObject(statementHandler);

		// 获取拦截的SQL语句
		MappedStatement mappedStatement = (MappedStatement) metaStatementHandler.getValue("delegate.mappedStatement");
		String daoSqlId = mappedStatement.getId();

		RebuildType rebuildType = computeRebuildType(daoSqlId);
		Long memberId = getCurrentMemberId();
		BoundSql boundSql = (BoundSql) metaStatementHandler.getValue("delegate.boundSql");

		if (Objects.equals(rebuildType , RebuildType.REBUILD_SQL)){
			rebuildSql(metaStatementHandler, mappedStatement, boundSql, memberId);
		}else if (Objects.equals(rebuildType , RebuildType.RESET_PARAM)){
			resetParam(metaStatementHandler, mappedStatement, boundSql, memberId);
		}

		Object result = invocation.proceed();
		return result;
	}

	/**
	 * 获取当前上下文中的memberId
	 * @return
	 */
	private Long getCurrentMemberId() {
		// 获取本地线程变量
		Long memberId = 0L;
		try {
			if (StringUtils.isNotEmpty(SaasParameter.getMemberId())) {
				memberId = Long.parseLong(SaasParameter.getMemberId());
			}
		} catch (Exception e) {
			logger.error("【noSaas拦截构建】会员ID转换异常，id=" + memberId, e);
		}
		return memberId;
	}

	/**
	 * 重置sql查询参数
	 * @param metaStatementHandler
	 * @param mappedStatement
	 * @param boundSql
	 * @param memberId
	 */
	private void resetParam(MetaObject metaStatementHandler, MappedStatement mappedStatement, BoundSql boundSql, Long memberId) {
		if(memberId <= 0){
			return;
		}
		if ("SELECT".equals(mappedStatement.getSqlCommandType().toString())
				|| "INSERT".equals(mappedStatement.getSqlCommandType().toString())) {
			boundSql.setAdditionalParameter("memberId", memberId);
			metaStatementHandler.setValue("delegate.boundSql", boundSql);
		}
	}

	/**
	 * 重写sql
	 * @param metaStatementHandler
	 * @param mappedStatement
	 * @param boundSql
	 * @param memberId
	 * @throws JSQLParserException
	 */
	private void rebuildSql(MetaObject metaStatementHandler, MappedStatement mappedStatement, BoundSql boundSql, Long memberId) throws JSQLParserException {
		if(memberId <= 0){
			return;
		}
		// 当statement的id不以noSaas结尾，且memberId>0，则执行对INSERT与SELECT语句的重构
		if ("SELECT".equals(mappedStatement.getSqlCommandType().toString())) {
			List<ParameterMapping> parameterMappings = boundSql.getParameterMappings();
			metaStatementHandler.setValue("delegate.boundSql.sql", RebuildSqlUtils.rebuildQuery(boundSql.getSql(),
					memberId.toString(), parameterMappings));
		} else if ("INSERT".equals(mappedStatement.getSqlCommandType().toString())) {
			metaStatementHandler.setValue("delegate.boundSql.sql",
					RebuildSqlUtils.rebuildInsert(boundSql.getSql(), memberId.toString()));
		}
	}

	public Object plugin(Object target) {
		// 当目标类是StatementHandler类型时，才包装目标类，否者直接返回目标本身,减少目标被代理的次数
		if (target instanceof StatementHandler) {
			return Plugin.wrap(target, this);
		} else {
			return target;
		}
	}

	public void setProperties(Properties properties) {
		//do nothing
	}

	/**
	 * 通过反射机制和上下文方法中计算sql的重构类型
	 * @param daoSqlId
	 * @return
	 */
	private RebuildType computeRebuildType(String daoSqlId){
		try{
			// 1.获取命名空间类型和执行的sqlId
			int lastIndex = StringUtils.lastIndexOf(daoSqlId,".");
			String daoClassName = StringUtils.substring(daoSqlId,0,lastIndex);
			String sqlMethodName = StringUtils.substring(daoSqlId,lastIndex + 1);

			// 2.将命名空间类型反射为class
			Class clazz = getClassByDaoSql(daoClassName);

			// 3.通过当前执行的dao方法获取sql rebuild 类型,如果获得的RebuildType为null,则尝试从类或接口上获取
			RebuildType rebuildType = computeRebuildTypeByDaoMethod(clazz,sqlMethodName,daoSqlId);

			if(rebuildType != null){
				return rebuildType;
			}else{
				// 4.判断当前执行的sqlMethod方法是否需要跳过
				return computeRebuildTypeByClazz(clazz,sqlMethodName);
			}
		}catch (Exception e){
			logger.warn(String.format("[%s]获取sql重构类型时异常，使用默认SKIP_REBUILD策略",daoSqlId),e);
			return RebuildType.SKIP_REBUILD;
		}
	}

	/**
	 * 获取注解上的所有定义需要跳过的sql
	 * @param skipRebuildMemberId
	 * @return
	 */
	private Set<String> getRebuildSqls(RebuildMemberData skipRebuildMemberId){
		return new HashSet<>(Arrays.asList(skipRebuildMemberId.value()));
	}

	/**
	 * 获取当前执行的方法,然后在拉取方法上的RebuildMemberData来获取该方法指定的RebuildType
	 */
	private RebuildType computeRebuildTypeByDaoMethod(Class daoClazz, String sqlMethodName, String daoSqlId) {
		Method sqlMethod = getCurrentSqlMethod (daoClazz, sqlMethodName,daoSqlId);
		if(sqlMethod != null && sqlMethod.isAnnotationPresent(RebuildMemberData.class)){
			Class methodClazz = sqlMethod.getDeclaringClass();
			RebuildMemberData rebuildMemberData = sqlMethod.getAnnotation(RebuildMemberData.class);
			return (methodClazz.isAssignableFrom(daoClazz) && rebuildMemberData != null) ?  rebuildMemberData.rebuildType() : null ;
		}
		return null ;
	}

	/**
	 * 获取当前执行方法：
	 *  如果当前dao类为接口:则表示是通过mybatis风格编写dao层，则通过反射获取当前执行的dao方法
	 *     因mybatis只有接口没有实现类,所以aop拦截不到mybatis的dao方法
	 *     但mybatis的dao中是不允许存在方法重载,所以一个方法名就只对应一个具体的方法,
	 *     所以可以直接通过方法名方式获取到对应的dao方法
	 *  否则则表示通过ibatis风格编写dao层，则从线程上下文中获取通过aop拦截存入的当前执行方法
	 * @param daoClazz
	 * @param sqlMethodName
	 * @return
	 */
	private Method getCurrentSqlMethod(Class daoClazz, String sqlMethodName, String daoSqlId){
		// mybatis风格配置,通过反射获取当前执行方法
		if(daoClazz.isInterface()){
			try{
				if (mybatisMethods.contains(daoSqlId)){
					return mybatisMethods.get(daoSqlId);
				}else {
					Method daoMethod = getMybatisMethod(daoClazz,sqlMethodName,daoSqlId);
					if(daoMethod!=null){
						mybatisMethods.putIfAbsent(daoSqlId,daoMethod);
					}
					return daoMethod;
				}
			}catch (Exception e){
				logger.warn(String.format("[%s.%s]获取sql重构类型时异常，使用默认SKIP_REBUILD策略",daoClazz.getName(),sqlMethodName),e);
				return null;
			}
		}else { // ibatis风格配置,通过线程级上下文获取当前执行sql方法
			return SaasParameter.getCurrentDaoMethod();
		}

	}

	private Method getMybatisMethod(Class daoClazz, String sqlMethodName, String daoSqlId) throws NoSuchMethodException, ClassNotFoundException {
		Method daoMethod ;
		try{
			daoMethod = ReflectionUtils.findMethod(daoClazz,sqlMethodName,null);
			if (Objects.isNull(daoMethod) && StringUtils.endsWith(sqlMethodName,pageContSqlSuffix)){
				String listMethodName = StringUtils.substring(sqlMethodName,0,sqlMethodName.length() - pageContSqlSuffix.length());
				daoMethod = ReflectionUtils.findMethod(daoClazz,listMethodName,null);
			}
		}catch (Exception e){
			if(StringUtils.endsWith(sqlMethodName,pageContSqlSuffix)){
				String listMethodName = StringUtils.substring(sqlMethodName,0,sqlMethodName.length() - pageContSqlSuffix.length());
				daoMethod = ReflectionUtils.findMethod(daoClazz,listMethodName,null);
			}else{
				throw e;
			}
		}
		return daoMethod;
	}

	/**
	 * 判断是否需要指定sql是否需要跳过
	 * 1.类上必须要有SkipRebuildMemberId注解
	 * 2.注解值为空
	 * 3.注解值中包含sql
	 * 条件1必须满足，条件2和条件3只需满足其中一个
	 * @param clazz
	 * @param sql
	 * @return
	 */
	private RebuildType computeRebuildTypeByClazz(Class clazz,String sql){
		if(clazz.isAnnotationPresent(RebuildMemberData.class)){
			RebuildMemberData rebuildMemberData = (RebuildMemberData)clazz.getAnnotation(RebuildMemberData.class);
			Set<String> skipSqls = getRebuildSqls(rebuildMemberData);
			if(CollectionUtils.isEmpty(skipSqls) || skipSqls.contains(sql)){
				return rebuildMemberData.rebuildType();
			}
		}
		return  RebuildType.SKIP_REBUILD;
	}

	private Class getClassByDaoSql(String daoClass){
		if(daoSqlClazzs.contains(daoClass)){
			return daoSqlClazzs.get(daoClass);
		}

		try{
			Class daoClazz = Class.forName(daoClass);
			daoSqlClazzs.putIfAbsent(daoClass,daoClazz);
			return daoClazz;
		}catch (Exception e){
			logger.warn(String.format("[%s]获取sql重构类型时异常，使用默认SKIP_REBUILD策略",daoClass),e);
			return null;
		}
	}
}
```



