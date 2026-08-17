---
title: Spring Cloud初步学习
date: 2021-04-11 14:28:50
tags:
---

Spring Cloud: 分布式微服务架构的一站式解决方案，是多种微服务架构落地技术的集合体，俗称微服务全家桶。

Spring Cloud 对应 Spring Boot详细版本查看：https://start.spring.io/actuator/info

Spring Boot 与 Spring Cloud 对应版本的确定：
![](/images/Spring Boot 与Spring Cloud技术选择.jpg)

![](/images/版本对应.jpg)

服务注册中心：Eureka, Zookeeper, Consul, Nacos

服务调用：Ribbon, LoadBalancer

服务调用2：Feign, OpenFeign

服务降级：Hystrix, resilience4j, sentienl

服务网关：Zuul, Zuul2, gateway

服务配置:Config, Nacos, 携程阿波罗

服务总线：Bus, Nacos


创建工程：
约定 > 配置 > 编码

首先处理好项目环境： File Encoding
![](/images/项目编码设置.jpg)

项目注解生效激活： Annotation Processor
![](/images/项目注解生效激活.jpg)

Java编译版本选择：Java Compiler
![](/images/Java编译版本选择.jpg)

文件类型过滤：File Types
![](/images/文件类型过滤.jpg)

POM文件相关：
dependencyManagement：锁定版本，子模块不用重写版本号，需要其他版本只需要子模块单独定义即可，好处：全工程的jar包统一，并不实现引入，只是全局声明引入的版本号

Maven中跳过单元测试：
![](/images/Maven中跳过单元测试.jpg)

微服务模块

1.建Module
2.改POM
3.写YML
4.主启动
5.业务类

什么是服务治理：
Spring Cloud 封装了Netflix公司开发的Eureka模块来实现服务治理

在传统的rpc远程调用框架中，管理每个服务与服务之间依赖关系比较复杂

服务注册：

服务发现：

eureka自我保护机制：

Spring Cloud Ribbon是基于Netflix Ribbon实现的一套客户端负载均衡的工具。

简单地说，Ribbon是Netflix发布的开源项目，主要功能是提供客户端的负载均衡算法和服务调用。Ribbon客户端提供一系列完善的配置项如连接超时，重试等。简单的说，就是在配置文件中列出Load Balance(简称LB)后面所有的机器，Ribbon会自动的帮助你基于某种规则(如简单轮询，随机连接等)去连接这些机器。我们很容易使用Ribbon实现自定义的负载均衡算法。

官网资料：https://github.com/Netflix/ribbon/wiki/Getting-Started

源码：https://github.com/Netflix/ribbon

LB负载均衡(Load Balance)是什么
简单的说就是将用户的请求平摊的分配到多个服务上，从而达到系统的HA(高可用)。
常见的负载均衡有软件Nginx，LVS，硬件F5等。

Ribbon本地负载均衡客户端 VS Nginx服务端负载均衡区别
Nginx是服务器负载均衡，客户端所有请求都会交给nginx,然后由nginx实现转发请求，及负载均衡是由服务器端实现的

Ribbon本地负载均衡，在调用微服务接口的时候，会在注册中心上获取注册信息服务列表之后缓存到JVM本地，从而在本地实现RPC远程服务调用技术。

集中式LB

即在服务的消费方和提供方之间使用独立的LB设施(可以是硬件，如F5,也可以是软件，如nginx),由改设市负责把访问请求通过某种策略转发至服务提供方

进程内LB

将LB逻辑集成到消费方，消费方从服务注册中心获取有哪些地址可用，然后自己再从这些地址中选择出一个合适的服务器。

Ribbon就属于进程内的LB,它就是一个类库，集成于消费发进程，消费方通过它来获取到服务提供方地址。

一句话：负载均衡 + RestTemplate调用

架构说明：Ribbon其实就是一个软负载均衡客户端组件，它可以和其他所需请求的客户端结合使用，和eureka结合只是其中的一个实例。

Feign:是一个声明式的web服务客户端，让编写Web服务客户端变得非常容易，

OpenFeign:



