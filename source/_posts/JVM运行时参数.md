---
title: JVM运行时参数
date: 2022-06-4 16:15:38
tags:
---

一.标准参数选项：
	(1).常用命令：
		-version，-help

二.-X类型参数：
	java -X命令可以查看所有-X类型命令
	-Xbatch           禁用后台编译
    -Xbootclasspath/a:<以 ; 分隔的目录和 zip/jar 文件>
                      附加在引导类路径末尾
    -Xcheck:jni       对 JNI 函数执行其他检查
    -Xcomp            在首次调用时强制编译方法
    -Xdebug           为实现向后兼容而提供
    -Xdiag            显示附加诊断消息
    -Xfuture          启用最严格的检查，预期将来的默认值
    -Xint             仅解释模式执行
    -Xinternalversion
                      显示比 -version 选项更详细的 JVM
                      版本信息
    -Xloggc:<文件>    将 GC 状态记录在文件中（带时间戳）
    -Xmixed           混合模式执行（默认值）
    -Xmn<大小>        为年轻代（新生代）设置初始和最大堆大小
                      （以字节为单位）
    -Xms<大小>        设置初始 Java 堆大小
    -Xmx<大小>        设置最大 Java 堆大小
    -Xnoclassgc       禁用类垃圾收集
    -Xrs              减少 Java/VM 对操作系统信号的使用（请参见文档）
    -Xshare:auto      在可能的情况下使用共享类数据（默认值）
    -Xshare:off       不尝试使用共享类数据
    -Xshare:on        要求使用共享类数据，否则将失败。
    -XshowSettings    显示所有设置并继续
    -XshowSettings:all
                      显示所有设置并继续
    -XshowSettings:locale
                      显示所有与区域设置相关的设置并继续
    -XshowSettings:properties
                      显示所有属性设置并继续
    -XshowSettings:vm
                      显示所有与 vm 相关的设置并继续
    -XshowSettings:system
                      （仅 Linux）显示主机系统或容器
                      配置并继续
    -Xss<大小>        设置 Java 线程堆栈大小
    -Xverify          设置字节码验证器的模式

    (1).重要参数解释：
     -Xint             仅解释模式执行
     -Xcomp            在首次调用时强制编译方法
     -Xmixed           混合模式执行（默认值）

     -Xmn<大小>        为年轻代（新生代）设置初始和最大堆大小（以字节为单位）
     -Xms<大小>        设置初始 Java 堆大小，等价于-XX:InitialHeapSize
     -Xmx<大小>        设置最大 Java 堆大小，等价于-XX:MaxHeapSize
     -Xss<大小>        设置 Java 线程堆栈大小，等价于-XX:ThreadStackSize

三.-XX类型参数：
	-XX:+PrintFlagsFinal   输出所有JVM参数名称和默认值

四.添加JVM参数：
	运行jar包：java -Xms500m -Xmx500m -xx:+PrintGCDetails -xx:+PrintGCTimeStamps -jar demo.jar
	程序运行过程中：jinfo -flag 参数 值 <pid> 只有部分值支持修改
```java
C:\Users\shuaixiang>jinfo -flag +UseG1GC 14228
Exception in thread "main" com.sun.tools.attach.AttachOperationFailedException: flag 'UseG1GC' cannot be changed
        at jdk.attach/sun.tools.attach.VirtualMachineImpl.execute(VirtualMachineImpl.java:130)
        at jdk.attach/sun.tools.attach.HotSpotVirtualMachine.executeCommand(HotSpotVirtualMachine.java:309)
        at jdk.attach/sun.tools.attach.HotSpotVirtualMachine.setFlag(HotSpotVirtualMachine.java:282)
        at jdk.jcmd/sun.tools.jinfo.JInfo.flag(JInfo.java:152)
        at jdk.jcmd/sun.tools.jinfo.JInfo.main(JInfo.java:127)
```

五.常用的JVM参数选项：
	(1).打印设置的XX选项及值:
		-XX:+PrintFlagsFinal   打印出XX选项在运行程序时生效的值
		jinfo -flag UseParNewGC <pid>  查看具体某项的值
	(2).堆，栈，方法区等内存大小的设置：
		1.栈：
		    -Xss128k        设置 Java 线程的栈大小，等价于-XX:ThreadStackSize
		2.堆内存：
			-Xmn<大小>                        设置年轻代（新生代）大小，官方推荐配置为整个堆的3/8
            -Xms<大小>                        设置初始 Java 堆大小，等价于-XX:InitialHeapSize
            -Xmx<大小>                        设置最大 Java 堆大小，等价于-XX:MaxHeapSize
            -XX:NewSize=1024m                 设置年轻代初始值为1024m
            -XX:MaxNewSize=1024m              设置年轻代最大值为1024m
            -XX:SurvivorRatio=8               设置年轻代中Eden区与一个Survivor区的比值，默认为8
            -XX:+UseAdaptiveSizePolicy        自动选择新生代各区大小比例（默认是开启状态，会对Eden，Survivor的比例自动分配）
            // 若想禁用除了加上-XX:-UseAdaptiveSizePolicy外，还需要加上-XX:SurvivorRatio=8
            -XX:NewRatio=4                    设置老年代与年轻代（包括一个Eden和两个Survivor区）的比值,默认2：1
            -XX:PretenureSizeThreadshold=1024 设置让大于此阈值的对象直接分配在老年代，单位为字节，只对Serial,ParNew收集器有效
            -XX:MaxTenuringThreshold=15       默认值为15，新生代每次MinorGC后，还存活的对象年龄 + 1，当对象的年龄大于这个值时就会进入老年代
            -XX:+PrintTenuringDistribution    让JVM在每次MinorGC后打印出当前使用的Survivor中对象的年龄分布
            -XX:TargetSurvivorRatio           表示MinorGC结束后Survivor区域中占用空间的期望比例
    	3.永久代（jdk7）,元空间（jdk8+）: 
    		永久代：-XX:PermSize=256m      设置永久代初始值为256m
    		       -XX:MaxPermSize=256m   设置永久代最大值为256m
    		元空间：-XX:MetaspaceSize      初始空间大小
    			   -XX:MaxMetaspaceSize   最大空间，默认没有限制
    			   -XX:+UseCompressedOops 压缩对象指针
    			   -XX:+UseCompressedClassPointers    压缩类指针
    			   -XX:CompressedClassSpaceSize       设置Klass Metaspace的大小，默认1G
    	4.直接内存：-XX:MaxDirectMemorySize      指定DirectMemory容量，若未指定，则默认与java堆最大值一样
    (3).OMM相关参数：
    	-XX:+HeapDumpOnOutOfMemoryError   表示在内存出现OOM的时候，把Heap转存（Dump）到文件以便后续分析
        -XX:+HeapDumpBeforeFullGC         表示在出现FullGC之前，生成Heap转储文件
        -XX:HeapDumpPath=d:\heapdumpinstance.hprof  指定heap转储文件路径
        -XX:OnOutOfMemoryError            指定一个可行性程序或者脚本路径，当发生OOM的时候，去执行这个脚本
        例如：-XX:OnOutOfMemoryError=/opt/Server/restart.sh   发生OOM，执行restart.sh文件进行重启
    (4).垃圾收集相关参数：
    	-XX:+PrintCommandLineFlags       查看命令行相关参数（包含使用的垃圾回收器）
    	jinfo -flag 相关垃圾回收器参数 <pid>    
    	1.SerialGC与SerialOldGC(MSC):-XX:+UseSerialGC(主要应用于特定的低配环境，单核cup的情景)
    	2.ParNewGC:-XX:+UseParNewGC(并行的垃圾回收器),-XX:ParallelGCThreads=N(设置线程数量, 8个CPU内默认和CPU数量相同)
    	3.ParallelScavengeGC(吞吐量优先)与ParallelOldGC:
    	  -XX:+UseParallelGC与-XX:+UseParallelOldGC搭配，这两可以互相激活，
    	  -XX:ParallelGCThreads=N当CPU个数大于8个时，ParallelGCThreads的值等于3+[5 * CPU_Count/8]
    	  -XX:MaxGCPauseMillis 设置垃圾收集的最大停顿时间（即STW的时间），单位毫秒
    	  为了尽可能的把停顿时间控制在MaxGCPauseMillis以内，收集器在工作时会调整java堆大小或者其他的一些参数，
    	  该参数谨慎使用
    	  -XX:GCTimeRatio=N 设置垃圾收集时间占总时间的比例（1 / (N + 1)）。用于衡量吞吐量的大小
    	  取值范围（0，100），默认值99，也就是垃圾回收时间不超过1%
    	  与上面的MaxGCPauseMillis参数有一定的矛盾性。暂停时间越长，Radio参数就容易超过设定比例
    	  -XX:+UseAdaptiveSizePolicy 设置Parallel Scavenge收集器具有自适应调节策略
    	4.CMSGC:-XX:+UseConcMarkSweepGC (HostPort虚拟机第一款并发的垃圾回收器，用户线程和垃圾回收线程可以同时执行)
    	  可惜的是CMS只能与ParNewGC和SerialGC搭配，不能与ParallelGC搭配
    	  使用的是标记清除算法，会导致内存碎片化的问题，可以使用-XX:+UseCMSCompactAtFullCollection在Full GC之后进行碎片化的整理，但是这样会导致STW的时间会更长
    	  在JDK9已经被标记为过时了，在JDK14中已经被拿掉了
    	5.G1：-XX:+UseG1GC（分代收集，堆空间被分为一个一个的Region）
    	  -XX:G1HeapRegionSize  设置每个Region的大小，值是2的幂，范围在1MB到32MB之间，目标是根据java堆大小划分出约2048个
    	  区域，默认是堆内存的1/2000
    	  -XX:MaxGCPauseMillis 设置垃圾收集的最大停顿时间（即STW的时间），默认值200ms
    	  -XX:ParallelGCThreads=N  设置STW时GC线程数量,最多设置为8个
    	  -XX:ConcGCThreads  设置并发标记的线程数，将设置为ParallelGCThreads的1/4左右
          -XX:InitiatingHeapOccupancyPercent 设置触发并发GC周期的Java堆占用率阈值，超过此值，就触发GC
          -XX:G1NewSizePercent、-XX:G1MaxNewSizePercent  设置新生代占用整个堆内存的最小百分比
          （默认5%）,最大百分比（默认60%）
          -XX:G1ReservePercent=10保留内存区域，防止to space(Survivor中的to区)溢出
    垃圾回收器组合关系图：


    (5).GC日志相关参数：
    	-verbose:gc或者-XX:+PrintGC 表示打开简化的GC日志
```java
[GC (Allocation Failure)  16302K->14914K(59392K), 0.0044727 secs]
[GC (Allocation Failure)  31234K->31192K(59392K), 0.0059224 secs]
[Full GC (Ergonomics)  31192K->30961K(59392K), 0.0094891 secs]
[Full GC (Ergonomics)  47312K->46963K(59392K), 0.0071196 secs]
```
		-XX:+PrintGCDetails        在发生垃圾回收时打印内存回收详细的日志，并在进程退出时输出当前的内存各区域分配的情况
```java
[GC (Allocation Failure) [PSYoungGen: 16302K->2016K(18432K)] 16302K->14850K(59392K), 0.0056557 secs] [Times: user=0.00 sys=0.00, real=0.01 secs] 
[GC (Allocation Failure) [PSYoungGen: 18336K->2032K(18432K)] 31170K->31204K(59392K), 0.0070365 secs] [Times: user=0.00 sys=0.00, real=0.01 secs] 
[Full GC (Ergonomics) [PSYoungGen: 2032K->0K(18432K)] [ParOldGen: 29172K->30961K(40960K)] 31204K->30961K(59392K), [Metaspace: 3448K->3448K(1056768K)], 0.0074910 secs] [Times: user=0.14 sys=0.02, real=0.01 secs] 
[Full GC (Ergonomics) [PSYoungGen: 16350K->6100K(18432K)] [ParOldGen: 30961K->40862K(40960K)] 47312K->46963K(59392K), [Metaspace: 3448K->3448K(1056768K)], 0.0075273 secs] [Times: user=0.00 sys=0.00, real=0.01 secs] 
Heap
 PSYoungGen      total 18432K, used 9983K [0x00000000fec00000, 0x0000000100000000, 0x0000000100000000)
  eden space 16384K, 60% used [0x00000000fec00000,0x00000000ff5bfdc0,0x00000000ffc00000)
  from space 2048K, 0% used [0x00000000ffe00000,0x00000000ffe00000,0x0000000100000000)
  to   space 2048K, 0% used [0x00000000ffc00000,0x00000000ffc00000,0x00000000ffe00000)
 ParOldGen       total 40960K, used 40862K [0x00000000fc400000, 0x00000000fec00000, 0x00000000fec00000)
  object space 40960K, 99% used [0x00000000fc400000,0x00000000febe7be0,0x00000000fec00000)
 Metaspace       used 3454K, capacity 4496K, committed 4864K, reserved 1056768K
  class space    used 378K, capacity 388K, committed 512K, reserved 1048576K
```
		-XX:+PrintGCTimeStamps(不可以单独使用):输出GC发生时的时间戳 -XX:+PrintGCDetails
```java
4.489: [GC (Allocation Failure) [PSYoungGen: 16302K->2032K(18432K)] 16302K->14858K(59392K), 0.0058347 secs] [Times: user=0.00 sys=0.00, real=0.01 secs] 
9.539: [GC (Allocation Failure) [PSYoungGen: 18352K->2016K(18432K)] 31178K->31160K(59392K), 0.0069080 secs] [Times: user=0.00 sys=0.00, real=0.01 secs] 
9.546: [Full GC (Ergonomics) [PSYoungGen: 2016K->0K(18432K)] [ParOldGen: 29144K->30961K(40960K)] 31160K->30961K(59392K), [Metaspace: 3448K->3448K(1056768K)], 0.0076182 secs] [Times: user=0.16 sys=0.00, real=0.01 secs] 
14.521: [Full GC (Ergonomics) [PSYoungGen: 16350K->6100K(18432K)] [ParOldGen: 30961K->40862K(40960K)] 47312K->46963K(59392K), [Metaspace: 3448K->3448K(1056768K)], 0.0071428 secs] [Times: user=0.00 sys=0.00, real=0.01 secs] 
```
		-XX:+PrintGCDateStamps(不可以单独使用)：输出GC发生的日期 -XX:+PrintGCDetails
```java
2022-06-04T23:20:35.268+0800: [GC (Allocation Failure) [PSYoungGen: 16302K->2016K(18432K)] 16302K->14890K(59392K), 0.0979226 secs] [Times: user=0.00 sys=0.00, real=0.10 secs] 
2022-06-04T23:20:40.410+0800: [GC (Allocation Failure) [PSYoungGen: 18336K->2008K(18432K)] 31210K->31192K(59392K), 0.0048006 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
2022-06-04T23:20:40.415+0800: [Full GC (Ergonomics) [PSYoungGen: 2008K->0K(18432K)] [ParOldGen: 29184K->30963K(40960K)] 31192K->30963K(59392K), [Metaspace: 3448K->3448K(1056768K)], 0.0086367 secs] [Times: user=0.16 sys=0.00, real=0.01 secs] 
2022-06-04T23:20:45.483+0800: [Full GC (Ergonomics) [PSYoungGen: 16322K->6501K(18432K)] [ParOldGen: 30963K->40764K(40960K)] 47286K->47265K(59392K), [Metaspace: 3448K->3448K(1056768K)], 0.0116466 secs] [Times: user=0.00 sys=0.00, real=0.01 secs] 
```
		-XX:+PrintHeapAtGC    每一次GC前和GC后，都打印堆信息
```java
{Heap before GC invocations=1 (full 0):
 PSYoungGen      total 18432K, used 16302K [0x00000000fec00000, 0x0000000100000000, 0x0000000100000000)
  eden space 16384K, 99% used [0x00000000fec00000,0x00000000ffbeb818,0x00000000ffc00000)
  from space 2048K, 0% used [0x00000000ffe00000,0x00000000ffe00000,0x0000000100000000)
  to   space 2048K, 0% used [0x00000000ffc00000,0x00000000ffc00000,0x00000000ffe00000)
 ParOldGen       total 40960K, used 0K [0x00000000fc400000, 0x00000000fec00000, 0x00000000fec00000)
  object space 40960K, 0% used [0x00000000fc400000,0x00000000fc400000,0x00000000fec00000)
 Metaspace       used 3447K, capacity 4496K, committed 4864K, reserved 1056768K
  class space    used 377K, capacity 388K, committed 512K, reserved 1048576K
Heap after GC invocations=1 (full 0):
 PSYoungGen      total 18432K, used 2016K [0x00000000fec00000, 0x0000000100000000, 0x0000000100000000)
  eden space 16384K, 0% used [0x00000000fec00000,0x00000000fec00000,0x00000000ffc00000)
  from space 2048K, 98% used [0x00000000ffc00000,0x00000000ffdf8100,0x00000000ffe00000)
  to   space 2048K, 0% used [0x00000000ffe00000,0x00000000ffe00000,0x0000000100000000)
 ParOldGen       total 40960K, used 12865K [0x00000000fc400000, 0x00000000fec00000, 0x00000000fec00000)
  object space 40960K, 31% used [0x00000000fc400000,0x00000000fd0907e0,0x00000000fec00000)
 Metaspace       used 3447K, capacity 4496K, committed 4864K, reserved 1056768K
  class space    used 377K, capacity 388K, committed 512K, reserved 1048576K
}

{Heap before GC invocations=3 (full 1):
 PSYoungGen      total 18432K, used 2040K [0x00000000fec00000, 0x0000000100000000, 0x0000000100000000)
  eden space 16384K, 0% used [0x00000000fec00000,0x00000000fec00000,0x00000000ffc00000)
  from space 2048K, 99% used [0x00000000ffe00000,0x00000000ffffe110,0x0000000100000000)
  to   space 2048K, 0% used [0x00000000ffc00000,0x00000000ffc00000,0x00000000ffe00000)
 ParOldGen       total 40960K, used 29184K [0x00000000fc400000, 0x00000000fec00000, 0x00000000fec00000)
  object space 40960K, 71% used [0x00000000fc400000,0x00000000fe080210,0x00000000fec00000)
 Metaspace       used 3448K, capacity 4496K, committed 4864K, reserved 1056768K
  class space    used 377K, capacity 388K, committed 512K, reserved 1048576K
Heap after GC invocations=3 (full 1):
 PSYoungGen      total 18432K, used 0K [0x00000000fec00000, 0x0000000100000000, 0x0000000100000000)
  eden space 16384K, 0% used [0x00000000fec00000,0x00000000fec00000,0x00000000ffc00000)
  from space 2048K, 0% used [0x00000000ffe00000,0x00000000ffe00000,0x0000000100000000)
  to   space 2048K, 0% used [0x00000000ffc00000,0x00000000ffc00000,0x00000000ffe00000)
 ParOldGen       total 40960K, used 30961K [0x00000000fc400000, 0x00000000fec00000, 0x00000000fec00000)
  object space 40960K, 75% used [0x00000000fc400000,0x00000000fe23c758,0x00000000fec00000)
 Metaspace       used 3448K, capacity 4496K, committed 4864K, reserved 1056768K
  class space    used 377K, capacity 388K, committed 512K, reserved 1048576K
}
```
		-Xloggc:d:/JVM/heaplog.log   将日志信息输出到指定位置
	(6).其他参数：
		-XX:+UseTLAB  使用TLAB，默认开启的
六.通过java代码获取JVM参数：(监控我们的应用服务器的堆内存使用情况，设置一些阈值进行报警等处理)
```java
		MemoryMXBean memorymbean = ManagementFactory.getMemoryMXBean();
        MemoryUsage usage = memorymbean.getHeapMemoryUsage();
        System.out.println("INIT HEAP: " + usage.getInit() / 1024 / 1024 + "m");
        System.out.println("MAX HEAP: " + usage.getMax() / 1024 / 1024 + "m");
        System.out.println("USE HEAP: " + usage.getUsed() / 1024 / 1024 + "m");
        System.out.println("\nFull Information:");
        System.out.println("Heap Memory Usage: " + memorymbean.getHeapMemoryUsage());
        System.out.println("Non-Heap Memory Usage: " + memorymbean.getNonHeapMemoryUsage());

        System.out.println("=======================通过java来获取相关系统状态============================ ");
        System.out.println("当前堆内存大小totalMemory " + (int) Runtime.getRuntime().totalMemory() / 1024 / 1024 + "m");// 当前堆内存大小
        System.out.println("空闲堆内存大小freeMemory " + (int) Runtime.getRuntime().freeMemory() / 1024 / 1024 + "m");// 空闲堆内存大小
        System.out.println("最大可用总堆内存maxMemory " + Runtime.getRuntime().maxMemory() / 1024 / 1024 + "m");// 最大可用总堆内存大小
```
七.GC日志分类：
	部分收集：
	(1).新生代收集(Minor GC / Young GC):只是新生代（Eden\S0,S1）的垃圾收集
	(2).老年代收集(Major GC / Old GC):只是老年代的垃圾收集。
		目前：只有CMS GC会有单独收集老年代的行为。
		注意：很多时候Major GC会和Full GC混淆使用，需要具体分辨是老年代回收还是整堆回收
	(3).混合收集（Mixed GC):收集整个新生代以及部分老年代的垃圾收集
		目前：只有G1、GC会有这种行为
	整堆收集：
	(1).Full GC：收集整个java堆和方法区的垃圾收集

八.那些情况会触发Full GC?
	1.老年代空间不足；
	2.方法区空间不足；
	3.显示调用System.gc();
	4.Minor GC进入老年代的数据的平均大小大于老年代的可用内存；
	5.大对象直接进入老年代，而老年代空间不足；

九.常见的日志分析工具：
	GCEasy:https://gceasy.io/
	GCViewer

十.OOM常见各种场景及解决方案：
	1.堆溢出：
	2.元空间溢出：
	3.GC overhead limit exceeded:
	4.线程溢出：

十一.性能优化案例：
	性能测试工具：Jmeter
	1.调整堆大小提高服务的吞吐量;
	2.调整垃圾回收器提高服务的吞吐量；
	3.JVM优化之JIT优化；
	4.G1并发执行的线程数对性能的影响；
	5.合理配置堆内存；
	6.特殊问题：新生代与老年代的比例；
	7.CPU占用很高排查方案；
	8.日均百万级订单交易系统如何设置JVM参数；




