---
title: Spring常见的面试题
date: 2022-09-15 09:34:38
tags: spring
---

### spring是什么

### spring的优缺点

优点

方便解耦，简化开发 ：Spring就是一个大工厂，可以将所有对象的创建和依赖关系的维护，交给Spring管理。

AOP编程的支持 ：Spring提供面向切面编程，可以方便的实现对程序进行权限拦截、运行监控等功能。

声明式事务的支持 ：只需要通过配置就可以完成对事务的管理，而无需手动编程。

方便程序的测试 ：Spring对Junit4支持，可以通过注解方便的测试Spring程序。

方便集成各种优秀框架 ：Spring不排斥各种优秀的开源框架，其内部提供了对各种优秀框架的直接支持（如：Struts、Hibernate、MyBatis等）。

降低JavaEE API的使用难度 ：Spring对JavaEE开发中非常难用的一些API（JDBC、JavaMail、远程调用等），都提供了封装，使这些API应用难度大大降低。

缺点

Spring依赖反射，反射影响性能

使用门槛升高，入门Spring需要较长时间 

### 控制反转

### 依赖注入

### spring的特点

轻量级： 组件大小与开销两方面而言Spring都是轻量的。完整的Spring框架可以在一个大小只有1M多的JAR文件中发布，并且Spring所需的处理开销也是微不足道的。此外，Spring是非侵入式，典型案例，Spring应用中的对象不依赖于Spring特定的类

控制反转： Spring通过控制反转（IOC）技术实现解耦。一个对象依赖的其他对象会通过被动的方式传递进来，而不需要对象自己创建或者查找依赖。

面向切面： 支持切面（AOP）编程，并且吧应用业务逻辑和系统服务区分开。

容器： Spring包含并管理应用对象的配置和生命周期，在这个意义上它是一种容器。可以配置每个bean如何被创建、销毁，bean的作用范围是单例还是每次都生成一个新的实例，以及他们是如何相互关联。

框架集合： 将简单的组件配置，组合成为复杂的框架；

应用对象被申明式组合；

提供许多基础功能（事务管理、持久化框架继承），提供应用逻辑开发接口

### BeanFactory 和 applicationContext有什么区别 

applicationContext 由 BeanFactory 派生而来，提供了更多面向实际应用的功能。

applicationContext 继承了 HierarchicalBeanFactory 和 ListableBeanFactory 接口，在此基础

上，还通过多个其他的接口扩展了 BeanFactory 的功能 

ClassPathXmlApplicationContext

FileSystemXmlApplicationContext

AnnotationConfigApplicationContext

AnnotationConfigWebApplicationContext
### Spring常见的扩展点