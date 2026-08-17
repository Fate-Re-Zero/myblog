---
title: 分布式session原理解析
date: 2020-11-21 19:41:58
tags:
---

### 无状态的HTTP协议中保存用户登陆状态的方式,session和cookie 
cookie:cookie将用户登陆信息以文本格式存储在用户浏览器上 
session:将用户登陆信息保存到后端应用上下文,通过将sessionId设置到cookie中 
对比： 
（1）Cookie以文本文件格式存储在浏览器中，而session存储在服务端它存储了限制数据 量。它只允许4kb它没有在cookie中保存多个变量；
（2）cookie的存储限制了数据量，只允许4KB，而session是无限量的；
（3）我们可以轻松访问cookie值但是我们无法轻松访问session值，因此它更安全；
（4）设置cookie时间可以使cookie过期。但是使用session-destory()，我们将会销毁会话；

### 传统session/cookie的基本工作流程：
![](/images/传统sessioncookie的基本工作流程.jpg)

### session在分布式应用存在的缺陷： 
因为session存储在应用上下文,当分布式应用时各个应用节点的session不能共享,导致判断用户登陆状态失败
![](/images/session在分布式应用存在的缺陷.jpg)

### 解决方案：
session同步:各个应用服务节点间通过实时数据同步来更新session信息，来达 到session在各个服务节点间进行数据传递

![](/images/session同步.jpg)

session共享:将session存储到公共的存储介质(一般为redis中),以达到分布式集 群中各个节点都可以访问和更新session，来达到session在各个服务节点间进行 数据传递

![](/images/session共享.jpg)

jwt(json word token):在分布式集群中各个服务节点通过共同的加密和签名算法 对session进行加密解密,来达到session在各个服务节点间进行数据传递 https://www.cnblogs.com/yan7/p/7857833.html

![](/images/jwt.jpg)

### jwt的优点： 
1. 可扩展性好 jwt不需要任何附加操作就可以做到应用程序分布式部署;
2. 无状态 jwt不在服务端存储任何状态。RESTful API的原则之一是无状态,发出请求时,总会返回带 有参数的响应，不会产生附加影响。jwt的载荷中可以存储一些常用信息，用于交换信息， 有效地使用 JWT，可以降低服务器查询数据库的次数。 

### jwt的缺点： 
1. 安全性 由于jwt的payload是使用base64编码的，并没有加密，因此jwt中不能存储敏感数据。而 session的信息是存在服务端的，相对来说更安全;
2. 性能 jwt太长。由于是无状态使用JWT，所有的数据都被放到JWT里，如果还要进行一些数据交 换，那载荷会更大，经过编码之后导致jwt非常长，cookie的限制大小一般是4k，cookie很 可能放不下，所以jwt一般放在local storage里面。并且用户在系统中的每一次http请求都 会把jwt携带在Header里面，http请求的Header可能比Body还要大。而sessionId只是很 短的一个字符串，因此使用jwt的http请求比使用session的开销大得多;
3. 一次性 无状态是jwt的特点，但也导致了这个问题，jwt是一次性的。想修改里面的内容，就必须签 发一个新的jwt，一旦签发一个jwt，在到期之前就会始终有效，无法中途废弃。

![](/images/二者结合.jpg)
