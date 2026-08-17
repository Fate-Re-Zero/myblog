---
title: Class文件结构
date: 2022-05-22 20:00:38
tags:
---

一.Java语言：跨平台的语言
	(1).正真实现Java跨平台的其实是字节码，Java源代码及其他可以编译成字节码码的语言编译后直接可以运行在各个平台的虚拟机上，实现了一次编译，到处运行；

二.Java虚拟机：跨语言的平台
	(1).Java虚拟机不和包括Java在内的任何语言绑定,它只与"Class"文件这种特定的二进制文件格式所关联

三.类文件结构有几个部分：

四.关于String一个题目：
```java
	// 通过下述字节码文件可知
	// 首先在堆中创建了StringBuilder对象，然后在堆中创建hello的String对象，然后调用了StringBuilder的Append
	方法拼接hello,然后又在堆中创建了world的String对象，然后再次调用了append方法拼接了world,最后调用了StringBuilder的toString方法，toString方法底层其实就是new了一个String对象，相当于再次在堆中创建了helloworld的String对象。
	String str = new String("hello") + new String("world");
	// 下面这行注释若打开，第一个str == str1将为true,str调用intern方法，首先会查找字符串常量池中是
	否存在该字面值相同的字符串常量，若存在，则直接将该字符串常量引用返回指向str变量，若不存在，则在字符串常量池中创建该字符串常量，并返回引用指向str变量
	// str.intern(); 
	// 在字符串常量池创建helloworld对象
    String str1 = "helloworld";
    System.out.println(str == str1);  // false
    // 再次在堆中创建新的helloworld对象，注意堆中可以存在字面值相同的但是引用不同的两个String对象,但是字符串常量池中一个字面值只能有一个对象
    String str2 = new String("helloworld");
    System.out.println(str == str2);  // false
```

    上述文件对应的字节指令
```java
0 new #2 <java/lang/StringBuilder>
3 dup
4 invokespecial #3 <java/lang/StringBuilder.<init>>
7 new #4 <java/lang/String>
10 dup
11 ldc #5 <hello>
13 invokespecial #6 <java/lang/String.<init>>
16 invokevirtual #7 <java/lang/StringBuilder.append>
19 new #4 <java/lang/String>
22 dup
23 ldc #8 <world>
25 invokespecial #6 <java/lang/String.<init>>
28 invokevirtual #7 <java/lang/StringBuilder.append>
31 invokevirtual #9 <java/lang/StringBuilder.toString>
34 astore_1
35 ldc #10 <helloworld>
37 astore_2
38 getstatic #11 <java/lang/System.out>
41 aload_1
42 aload_2
43 if_acmpne 50 (+7)
46 iconst_1
47 goto 51 (+4)
50 iconst_0
51 invokevirtual #12 <java/io/PrintStream.println>
54 new #4 <java/lang/String>
57 dup
58 ldc #10 <helloworld>
60 invokespecial #6 <java/lang/String.<init>>
63 astore_3
64 getstatic #11 <java/lang/System.out>
67 aload_1
68 aload_3
69 if_acmpne 76 (+7)
72 iconst_1
73 goto 77 (+4)
76 iconst_0
77 invokevirtual #12 <java/io/PrintStream.println>
80 return
```

五.一个关于多态的题目：
```java
/*
成员变量（非静态的）的赋值过程： ① 默认初始化 - ② 显式初始化 /代码块中初始化 - ③ 构造器中初始化 - ④ 有了对象之后，可以“对象.属性”或"对象.方法"
 的方式对成员变量进行赋值。
 */
class Father {
    int x = 10;

    public Father() {
    	// 3.此时x只进行了默认初始化，x =0
        this.print();
        // 5.将x赋值为20
        x = 20;
    }
    public void print() {
    	// 4.打印x = 0
        System.out.println("Father.x = " + x);
    }
}

class Son extends Father {
	// 1.默认赋值后，执行属性赋值x=30
    int x = 30;
//    float x = 30.1F;
	// 2.执行字类构造方法前首先执行父类构造方法
    public Son() {
    	// 6.打印x = 30
        this.print();
        // 7.将x赋值为40
        x = 40;
    }
    public void print() {
        System.out.println("Son.x = " + x);
    }
}

public class SonTest {
    public static void main(String[] args) {
        Father f = new Son();
        // 注意成员变量属性无多态特性
        System.out.println(f.x);
    }
}
```

六.Class类的本质：
	Class文件是一组以8位字节为基础单位的二进制流

七.Class文件结构：
	(1).魔数：识别当前文件是一个Class文件;都是以ca fe ba be开始的（4个字节）
	(2).Class文件版本；（5，6两个字节代表副版本；7,8两个字节代表主版本）
	(3).常量池；
	-- 常量池计数器 = 常量池表的实际长度 + 1
	--(如方法的符号引用，参数字面量，参数类型，方法返回值字面量，返回值类型，字段的符号引用，字段类型等) 
	--（前两个字节，常量池计数器，后n个字节常量池表） 
	--（常量池表项中，用于存放编译时期生成的各种字面量和符号引用，这部分内容将在类加载后进入方法区的运行时常量池中存放）
	(4).访问标识；（标记是类、接口、枚举；标记访问权限；标记是否是抽象类；标记是否有final修饰）
	(5).类索引、父类索引、接口索引：（类索引；父类索引；接口计数器；实现接口集合）
	(6).字段（Filed属性）表集合：（类级变量以及实例实例变量，不包含局部变量；字段表计数器；字段访问标识
	字段名索引；字段描述符索引;字段属性计数器;属性表集合）
	(7).方法表集合:(方法计数器;方法表；方法访问标识;方法名索引;方法描述符索引;方法的属性计数器;
	属性计数器；属性名索引;属性长度；操作数栈的最大深度；局部变量表的长度；字节码指令的长度；具体的字节码指令；异常表的长度；Code中的属性计数器；LineNumberTable_attribute；LocalVariableTable_attribute)
	(8).属性表集合:(不是我们平时所说的类的属性,指的是class文件的辅助信息；附加属性计数器，属性名索引；
	属性的长度；源码文件索引；源码文件名称)

八.javac -g 操作说明:相对于javac会多编译出一些局部变量表信息，IDEA使用同样是javac -g

九.javap命令的参数说明：
  -version                         版本信息
  -public                          仅显示公共类和成员
  -protected                       显示受保护的/公共类和成员
  -package                         显示程序包/受保护的/公共类和成员 (默认)
  -sysinfo                         显示正在处理的类的系统信息 (路径, 大小, 日期, MD5 散列)

  -p  -private                     显示所有类和成员
  -v  -verbose                     输出附加信息
  -c                               对代码进行反汇编
  -s                               输出内部类型签名
  -l                               输出行号和本地变量表
                                 
  -constants                       显示最终常量
  --module <模块>, -m <模块>       指定包含要反汇编的类的模块
  --module-path <路径>             指定查找应用程序模块的位置
  --system <jdk>                   指定查找系统模块的位置
  --class-path <路径>              指定查找用户类文件的位置
  -classpath <路径>                指定查找用户类文件的位置
  -cp <路径>                       指定查找用户类文件的位置
  -bootclasspath <路径>            覆盖引导类文件的位置
注意：想要看到最全的文件结构使用javap -v -p

十.各基本数据类型所占的字节数及槽位数及对应的指令标识（short,byte,char,Boolean都表示为带符号的int）：
	byte:二进制位数为8，占1个字节，（-2^7 --> 2^7-1）,占1个slot
	short:二进制位数为16，占2个字节，（-2^15 --> 2^15-1）,占1个slot
	char:二进制位数为16，占2个字节，（0 --> 2^16-1）,占1个slot
	Boolean:二进制位数为1，占1个字节，（true,false）,占1个slot
	int:二进制位数为32，占4个字节，（-2^31 --> 2^31-1）,占1个slot
	float:二进制位数为32，占4个字节，（3.402823e+38 ~ 1.401298e-45）,占1个slot
	long:二进制位数为64，占8个字节，（-2^63 --> 2^63-1）,占2个slot
	double:二进制位数为64，占8个字节，（1.797693e+308~ 4.9000000e-324）,占2个slot

十一.类型转换:
	宽化类型转换：int --> long --> float --> double（i2l,l2f,f2d）
	宽化类型转换依然会出现精度损失问题（long(8个字节)-->float(4个字节)）：如下实例：
```java
public void upCast2(){
        int i = 123123123;
        float f = i;
        System.out.println(f);//123123120

        long l = 123123123123L;
        l = 123123123123123123L;
        double d = l;
        System.out.println(d);//123123123123123120

    }
```
	窄化类型转换：int --> byte, int -->short, int --> char(i2b,i2s,i2c)
	long --> int(l2i), float --> int(f2i), float --> long(f2l),double --> int(d2i),
	double --> long(d2l),double --> float(d2f)
	精度损失：JVM底层不会抛运行时异常
	代码样例：
```java
	public void downCast3(){
		short s = 10;
    	byte b = (byte)s;// i2b		
	}

    //窄化类型转换的精度损失
    @Test
    public void downCast4(){
        int i = 128;
        byte b = (byte)i;
        System.out.println(b);//-128
    }
```

十二.NaN和无穷大
```java
	//测试NaN,无穷大的情况
    @Test
    public void downCast5(){
        double d1 = Double.NaN; //0.0 / 0.0
        int i = (int)d1;
        System.out.println(d1);
        System.out.println(i);

        double d2 = Double.POSITIVE_INFINITY;
        long l = (long)d2;
        int j = (int)d2;
        System.out.println(l); // Long.MAX_VALUE
        System.out.println(Long.MAX_VALUE);
        System.out.println(j); // Integer.MAX_VALUE
        System.out.println(Integer.MAX_VALUE);

        float f = (float)d2;
        System.out.println(f); // Infinity

        float f1 = (float)d1;
        System.out.println(f1);// NaN
    }
```

十三.题目：
```java
	public long nextIndex() {
        // index的值为1了，但是返回的是0
        return index++;
    }

    private long index = 0;

   	//字节指令如下：
   	 0 aload_0
	 1 dup
	 2 getfield #2 <com/atguigu/java/StackOperateTest.index>
	 5 dup2_x1
	 6 lconst_1
	 7 ladd
	 8 putfield #2 <com/atguigu/java/StackOperateTest.index>
	11 lreturn

	// 分析如上字节指令
	0 将this对象引用地址加载到操作数栈（非静态方法局部变量表第0位是this的引用地址）
	1 复制this引用地址
	2 调用this的getfield(这个field不是显式的写在类中的方法)，意思是获取index字段值（此时顶部的this引用
	出栈,index字段入栈值为0，long类型占2个slot）
	5 复制两个slot的index下移3位(值为0)，也就是移到this引用地址的下面
	6 加载1进入操作数栈
	7 栈顶的index(值为0)与1相加
	8 栈顶做完加法的index（值为1）出栈
	11 最后返回栈中index(值为0)
```

十四.swithch case的特殊情况：
```java
	//jdk7新特性：引入String类型
    public void swtich3(String season){
        switch(season){
            case "SPRING":break;
            case "SUMMER":break;
            case "AUTUMN":break;
            case "WINTER":break;
        }
    }
    // 字节指令如下：
      0 aload_1
	  1 astore_2
	  2 iconst_m1
	  3 istore_3
	  4 aload_2
	  5 invokevirtual #11 <java/lang/String.hashCode>
	  8 lookupswitch 4
		-1842350579:  52 (+44)
		-1837878353:  66 (+58)
		-1734407483:  94 (+86)
		1941980694:  80 (+72)
		default:  105 (+97)
	 52 aload_2
	 53 ldc #12 <SPRING>
	 55 invokevirtual #13 <java/lang/String.equals>
	 58 ifeq 105 (+47)
	 61 iconst_0
	 62 istore_3
	 63 goto 105 (+42)
	 66 aload_2
	 67 ldc #14 <SUMMER>
	 69 invokevirtual #13 <java/lang/String.equals>
	 72 ifeq 105 (+33)
	 75 iconst_1
	 76 istore_3
	 77 goto 105 (+28)
	 80 aload_2
	 81 ldc #15 <AUTUMN>
	 83 invokevirtual #13 <java/lang/String.equals>
	 86 ifeq 105 (+19)
	 89 iconst_2
	 90 istore_3
	 91 goto 105 (+14)
	 94 aload_2
	 95 ldc #16 <WINTER>
	 97 invokevirtual #13 <java/lang/String.equals>
	100 ifeq 105 (+5)
	103 iconst_3
	104 istore_3
	105 iload_3
	106 tableswitch 0 to 3	0:  136 (+30)
		1:  139 (+33)
		2:  142 (+36)
		3:  145 (+39)
		default:  145 (+39)
	136 goto 145 (+9)
	139 goto 145 (+6)
	142 goto 145 (+3)
	145 return

	//分析如上字节指令：
	通过以上的字节码可以发现：对比String是否相同先调用了hashCode方法对比hashcode值是否相同，然后在调用equals方法进行对比
```

十五.同步控制指令（synchronized）：
	概述：java虚拟机支持两种同步结构:方法级的同步和方法内部一段指令序列的同步，这两种同步都是使用monitor来支持的。
	(1).方法级的同步:是隐式的,即无须通过字节码指令来控制,它实现在方法调用和返回操作之中。虚拟机可以从方法常量池的方法表结构中的ACC_SYNCHRONIZED访问标志得知一个方法是否声明为同步方法;
       1.当调用方法时,调用指令将会检查方法的AC_SYNCHRONIZED访问标志是否设置。
	   2.如果设置了,执行线程将先持有同步锁,然后执行方法。最后在方法完成(无论是正常完成还是非正常完成)时释放同步锁。
       3.在方法执行期间,执行线程持有了同步锁,其他任何线程都无法再获得同一个锁。
       4.如果一个同步方法执行期间抛出了异常,并且在方法内部无法处理此异常,那这个同步方法所持有的锁将在异常抛到同步方法之外时自动释放。
    (2).方法内指定指令序列的同步:
	同步一段指令集序列:通常是由java中的synchronized语句块来表示的。jvm的指令集有 monitorenter和monitorexit两条指令来
	支持synchronized关键字的语义。
	当一个线程进入同步代码块时，它使用monitorenter指令请求进入。如果当前对象的监视器计数器为0，则它会被准许进入，若为1，则判断持有当前监视器的线程是否为自己，如果是，则进入，否则进行等待，直到对象的监视器计数器为0，才会被允许进入同步块。

	当线程退出同步块时，需要使用monitorexit声明退出。在Java虚拟机中，任何对象都有一个监视器与之相关联，用来判断对象是否被锁定，当监视器被持有后，对象处于锁定状态。

	指令monitorenter和monitorexit在执行时，都需要在操作数栈顶压入对象，之后monitorenter和monitorexit的锁定和释放都是针对这个对象的监视器进行的。

	下图展示了监视器如何保护临界区代码不同时被多个线程访问，只有当线程4离开临界区后，线程1、2、3才有可能进入。
	![](/images/jvm/多线程访问同步代码块示例图.jpg)
	
```java
    public synchronized void add(){
        i++;
    }

    //字节码指令如下：
     0 aload_0
	 1 dup
	 2 getfield #2 <com/atguigu/java1/SynchronizedTest.i>
	 5 iconst_1
	 6 iadd
	 7 putfield #2 <com/atguigu/java1/SynchronizedTest.i>
	10 return 
	// 方法签名相关信息：
	Name: cp_info#21 <add>
	Descriptor: cp_info#11 <()V>
	Access Flags: 0x0021[public synchronized]
	//字节码解析如下：
	通过字节码指令可以看到，当synchronized标记方法时，字节码指令没有发生任何变化，但是方法前面签名信息会带上synchronized关键字
```

```java
	private int i = 0;
	private Object obj = new Object();
    public void subtract(){
        synchronized (obj){
            i--;
        }
    }
    //字节码指令如下：
     0 aload_0
	 1 getfield #4 <com/atguigu/java1/SynchronizedTest.obj>
	 4 dup
	 5 astore_1
	 6 monitorenter
	 7 aload_0
	 8 dup
	 9 getfield #2 <com/atguigu/java1/SynchronizedTest.i>
	12 iconst_1
	13 isub
	14 putfield #2 <com/atguigu/java1/SynchronizedTest.i>
	17 aload_1
	18 monitorexit
	19 goto 27 (+8)
	22 astore_2
	23 aload_1
	24 monitorexit
	25 aload_2
	26 athrow
	27 return

	//字节码解析如下：
	通过字节码指令
```
	