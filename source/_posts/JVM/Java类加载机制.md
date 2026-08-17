---
title: Java类加载机制
date: 2022-07-31 16:00:38
tags: JVM
---

### JVM相关的理论
1. JVM跨语言的平台，不管任何语言，只要能编译程class文件，都可以在JVM上执行;
2. JVM是一种规范

### JVM,JRE,JDK
1. JVM：java虚拟机
2. JRE：java运行时环境 = JVM + Java核心类库
3. JDK：JRE + 编译器等开发工具

### 类加载过程
1. 加载（Loading）：将class文件加载进内存；
2. 链接(Linking)[验证(Verification) --> 准备(Preparation) --> 解析(Resolution)] 
	1.验证(Verification)：校验加载进来的class文件是否符合class文件的标准；(校验文件是否符合JVM规定)
	2.准备(Preparation)：为class文件的静态成员变量赋默认值；
	3.解析(Resolution)：将class文件的符号引用转换成直接引用；将类，方法，属性等符号引用解析为直接引用，常量池中的各种符号引用解析为指针、偏移量等内存地址的直接引用；
3. 初始化（Initialization）：给静态成员变量赋初始值，这一步才执行静态代码块；调用类初始化代码<clinit>,给静态成员变量
	赋初始值

### 类加载过程中赋初始值和new对象的赋初始值
1. load - 默认值 - 初始值
2. new - 申请内存 - 默认值 - 初始值

### 单例模式
- 双重检查锁，在前一个线程获取到锁进行对象初始化的时候，对象初始化的正确顺序（1：分配对象的内存空间；2：初始化对象；3：设置instance指向刚分配的内存地址）, 此时发生了指令重排序，先将对象引用指向了内存地址，还没有初始化象但是此时对象还没有赋值，对象引用已经指向了对象的内存地址，这时候其他线程检查对象是否为null的时候，发现对象不为null,此时其他线程使用的是这个半初始化状态的对象从而引发一些问题；解决方案：单例对象加上volatile
```java
public class ClassLoadingProcedure {
    public static void main(String[] args) {
        System.out.println(T.count);
    }
}

class T {
    public static T t = new T(); // null
    public static int count = 2; //0

    //private int m = 8;

    private T() {
        count ++;
        //System.out.println("--" + count);
    }
}
```

### JVM的懒加载
- 理解：Jvm采用的是懒加载的方式进行类加载的，也就是按需加载，只有这个类被用到时候才会去加载；

### 类加载器的分类：
1. 启动类加载器(引导类加载器，Bootstrap ClassLoader)：加载一些java核心类的jar包及扩展类加载器和系统类加载器
2. 扩展类加载器(Extension ClassLoader)：主要用于加载(D:\jdk1.8\jre\lib\ext，C:\WINDOWS\Sun\Java\lib\ext)下的jar包
3. 系统类加载器(应用程序类加载器，Application ClassLoader)：父类加载器为扩展类加载器，它负责加载环境变量classpath或系统属性java.class.path指定路径下的类库，可以通过ClassLoader.getSystemClassLoader()来获取该类的加载器
4. 用户自定义加载器(User ClassLoader)：java开发者可以自定义类加载器来实现类库的动态加载，加载源可以是本地的jar包，也可以是网络上的远程资源
	注意：Application ClassLoader和Extension ClassLoader类加载器的加载器是Bootstrap ClassLoader;

### 双亲委派机制
1.双亲委派机制里的父加载器：这里父加载器并不是指父类加载器，Application ClassLoader和Extension ClassLoader都继承自URLClassLoader,之所以称之为父加载器，是因为双亲委派机制的逻辑类似于字类将任务委托给父类查找是否加载了某个类，所以称之为父加载器;

### 为什么要使用双亲委派机制
1. 保护程序安全，防止核心API被随意篡改(例如在src下创建java.lang包，编写自己的String类)；
2. 避免了类的重复加载，确保一个类是全局唯一性的，通过这种层级关系避免了类的重复加载；
	补充：在一个类加载器的命名空间中，同一个类型的类只会有一个；
	注意：同一个类型由不同的类加载器加载，执行类型转换时会发生异常；
	双亲委派机制的弊端：底层ClassLoader可以通过parent属性来获取父类的所加载的类，但是顶层ClassLoader无法访问底层ClassLoader所加载的类

### 打破双亲委派机制
1. JDK1.2之前，自定义ClassLoader是需要重写LoadClass方法的；
2. 可以设置线程上下文类加载器，Thread.currentThread().setContextClassLoader(this.loader);
3. 热部署：自定义classLoader重写loadClass方法，当触发热部署条件时，直接重写构建一个新的classLoader进行类加载，这样就可以保证加载的内容都是最新的;同一个tomcat的web容器中两个应用可以加载不同版本jar包：每个模块都有自己的classLoader;

### Launcher
- 理解：Launcher为类加载器的启动类，常见的类加载器为其内部类，内部定义了类加载器的加载范围；
1. Bootstrap ClassLoader： String bootClassPath = System.getProperty("sun.boot.class.path");
2. ExtClassLoader：String var0 = System.getProperty("java.ext.dirs");
3. AppClassLoader：String var1 = System.getProperty("java.class.path");

### Java是解释执行的语言还是编译执行的语言
1. 解释器：bytecode intepreter
2. JIT：Just In-Time compiler
3. 混合模式：
	1.混合使用解释器 + 热点代码编译
	2.起始阶段采用解释执行
	3.热点代码检测 ： -XX:CompileThreshold = 10000
	-多次被调用的方法（方法计数器：监测方法执行频率）
	-多次被调用的循环（循环计数器：检测循环执行频率）
	-进行编译
	-Xmixed 默认为混合模式
	开始解释执行，启动速度较快，对热点代码实行检测和编译
	-Xint 使用解释模式，启动很快，执行稍慢
	-Xcomp 使用纯编译模式，执行很快，启动很慢


