---
title: JVM性能监控与调优
date: 2022-06-1 21:15:38
tags:
---

一.为什么调优：
	(1).防止OOM的出现
	(2).解决OOM
	(3).减少Full GC出现的频率

二.性能优化的步骤：
	(1).性能监控：
	(2).性能分析：
	(3).性能调优：

三.性能测试指标及相互关系：
	(1).停顿时间（或响应时间）
	(2).吞吐量：运行用户代码的时间占总运行时间的比例（总运行时间：程序的运行时间 + 内存回收时间）
	(3).并发数：同一时刻，对服务器有实际交互的请求数
	(4).内存占用：java堆区所占的内存大小

四.jps：查看java正在运行的进程
	基本用法：jps [options] [hostid]

五.jstat：
	jstat -<option> [-t] [-h<lines>] <vmid> [<interval>] [<count>]
	使用样例：jstat -class -t -h3 2280 1000 10
Timestamp       Loaded  Bytes  Unloaded  Bytes     Time
          393.9    684  1346.8        0     0.0       0.19
          394.8    684  1346.8        0     0.0       0.19
          395.8    684  1346.8        0     0.0       0.19
Timestamp       Loaded  Bytes  Unloaded  Bytes     Time
          396.8    684  1346.8        0     0.0       0.19
          397.9    684  1346.8        0     0.0       0.19
          398.9    684  1346.8        0     0.0       0.19
Timestamp       Loaded  Bytes  Unloaded  Bytes     Time
          399.9    684  1346.8        0     0.0       0.19
          400.9    684  1346.8        0     0.0       0.19
          401.9    684  1346.8        0     0.0       0.19
Timestamp       Loaded  Bytes  Unloaded  Bytes     Time
          402.9    684  1346.8        0     0.0       0.19

     
六.浅堆、深堆和实际对象大小：

七.内存泄露：一些系统不需要使用的对象仍被其他对象所引用，导致JVM无法回收

八.内存溢出:申请内存时，GC之后没有足够的内存可以使用

九.8种内存泄漏的场景：
	1.静态集合类：声明了static的集合类，那么这个集合类的生命周期就和JVM的消亡一致，如果向该集合中添加了对象，这个对象可能已经不需要使用了，那么该对象的就会一直无法被回收
```java
static List list = new ArrayList();

    public void oomTests() {
        Object obj = new Object();
        list.add(obj);
    }
```
	2.单例模式：单例模式创建的对象与JVM的生命周期一致，如果单例对象持有某个外部对象，那么这个外部对象就会一直无法回收，导致内存泄露；
	3.内部类持有外部类：外部类的内部方法可以获取内部类对象，若某个对象调用该内部方法获取内部类实例，此时外部类无法被回收；
	4.各种连接，如数据库连接，网络连接和IO连接等：各种连接如果不显式的关闭，也无法被JVM回收
	5.变量不合理的作用域：局部变量定义为成员变量, 导致方法执行完变量并没被回收
	6.改变Hash值：改变HashSet中对象某个参与hashCode方法的属性值，会导致从HashSet中无法单独删除该对象，造成内存泄露
	注：String是不可变类型，所以我们可以放心的把String插入HashSet,活着把String当成HashMap的值
```java
public class ChangeHashCode {
    public static void main(String[] args) {
        HashSet set = new HashSet();
        Person p1 = new Person(1001, "AA");
        Person p2 = new Person(1002, "BB");

        set.add(p1);
        set.add(p2);
        // p1的name更改了，导致p1的HashCode值变了，导致Hashset删除p1的时候通过HashCode无法找到原来的值，导致了内存的泄漏
        p1.name = "CC";
        set.remove(p1); //删除失败

        System.out.println(set);

        set.add(new Person(1001, "CC"));
        System.out.println(set);

        set.add(new Person(1001, "AA"));
        System.out.println(set);

    }
}

class Person {
    int id;
    String name;

    public Person(int id, String name) {
        this.id = id;
        this.name = name;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Person)) return false;

        Person person = (Person) o;

        if (id != person.id) return false;
        return name != null ? name.equals(person.name) : person.name == null;
    }

    @Override
    public int hashCode() {
        int result = id;
        result = 31 * result + (name != null ? name.hashCode() : 0);
        return result;
    }

    @Override
    public String toString() {
        return "Person{" +
                "id=" + id +
                ", name='" + name + '\'' +
                '}';
    }
}
```
	7.缓存泄露：比如应用启动时加载某个表中的数据到缓存（内存）中，测试环境只有几百条数据，但是生产环境中却有几百万条数据，导致内存泄露，解决方式，将这些数据读取到WeakHashMap中
	WeakHashMap的特点：当除了自身对key的引用外,此key没有其他引用，那么map会自动丢弃此值
```java
public class MapTest {
    static Map wMap = new WeakHashMap();
    static Map map = new HashMap();

    public static void main(String[] args) {
        init();
        testWeakHashMap();
        testHashMap();
    }

    public static void init() {
        String ref1 = new String("obejct1");
        String ref2 = new String("obejct2");
        String ref3 = new String("obejct3");
        String ref4 = new String("obejct4");
        wMap.put(ref1, "cacheObject1");
        wMap.put(ref2, "cacheObject2");
        map.put(ref3, "cacheObject3");
        map.put(ref4, "cacheObject4");
        System.out.println("String引用ref1，ref2，ref3，ref4 消失");

    }

    public static void testWeakHashMap() {

        System.out.println("WeakHashMap GC之前");
        for (Object o : wMap.entrySet()) {
            System.out.println(o);
        }
        try {
            System.gc();
            TimeUnit.SECONDS.sleep(5);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("WeakHashMap GC之后");
        for (Object o : wMap.entrySet()) {
            System.out.println(o);
        }
    }

    public static void testHashMap() {
        System.out.println("HashMap GC之前");
        for (Object o : map.entrySet()) {
            System.out.println(o);
        }
        try {
            System.gc();
            TimeUnit.SECONDS.sleep(5);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("HashMap GC之后");
        for (Object o : map.entrySet()) {
            System.out.println(o);
        }
    }

}
```
	8.监听器和回调：如果客户端在你实现的API中注册回调，却没有显示的取消，那么就无法积聚。需要确保回调立即被当作垃圾回收的最佳方法是只保存它的弱引用，例如将他们保存成为WeakHashMap中的键

十.内存泄露案例：
	案例一：使用java代码实现栈
```java
public class Stack {
    private Object[] elements;
    private int size = 0;
    private static final int DEFAULT_INITIAL_CAPACITY = 16;

    public Stack() {
        elements = new Object[DEFAULT_INITIAL_CAPACITY];
    }

    public void push(Object e) { //入栈
        ensureCapacity();
        elements[size++] = e;
    }
    //存在内存泄漏
//    public Object pop() { //出栈
//        if (size == 0)
//            throw new EmptyStackException();
//        return elements[--size];
//    }

    public Object pop() {
        if (size == 0)
            throw new EmptyStackException();
        Object result = elements[--size];
        elements[size] = null;
        return result;
    }

    private void ensureCapacity() {
        if (elements.length == size)
            elements = Arrays.copyOf(elements, 2 * size + 1);
    }
}
```

十一.Arthas的使用及了解：
	(1).好用的命令：
		1.jad命令将JVM中实际运行的class的byte code反编译成java代码便于你理解业务逻辑；
			在Arthas Console上反编译出来的源码是带语法高亮的阅读更方便
			当然反编译出来的java代码可能会存在语法错误但不影响你进行阅读理解
			使用例子：(jad java.lang.String)
		2.monitor——方法执行监控
			使用例子：monitor -c 5 demo.MathGame primeFactors
			返回方法总调用次数，成功次数，失败次数，平均RT（运行时间），失败率等信息
		3.watch——方法执行数据观测
			使用例子：watch demo.MathGame primeFactors -x 2(观察primeFactors方法的执行数据)
```java
Press Q or Ctrl+C to abort.
Affect(class count: 1 , method count: 1) cost in 32 ms, listenerId: 5
method=demo.MathGame.primeFactors location=AtExceptionExit
ts=2021-08-31 15:22:57; [cost=0.220625ms] result=@ArrayList[
    @Object[][
        @Integer[-179173],
    ],
    @MathGame[
        random=@Random[java.util.Random@31cefde0],
        illegalArgumentCount=@Integer[44],
    ],
    null,
]
method=demo.MathGame.primeFactors location=AtExit
ts=2021-08-31 15:22:58; [cost=1.020982ms] result=@ArrayList[
    @Object[][
        @Integer[1],
    ],
    @MathGame[
        random=@Random[java.util.Random@31cefde0],
        illegalArgumentCount=@Integer[44],
    ],
    @ArrayList[
        @Integer[2],
        @Integer[2],
        @Integer[26947],
    ],
]
```
	
