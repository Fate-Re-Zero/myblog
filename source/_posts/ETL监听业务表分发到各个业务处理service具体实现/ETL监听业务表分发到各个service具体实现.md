---
title: ETL监听业务表分发到各个service具体实现
date: 2021-03-20 12:15:50
tags:
---

### 开发背景： 
大数据部门需要其他各个业务部门业务表的数据，并且需要做到与其他业务部门业务表达到数据一致，也就会有与其他业务表达到数据同步这么一个过程，本组件的开发这是用来实现与各个业务部门表数据做到数据同步

### 实现原理：
Mysql Binlog日志文件:(每次对mysql进行一次写请求，都会写一次二进制日志，记录Mysql具体执行了什么操作，mysql主从复制就是基于binlog日志的)
本组件通过解析Binlog文件得到mysql对那张表具体执行了什么操作，然后将数据封装到MessageQueueDTO中，然后推消息到对应的kafak消息队列，对应的kafak监听器监听到消息，根据表名将Mysql执行的具体操作分发到对应的service进行相应的处理

### 业务service标记表名枚举：MonitorTableName
```java
import org.springframework.stereotype.Indexed;
import java.lang.annotation.*;

@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Indexed
public @interface MonitorTableName {
    /**
     * 监控的表名称
     *
     * @return 表名
     */
    String value() default "";
}
```

### 各服务操作基础接口：IMonitorOperateService
实现了该接口的service或者继承了实现该接口的类都会被后置处理器放入到ConcurrentHashMap中，key为对应的service，值为service对应的class

```java
import com.kafakdemo.demo.dto.MessageQueueDTO;

public interface IMonitorOperateService {
    /**
     * 新增数据
     *
     * @param messageQueueDTO 消息数据实体
     */
    void create(MessageQueueDTO messageQueueDTO);

    /**
     * 修改数据
     *
     * @param messageQueueDTO 消息数据实体
     */
    void update(MessageQueueDTO messageQueueDTO);

    /**
     * 删除数据
     *
     * @param messageQueueDTO 消息数据实体
     */
    void delete(MessageQueueDTO messageQueueDTO);

}
```

### ETL监听后置处理器:

```java
import org.springframework.aop.support.AopUtils;
import org.springframework.beans.factory.config.BeanPostProcessor;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public abstract class AbstractEtlListenerBeanPostProcessor implements BeanPostProcessor {

    /**
     * 保存监听操作服务集合
     */
    private final Map<IMonitorOperateService, Class<?>> lstMonitorOperateServices = new ConcurrentHashMap<>();

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        //是否是监听表接口
        if (bean instanceof IMonitorOperateService) {
            synchronized (this.lstMonitorOperateServices) {
                if (this.lstMonitorOperateServices.containsKey(bean)) {
                    return bean;
                }
                this.lstMonitorOperateServices.put((IMonitorOperateService) bean, AopUtils.getTargetClass(bean));
            }
        }
        return bean;
    }

    /**
     * 获取所有的监听操作类
     *
     * @return {@link Map}
     */
    protected Map<IMonitorOperateService, Class<?>> getLstMonitorOperateServices() {
        return lstMonitorOperateServices;
    }
}
```

### 对IMonitorOperateService的基础实现类：
IMonitorOperateService接口的一个简单实现，各个service只需要继承该类就可以被加载到ConcurrentHashMap中，这样写的好处是，不需要在各个service中进行打印日志，减轻了些许代码量，并且提供了返回MessageQueueDTO中实体集合的父类方法

```java
import com.fasterxml.jackson.core.type.TypeReference;
import com.kafakdemo.demo.dto.MessageQueueDTO;
import com.kafakdemo.demo.util.BaseUtils;
import lombok.extern.slf4j.Slf4j;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

@Slf4j
public abstract class AbstractMonitorOperateService implements IMonitorOperateService {

    /**
     * 新增数据
     *
     * @param messageQueueDTO 消息数据实体
     */
    @Override
    public void create(MessageQueueDTO messageQueueDTO) {
        log.debug("---过滤新增数据表名：{}", messageQueueDTO.getTable());
    }

    /**
     * 删除数据
     *
     * @param messageQueueDTO 消息数据实体
     */
    @Override
    public void delete(MessageQueueDTO messageQueueDTO) {
        log.debug("---过滤删除数据表名：{}", messageQueueDTO.getTable());
    }

    /**
     * 更新数据
     *
     * @param messageQueueDTO 消息数据实体
     */
    @Override
    public void update(MessageQueueDTO messageQueueDTO) {
        log.debug("---过滤更新数据表名：{}", messageQueueDTO.getTable());
    }

    /**
     * 获取实体集合
     *
     * @param messageQueueDTO 消息实体
     * @param typeReference   实体类型
     * @param <T>             泛型约束
     * @return 实体集合
     */
    protected <T> List<T> parseArray(MessageQueueDTO messageQueueDTO, TypeReference<List<T>> typeReference) {
        if (Objects.isNull(messageQueueDTO)) {
            return new ArrayList<>(0);
        }
        return BaseUtils.parseArray(messageQueueDTO.getData(), typeReference);
    }

    /**
     * 获取实体集合
     *
     * @param messageQueueDTO 消息实体
     * @param typeReference   实体类型
     * @param <T>             泛型约束
     * @return 实体集合
     */
    protected <T> List<T> parseOldArray(MessageQueueDTO messageQueueDTO, TypeReference<List<T>> typeReference) {
        if (Objects.isNull(messageQueueDTO)) {
            return new ArrayList<>(0);
        }
        return BaseUtils.parseArray(messageQueueDTO.getOld(), typeReference);

    }
}
```

### 具体操作处理工厂：

```java
import com.kafakdemo.demo.dto.MessageQueueDTO;
import com.kafakdemo.demo.enums.DataBaseOperateTypeEnum;
import org.springframework.stereotype.Component;
import java.util.List;

@Component
public class DefaultOperateFactory {

    /**
     * 处理监控操作
     *
     * @param messageQueueDTO binlog日志消息
     * @param lstTargets      操作服务集合
     */
    public void doExecute(MessageQueueDTO messageQueueDTO, List<IMonitorOperateService> lstTargets) {
        boolean flag = messageQueueDTO.isFromException();
        String className = messageQueueDTO.getClassName();
        String type = messageQueueDTO.getType().toUpperCase();
        for (IMonitorOperateService monitorOperateService : lstTargets) {
            messageQueueDTO.setFromException(flag);
            messageQueueDTO.setClassName(className);
            if (DataBaseOperateTypeEnum.INSERT.getType().equals(type)) {
                monitorOperateService.create(messageQueueDTO);
            } else if (DataBaseOperateTypeEnum.UPDATE.getType().equals(type)) {
                monitorOperateService.update(messageQueueDTO);
            } else if (DataBaseOperateTypeEnum.DELETE.getType().equals(type)) {
                monitorOperateService.delete(messageQueueDTO);
            }
        }
    }
}
```

### 监听调用策略类:
继承了AbstractEtlListenerBeanPostProcessor类，调用了父类的getLstMonitorOperateServicesByTableName(String tableName)方法，得到了所有实现了IMonitorOperateService或者继承AbstractMonitorOperateService的service，拿到service上标注的MonitorTableName注解的value值，根据表名拿到对应的service

```java
import com.google.common.collect.Lists;
import com.kafakdemo.demo.annotation.MonitorTableName;
import org.apache.commons.collections.MapUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Component;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * 监听调用策略类
 */
@Component
public class EtlListenerServiceStrategy extends AbstractEtlListenerBeanPostProcessor {

    /**
     * 根据监控的表名称获取所有的监听操作服务
     *
     * @param tableName 监听表名称
     * @return 监听操作服务集合
     */
    public List<IMonitorOperateService> getLstMonitorOperateServicesByTableName(String tableName) {
        List<IMonitorOperateService> lstTargets = Lists.newArrayList();
        if (StringUtils.isEmpty(tableName)) {
            return lstTargets;
        }
        Map<IMonitorOperateService, Class<?>> lstMonitorOperateServices = getLstMonitorOperateServices();
        if (MapUtils.isNotEmpty(lstMonitorOperateServices)) {

            Iterator<Map.Entry<IMonitorOperateService, Class<?>>> monitorOperateServiceIterators = lstMonitorOperateServices.entrySet().iterator();
            while (monitorOperateServiceIterators.hasNext()) {
                Map.Entry<IMonitorOperateService, Class<?>> monitorOperateServiceEntry = monitorOperateServiceIterators.next();
                MonitorTableName monitorTableName =
                        monitorOperateServiceEntry.getValue().getAnnotation(MonitorTableName.class);
                if (Objects.nonNull(monitorTableName) && tableName.equals(monitorTableName.value())) {
                    lstTargets.add(monitorOperateServiceEntry.getKey());
                }
            }
        }
        return lstTargets;
    }
}
```

### 监控操作分发器:
根据表名拿到具体的service，然后执行具体的操作

```java
import com.kafakdemo.demo.dto.MessageQueueDTO;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections.CollectionUtils;
import org.springframework.stereotype.Component;
import javax.annotation.Resource;
import java.util.List;

@Component
@Slf4j
public class MonitorOperateDispatcher {

    @Resource
    EtlListenerServiceStrategy etlListenerServiceStrategy;
    @Resource
    DefaultOperateFactory defaultOperateFactory;

    /**
     * 接到消息处理分发操作
     *
     * @param messageQueueDTO binlog反序列化实体
     */
    public void execute(MessageQueueDTO messageQueueDTO) {
        //根据表名称获取对应监控操作服务集合
        List<IMonitorOperateService> lstMonitorOperateServices = etlListenerServiceStrategy.getLstMonitorOperateServicesByTableName(messageQueueDTO.getTable());
        if (CollectionUtils.isEmpty(lstMonitorOperateServices)) {
            log.warn("没有配置当前数据表，是否需要配置请业务方确认，表名：{}", messageQueueDTO.getTable());
            return;
        }
        //开始处理操作
        defaultOperateFactory.doExecute(messageQueueDTO, lstMonitorOperateServices);
    }
}
```
