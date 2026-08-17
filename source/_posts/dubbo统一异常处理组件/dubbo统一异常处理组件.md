---
title: dubbo统一异常处理组件
date: 2021-03-02 18:57:33
tags:
---

### dubbo统一异常处理原理：
 dubbo作为rpc服务，会存在服务提供方抛出的异常的类型信息在传输到服务使用方时存在 类型丢失。类型丢失的原因如下: 1.基于java的多态性，所以rpc接口的生产者在接口服务实现时抛出的异常时接口api定义的 异常的子类，但该异常不在api的jar包中导致有可能在使用方的上下文中没有加载该异常 类。2.非捕获异常RuntimeException因为不需要在代码中显示捕获异常并处理，所以这类异常 可以不在方法签名中定义，所以服务生产者抛出的RuntimeException有可能在使用方的上 下文中没有加载该异常类。 如果服务提供方包装的异常类传递到服务使用方，但是因为上下文中没有加载该异常类，就 会导致解析rpc响应结果失败，所以dubbo在框架上通过ExceptionFilter来对rpc调用过程 中的异常进行统一处理。 

### dubbo统一异常处理默认扩展点实现类: 
com.alibaba.dubbo.rpc.filter.ExceptionFilter该扩展点为provider的扩展点，ExceptionFilter对异常的处理逻辑如下： 1.判断rpc结果中是否有异常，如果没有异常，则直接返回 2.如果抛出的异常是可捕获异常，则直接返回 3.如果所抛出异常在api的方法签名上有，则直接将结果返回 4.如果抛出异常类定义的jar包和rpc接口服务类定义的jar包文件是同一个，则直接将结果返 回5.如果异常为RpcException则直接将结果返回 6.如果为其他情况(RuntimeException子类并且没有在api对应的jar包中未定义)，这时服务 生产者就不能推断出服务消费者已经加载了这个异常类，则创建一个RuntimeException异 常并将原异常的堆栈信息设置成新异常的message作为最后响应结果的异常。

```java
package com.alibaba.dubbo.rpc.filter;

import com.alibaba.dubbo.common.extension.Activate;
import com.alibaba.dubbo.common.logger.Logger;
import com.alibaba.dubbo.common.logger.LoggerFactory;
import com.alibaba.dubbo.common.utils.ReflectUtils;
import com.alibaba.dubbo.common.utils.StringUtils;
import com.alibaba.dubbo.rpc.Filter;
import com.alibaba.dubbo.rpc.Invocation;
import com.alibaba.dubbo.rpc.Invoker;
import com.alibaba.dubbo.rpc.Result;
import com.alibaba.dubbo.rpc.RpcContext;
import com.alibaba.dubbo.rpc.RpcException;
import com.alibaba.dubbo.rpc.RpcResult;
import com.alibaba.dubbo.rpc.service.GenericService;
import java.lang.reflect.Method;

@Activate(
    group = {"provider"}
)
public class ExceptionFilter implements Filter {
    private final Logger logger;

    public ExceptionFilter() {
        this(LoggerFactory.getLogger(ExceptionFilter.class));
    }

    public ExceptionFilter(Logger logger) {
        this.logger = logger;
    }

    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        try {
            Result result = invoker.invoke(invocation);
            if (result.hasException() && GenericService.class != invoker.getInterface()) {
                try {
                    Throwable exception = result.getException();
                    if (!(exception instanceof RuntimeException) && exception instanceof Exception) {
                        return result;
                    } else {
                        try {
                            Method method = invoker.getInterface().getMethod(invocation.getMethodName(), invocation.getParameterTypes());
                            Class<?>[] exceptionClassses = method.getExceptionTypes();
                            Class[] arr$ = exceptionClassses;
                            int len$ = exceptionClassses.length;

                            for(int i$ = 0; i$ < len$; ++i$) {
                                Class<?> exceptionClass = arr$[i$];
                                if (exception.getClass().equals(exceptionClass)) {
                                    return result;
                                }
                            }
                        } catch (NoSuchMethodException var11) {
                            return result;
                        }

                        this.logger.error("Got unchecked and undeclared exception which called by " + RpcContext.getContext().getRemoteHost() + ". service: " + invoker.getInterface().getName() + ", method: " + invocation.getMethodName() + ", exception: " + exception.getClass().getName() + ": " + exception.getMessage(), exception);
                        String serviceFile = ReflectUtils.getCodeBase(invoker.getInterface());
                        String exceptionFile = ReflectUtils.getCodeBase(exception.getClass());
                        if (serviceFile != null && exceptionFile != null && !serviceFile.equals(exceptionFile)) {
                            String className = exception.getClass().getName();
                            if (!className.startsWith("java.") && !className.startsWith("javax.")) {
                                return (Result)(exception instanceof RpcException ? result : new RpcResult(new RuntimeException(StringUtils.toString(exception))));
                            } else {
                                return result;
                            }
                        } else {
                            return result;
                        }
                    }
                } catch (Throwable var12) {
                    this.logger.warn("Fail to ExceptionFilter when called by " + RpcContext.getContext().getRemoteHost() + ". service: " + invoker.getInterface().getName() + ", method: " + invocation.getMethodName() + ", exception: " + var12.getClass().getName() + ": " + var12.getMessage(), var12);
                    return result;
                }
            } else {
                return result;
            }
        } catch (RuntimeException var13) {
            this.logger.error("Got unchecked and undeclared exception which called by " + RpcContext.getContext().getRemoteHost() + ". service: " + invoker.getInterface().getName() + ", method: " + invocation.getMethodName() + ", exception: " + var13.getClass().getName() + ": " + var13.getMessage(), var13);
            throw var13;
        }
    }
}
```

### 自定义dubbo统一异常处理组件原理： 
如果直接通过dubbo默认的统一异常处理策略，则在我们的服务生产者中抛出的 BuzzErrorException都会包装成RuntimeException并且异常消息变成了异常堆栈信息，就 不能通过controller的统一异常处理来生成正确的前端异常响应结果。 本组件通过添加自定义的默认Filter扩展点来对服务生产者抛出的BuzzErrorException统一 处理。 

### dubbo的FIlter执行顺序的逻辑：
![](/images/dubbo的FIlter执行顺序的逻辑.jpg)

根据dubbo的FIlter执行顺序的逻辑，因为请求的异常处理，是在一个Filter的后置处理中执 行的。所以如果自定义的异常处理Filter需要在dubbo默认的异常处理ExceptionFilter之前 进行执行，则需要将自定义的异常处理Filter的执行顺序编号要比ExceptionFilter，所以可 以将自定义异常处理的Filter的执行顺序编号定义为最大值. 

### 自定义dubbo统一异常处理组件扩展原理图：
![](/images/自定义dubbo统一异常处理组件扩展原理图.jpg)

### 服务端统一异常处理拦截器： BuzzProviderExceptionFilter 
现有的实现逻辑中跟大部分逻辑在dubbo的默认异常处理中的逻辑异常相同，后续可以优 化掉，只保留对BuzzErrorException的异常处理逻辑

```java
import com.alibaba.dubbo.common.Constants;
import com.alibaba.dubbo.common.extension.Activate;
import com.alibaba.dubbo.common.utils.StringUtils;
import com.alibaba.dubbo.rpc.*;
import com.banksteel.openerp.commons.exception.BuzzErrorException;
import java.lang.reflect.Method;
import java.util.Objects;

@Activate(group = Constants.PROVIDER,order =Integer.MAX_VALUE)
public class BuzzProviderExceptionFilter implements Filter {
    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        return buildErrorResult(invoker,invocation,invoker.invoke(invocation));
    }

    private Result buildErrorResult(Invoker<?> invoker,Invocation invocation,Result result){
        if (result.hasException()){
            if (noBuildException(invoker,invocation,result.getException())){
                return result;
            }
            Throwable error = buildErrorException(result.getException());
            if (result instanceof RpcResult){
                ((RpcResult) result).setException(error);
            }else {
                return new RpcResult(error);
            }
        }
        return result;
    }

    private Throwable buildErrorException(Throwable exception){
        if (StringUtils.isBlank(exception.getMessage())){
            if (Objects.nonNull(exception.getCause())){
                return buildErrorException(exception.getCause());
            }else {
                return exception;
            }
        }else {
            Exception causeError = new Exception(StringUtils.toString(exception));
            if (exception instanceof BuzzErrorException){
                RpcException error = new RpcException(exception.getMessage(),causeError);
                error.setCode(RpcException.BIZ_EXCEPTION);
                return error;
            }else {
                return exception;
            }
        }
    }

    private boolean noBuildException(Invoker<?> invoker, Invocation invocation, Throwable exception){
        // 如果是checked异常，直接抛出
        if (! (exception instanceof RuntimeException) && (exception instanceof Exception)) {
            return true;
        }

        // 在方法签名上有声明，直接抛出
        try {
            Method method = invoker.getInterface().getMethod(invocation.getMethodName(), invocation.getParameterTypes());
            Class<?>[] exceptionClassses = method.getExceptionTypes();
            for (Class<?> exceptionClass : exceptionClassses) {
                if (exception.getClass().equals(exceptionClass)) {
                    return true;
                }
            }
        } catch (NoSuchMethodException e) {
            return false;
        }
        return false;
    }
}
```

### 消费端统一异常处理拦截器： BuzzConsumerExceptionFilter

```java
import com.alibaba.dubbo.common.Constants;
import com.alibaba.dubbo.common.extension.Activate;
import com.alibaba.dubbo.rpc.*;
import com.banksteel.openerp.commons.exception.BuzzErrorException;
import java.util.Objects;

@Activate(group = Constants.CONSUMER,order =Integer.MAX_VALUE)
public class BuzzConsumerExceptionFilter implements Filter {
    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        return buildErrorResult(invoker.invoke(invocation));
    }

    private Result buildErrorResult(Result result){
        if (result.hasException()){
            Throwable error = buildErrorException(result.getException());
            if (result instanceof RpcResult){
                ((RpcResult) result).setException(error);
            }else {
                return new RpcResult(error);
            }
        }
        return result;
    }

    private Throwable buildErrorException(Throwable exception){
        if (exception instanceof RpcException){
            RpcException rpcException = (RpcException) exception;
            if (Objects.equals(rpcException.getCode(),RpcException.BIZ_EXCEPTION)){
                BuzzErrorException errorException = new BuzzErrorException(rpcException.getMessage(),exception);
                return errorException;
            }
        }
        return exception;
    }
}
```

### 设置默认装载自定义过滤器：
在commans工程resource下的META-INF目录下创建dubbo 目录，并创建文件com.alibaba.dubbo.rpc.Filter，指定自定义的异常处理Filter类为默认扩展点:
buzzProviderExceptionFilter=com.commons.rpc.BuzzProviderExceptionFilter
BuzzConsumerExceptionFilter=com.commons.rpc.BuzzConsumerExceptionFilter

