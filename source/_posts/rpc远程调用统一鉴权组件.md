---
title: rpc远程调用统一鉴权组件
date: 2021-02-26 15:55:29
tags:
---

### 组件背景： 
因为很多的业务平台，大多数进行数据查询的时候，需要通过memberId去做数据隔离。同时 配合统一sql重新组件的工作，所以需要通过在框架层面上对rpc上下文参数进行设置、校 验、传递。 

### 组件原理： 
1.在服务消费端通过dubbo过滤器，从线程级变量中获取上下文参数(saas中只要判断 memberId是否存在)，并判断当前请求接口是否需要进行鉴权，如果需要进行鉴权而则校 验上下文参数是否合法，不合法则直接抛出异常；
 2.将获取到的上下文参数放到dubbo的rpc请求上下文中；
 3.服务生产端获取dubbo的rpc上下文参数，如果存在则存放到线程级变量中，判断当前请 求接口是否需要进行鉴权，如果需要进行鉴权而则校验上下文参数是否合法，不合法则直接 抛出异常。

### rpc统一鉴权时序图：
![](/images/rpc统一鉴权时序图.jpg)


### rpc统一鉴权策略描述注解类： RpcAuthority
通过该注解可以给指定的rpc方法设置rpc鉴权策略，现在指指定了要鉴权和不要鉴权两个策 略，后续如果需要更强的扩展性，可以将鉴权类型指定为整数值，在具体的鉴权实现中再 根据这个整数值来制定具体的鉴权策略。
```java
import com.lixiang.dubbo.authority.RpcType;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target({ElementType.METHOD, ElementType.TYPE, ElementType.PACKAGE})
@Retention(RetentionPolicy.RUNTIME)
public @interface RpcAuthority {
    RpcType rpcType() default RpcType.RPC;
}
```

### rpc统一鉴权功能描述接口类：AuthorityHandler
```java
import com.lixiang.dubbo.TokenInfo;
import com.lixiang.dubbo.authority.exception.RpcAuthorityException;
import org.apache.dubbo.rpc.Invocation;
import org.apache.dubbo.rpc.Invoker;

public interface AuthorityHandler<T extends TokenInfo>{
    void customerCheck (Invoker<?> invoker, Invocation invocation) throws RpcAuthorityException;

    void providerCheck (Invoker<?> invoker, Invocation invocation) throws RpcAuthorityException;

    T convertToToken (String tokenInfo);
}
```

### rpc请求信息描述类：RpcInfo
```java
import java.util.Arrays;
import java.util.Objects;

public class RpcInfo {
    private Class interfaceClazz;
    private String rpcMethod;
    private Class<?>[] parameterTypes;

    public Class getInterfaceClazz() {
        return interfaceClazz;
    }

    public void setInterfaceClazz(Class interfaceClazz) {
        this.interfaceClazz = interfaceClazz;
    }

    public String getRpcMethod() {
        return rpcMethod;
    }

    public void setRpcMethod(String rpcMethod) {
        this.rpcMethod = rpcMethod;
    }

    public Class<?>[] getParameterTypes() {
        return parameterTypes;
    }

    public void setParameterTypes(Class<?>[] parameterTypes) {
        this.parameterTypes = parameterTypes;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        RpcInfo rpcInfo = (RpcInfo) o;
        return Objects.equals(interfaceClazz, rpcInfo.interfaceClazz) &&
                Objects.equals(rpcMethod, rpcInfo.rpcMethod) &&
                Arrays.equals(parameterTypes, rpcInfo.parameterTypes);
    }

    @Override
    public int hashCode() {
        int result = Objects.hash(interfaceClazz, rpcMethod);
        result = 31 * result + Arrays.hashCode(parameterTypes);
        return result;
    }
}
```

### 鉴权策略实现： SimpleAuthorityHandler 

```java
import com.alibaba.fastjson.JSONObject;
import com.lixiang.dubbo.authority.AuthorityHandler;
import com.lixiang.dubbo.authority.RpcType;
import com.lixiang.dubbo.authority.annotation.RpcAuthority;
import com.lixiang.dubbo.authority.exception.RpcAuthorityException;
import com.lixiang.dubbo.rpc.DubboRpcUtils;
import com.lixiang.dubbo.rpc.RpcInfo;
import com.lixiang.dubbo.utils.AnnotationUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.dubbo.rpc.Invocation;
import org.apache.dubbo.rpc.Invoker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.lang.reflect.Method;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;

public class SimpleAuthorityHandler implements AuthorityHandler<MemberIdToken> {
    private static Logger logger = LoggerFactory.getLogger(SimpleAuthorityHandler.class);
    private ConcurrentHashMap<RpcInfo, RpcType> rpcAuthorityConfig = new ConcurrentHashMap<>();
    private RpcType defaultRpcType = RpcType.COMMON;
    public static final String RPC_TOKEN_NAME = "rpcTokenName";
    private static final ThreadLocal<MemberIdToken> CURRENT_USER_INFO = new ThreadLocal<>();

    @Override
    public void customerCheck(Invoker<?> invoker, Invocation invocation) throws RpcAuthorityException {
        MemberIdToken token = CURRENT_USER_INFO.get();
        checkToken(invoker, invocation, token);
        if (token != null) {
            invocation.getAttachments().put(RPC_TOKEN_NAME, JSONObject.toJSONString(token));
        }
    }
    @Override
    public void providerCheck(Invoker<?> invoker, Invocation invocation) throws RpcAuthorityException {
        String tokenInfo = invocation.getAttachment(RPC_TOKEN_NAME);
        MemberIdToken token = convertToToken(tokenInfo);
        checkToken(invoker, invocation, token);
        if (token != null) {
            setToken(token);
        } else {
            setToken(-1L);
        }
    }

    private void checkToken(Invoker<?> invoker, Invocation invocation, MemberIdToken token) throws RpcAuthorityException {
        if (token == null || token.getMemberId() == null) {
            RpcInfo rpcInfo = DubboRpcUtils.getInvokerRpcInfo(invoker, invocation);
            RpcType rpcType;
            if (rpcAuthorityConfig.containsKey(rpcInfo)) {
                rpcType = rpcAuthorityConfig.get(rpcInfo);
            } else {
                rpcType = getRpcType(rpcInfo);
                rpcAuthorityConfig.putIfAbsent(rpcInfo, rpcType);
            }
            if (Objects.equals(RpcType.RPC, rpcType)) {
                throw new RpcAuthorityException(String.format("rpc请求[%s]的rpc 权限不合法", JSONObject.toJSONString(rpcInfo)));
            }
        }
    }

    @Override
    public MemberIdToken convertToToken(String tokenInfo) {
        MemberIdToken token = null;
        if (StringUtils.isNotEmpty(tokenInfo)) {
            try {
                token = JSONObject.parseObject(tokenInfo, MemberIdToken.class);
            } catch (Exception e) {
                logger.warn("rpc MemberIdToken 格式不对", e);
            }
        }
        return token;
    }

    private RpcType getRpcType(RpcInfo rpcInfo) {
        Class interfaceClazz = rpcInfo.getInterfaceClazz();
        Package interfacePackage = interfaceClazz.getPackage();
        RpcAuthority packageRpcAuthority = AnnotationUtils.recursionGet(interfacePackage, RpcAuthority.class);
        RpcAuthority clazzRpcAuthority = (RpcAuthority) interfaceClazz.getAnnotation(RpcAuthority.class);
        try {
            Method rpcMethod = interfaceClazz.getMethod(rpcInfo.getRpcMethod(), rpcInfo.getParameterTypes());
            RpcAuthority methodRpcAuthority = rpcMethod.getAnnotation(RpcAuthority.class);

            if (methodRpcAuthority != null) {
                return methodRpcAuthority.rpcType();
            } else if (clazzRpcAuthority != null) {
                return clazzRpcAuthority.rpcType();
            } else if (packageRpcAuthority != null) {
                return packageRpcAuthority.rpcType();
            } else {
                return defaultRpcType;
            }

        } catch (NoSuchMethodException e) {
            throw new RpcAuthorityException(e);
        }
    }

    public static void setToken(MemberIdToken token) {
        CURRENT_USER_INFO.set(token);
    }

    public static void setToken(Long memberId) {
        MemberIdToken token = new MemberIdToken();
        token.setMemberId(memberId);
        setToken(token);
    }

    public static MemberIdToken getToken() {
        return CURRENT_USER_INFO.get();
    }

    public static void setUserId(Long userId) {
        MemberIdToken token = CURRENT_USER_INFO.get();
        token.setUserId(userId);
        setToken(token);
    }
}
```

1.获取rpc服务鉴权级别方法: 通过按照就近原则获取服务鉴权级别：按照方法签名注解->接口签名注解->包签名注解路 径去寻找RpcAuthority注解，如果有RpcAuthority注解，立马返回，如果都没有找到，则 指定为默认鉴权级别：不需要进行鉴权

```java
	private RpcType getRpcType(RpcInfo rpcInfo) {
        Class interfaceClazz = rpcInfo.getInterfaceClazz();
        Package interfacePackage = interfaceClazz.getPackage();
        RpcAuthority packageRpcAuthority = AnnotationUtils.recursionGet(interfacePackage, RpcAuthority.class);
        RpcAuthority clazzRpcAuthority = (RpcAuthority) interfaceClazz.getAnnotation(RpcAuthority.class);
        try {
            Method rpcMethod = interfaceClazz.getMethod(rpcInfo.getRpcMethod(), rpcInfo.getParameterTypes());
            RpcAuthority methodRpcAuthority = rpcMethod.getAnnotation(RpcAuthority.class);

            if (methodRpcAuthority != null) {
                return methodRpcAuthority.rpcType();
            } else if (clazzRpcAuthority != null) {
                return clazzRpcAuthority.rpcType();
            } else if (packageRpcAuthority != null) {
                return packageRpcAuthority.rpcType();
            } else {
                return defaultRpcType;
            }

        } catch (NoSuchMethodException e) {
            throw new RpcAuthorityException(e);
        }
    }
```

2.服务消费端鉴权校验 从线程级变量中获取上下文参数(saas中只要判断memberId是否存在)，并将获取到的上下 文参数放到dubbo的rpc请求上下文中（不管是否需求鉴权，都会把线程上下文推到rpc上 下文中），判断当前请求接口是否需要进行鉴权，如果需要进行鉴权而则校验上下文参数是 否合法，不合法则直接抛出异常。

```java
	@Override
    public void customerCheck(Invoker<?> invoker, Invocation invocation) throws RpcAuthorityException {
        MemberIdToken token = CURRENT_USER_INFO.get();
        checkToken(invoker, invocation, token);
        if (token != null) {
            invocation.getAttachments().put(RPC_TOKEN_NAME, JSONObject.toJSONString(token));
        }
    }

    private void checkToken(Invoker<?> invoker, Invocation invocation, MemberIdToken token) throws RpcAuthorityException {
        if (token == null || token.getMemberId() == null) {
            RpcInfo rpcInfo = DubboRpcUtils.getInvokerRpcInfo(invoker, invocation);
            RpcType rpcType;
            if (rpcAuthorityConfig.containsKey(rpcInfo)) {
                rpcType = rpcAuthorityConfig.get(rpcInfo);
            } else {
                rpcType = getRpcType(rpcInfo);
                rpcAuthorityConfig.putIfAbsent(rpcInfo, rpcType);
            }
            if (Objects.equals(RpcType.RPC, rpcType)) {
                throw new RpcAuthorityException(String.format("rpc请求[%s]的rpc 权限不合法", JSONObject.toJSONString(rpcInfo)));
            }
        }
    }
```

3.服务生产端鉴权校验 服务生产端获取dubbo的rpc上下文参数，如果存在则存放到线程级变量中，判断当前请求 接口是否需要进行鉴权，如果需要进行鉴权而则校验上下文参数是否合法，不合法则直接抛 出异常。

```java
@Override
    public void providerCheck(Invoker<?> invoker, Invocation invocation) throws RpcAuthorityException {
        String tokenInfo = invocation.getAttachment(RPC_TOKEN_NAME);
        MemberIdToken token = convertToToken(tokenInfo);
        checkToken(invoker, invocation, token);
        if (token != null) {
            setToken(token);
        } else {
            setToken(-1L);
        }
    }
```

### 服务消费端鉴权拦截器： CustomerFilter

```java
import com.alibaba.fastjson.JSONObject;
import com.lixiang.dubbo.authority.AuthorityHandler;
import com.lixiang.dubbo.simpletoken.SimpleAuthorityHandler;
import org.apache.dubbo.common.constants.CommonConstants;
import org.apache.dubbo.common.extension.Activate;
import org.apache.dubbo.rpc.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Activate(group = CommonConstants.CONSUMER)
public class CustomerFilter implements Filter {
    private AuthorityHandler authorityHandler = new SimpleAuthorityHandler();
    private static Logger logger = LoggerFactory.getLogger(CustomerFilter.class);

    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        try {
            authorityHandler.customerCheck(invoker, invocation);
        } catch (RpcException e) {
            writeRpcErrorLog(e, invoker, invocation);
            throw e;
        }

        try {
            Result result = invoker.invoke(invocation);
            if (result.hasException()) {
                writeRpcErrorLog(result.getException(), invoker, invocation);
            }
            return result;
        } catch (Exception e) {
            writeRpcErrorLog(e, invoker, invocation);
            throw e;
        }
    }

    private void writeRpcErrorLog(Throwable e, Invoker<?> invoker, Invocation invocation) {
        RpcInfo rpcInfo = DubboRpcUtils.getInvokerRpcInfo(invoker, invocation);
        Object[] args = invocation.getArguments();

        logger.warn(String.format("rpc接口信息:%s,rpc请  求参数:%s,异常信息:%s",
                JSONObject.toJSONString(rpcInfo),
                JSONObject.toJSONString(args),
                e.getMessage()
        ), e);
    }
}
```

### 服务生产端端鉴权拦截器：ProviderFilter

```java
import com.lixiang.dubbo.authority.AuthorityHandler;
import com.lixiang.dubbo.simpletoken.SimpleAuthorityHandler;
import org.apache.dubbo.common.constants.CommonConstants;
import org.apache.dubbo.common.extension.Activate;
import org.apache.dubbo.rpc.Filter;
import org.apache.dubbo.rpc.Invocation;
import org.apache.dubbo.rpc.Invoker;
import org.apache.dubbo.rpc.RpcException;
import org.apache.dubbo.rpc.*;

@Activate(group = CommonConstants.PROVIDER)
public class ProviderFilter implements Filter {

    private AuthorityHandler authorityHandler = new SimpleAuthorityHandler();

    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        authorityHandler.providerCheck(invoker, invocation);
        return invoker.invoke(invocation);
    }
}
```

### 设置默认装载自定义过滤器：在工程resource下的META-INF目录下创建dubbo 目录，并创建文件com.alibaba.dubbo.rpc.Filter，指定自定义的异常处理Filter类为默认扩展点

```java
xiangxiangCustomerFilter=com.lixiang.dubbo.rpc.CustomerFilter
xiangxiangProviderFilter=com.lixiang.dubbo.rpc.ProviderFilter
```
