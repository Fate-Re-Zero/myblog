---
title: Spring AOP原理及源码学习
date: 2020-06-08 18:50:12
tags: AOP
---

## AOP底层原理之一（动态代理Demo）：
Demo所解决的问题场景：有一个计算器，需要在其内部的所有计算方法中打印日志，乍一看这个需求可以简单粗暴的来实现，在每个计算方法中加上相应的日志就完成了，但是如方法非常多我们需要加日志的地方就非常多，这样工作量就会很大，下面是使用动态代理来实现这一过程。

### 计算器接口及计算器实现类
```java
/**
 * @author xiangxiang
 * @create 2020-03-07 22:13
 */
public interface Calculator {

    int add(int a, int b);

    int div(int a, int b);
}

/**
 * @author xiangxiang
 * @create 2020-03-08 19:17
 */
public class MyCalculator implements Calculator{
    @Override
    public int add(int a, int b) {
        return a + b;
    }

    @Override
    public int div(int a, int b) {
        return a / b;
    }
}
```

### 代理工具类
```java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

/**
 * @author xiangxiang
 * @create 2020-03-07 22:15
 */
public class ProxyUtil {
    public static Calculator getProxy(Calculator calculat) {
        InvocationHandler invocationHandler = new InvocationHandler() {
            @Override
            public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                Object result = null;
                try {
                    LogUtil.preLog(method, args);
                    result = method.invoke(calculat, args);
                    LogUtil.afterLog(method, args);
                } catch (Exception e) {
                    LogUtil.ExceptionLog(method, args);
                }
                return result;
            }
        };
        ClassLoader classLoader = calculat.getClass().getClassLoader();
        Class<?>[] interfaces = calculat.getClass().getInterfaces();
        Object proxy = Proxy.newProxyInstance(classLoader, interfaces, invocationHandler);
        return (Calculator) proxy;
    }
}
```
### 日志工具类
```java
/**
 * @author xiangxiang
 * @create 2020-03-07 22:21
 */
public class LogUtil {

    public static void preLog(Method method, Object[] args) {
        System.out.println(method.getName() + "执行前" + "参数为" + Arrays.toString(args));
    }

    public static void afterLog(Method method, Object[] args) {
        System.out.println(method.getName() + "执行后" + "参数为" + Arrays.toString(args));
    }

    public static void ExceptionLog(Method method, Object[] args) {
        System.out.println(method.getName() + "执行异常了" + "参数为" + Arrays.toString(args));
    }
}
```

## AOP专业术语：

## 如何将切面类中的这些方法（通知方法）动态的在目标方法运行的各个位置切入
1.将目标类和切面类（封装了通知方法（在目标方法执行前后执行的方法））加入到IOC容器；
2.还应该告诉Spring哪个类是切面类@Aspect;
3.告诉Spring每个方法都什么时候执行；
@Before 在目标方法之前执行
@After 在目标方法结束之后执行
@AfterReturning 在目标方法正常返回之后执行
@AfterThrowing 在目标方法抛出异常之后执行
切入点表达式：execution(访问权限 返回值类型 方法全限定类名)

IoC中保存的是的组件是它的代理对象，代理对象与目标对象的唯一关联关系是实现了同一个接口；
cglib为什么没有接口的组件也可以创键代理对象
cglib在目标类中创键了一个内部类，帮我们创键好了代理对象
细节二：切入点表达是通配符
细节三：通知方法的执行顺序
细节四：

多切面

AOP的使用场景：
1.AOP加日志
2.AOP权限验证
3.AOP做安全检查
4.AOP做事务控制





