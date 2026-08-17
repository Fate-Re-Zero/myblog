---
title: JVM常用参数
date: 2022-08-14 10:03:38
tags: JVM
---

### GC常用参数
- -Xmn2048M  --- 年轻代大小
- -Xms4096M  --- 最小堆大小
- -Xmx4096M  --- 最大堆大小
- -Xss500M   --- 栈空间
- -XX:+UseTLAB  --- 使用TLAB,默认打开
- -XX:+PrintTLAB  --- 打印TLAB的使用情况
- -XX:+DisableExplictGC  --- 禁用System.gc()
- -XX:+PrintGC  --- 打印GC信息
- -XX:+PrintGCDetails  --- 打印详细GC信息
- -XX:+PrintHeapAtGC  --- 打印GC前后堆的使用情况
- -XX:+PrintGCTimeStamps --- 打印GC产生的时间
- -XX:+PrintFlagsFinal -version | grep G1  --- 打印JVM最终参数设置情况
- -XX:+PrintFlagsInitail -version | grep G1 --- 打印JVM初始参数设置情况
- -Xloggc:opt/gclog/gc.log  --- 指定GC日志文件位置
```
线上环境实际因按照下面的使用方式：
-Xloggc:/opt/gclog/logs/xxx-xxx-gc-%t.log -XX:+UseGCLogFileRotation 
-XX:NumberOfGCLogFiles=5 -XX:GCLogFileSize=20M -XX:+PrintGCDetails 
-XX:+PrintGCDateStamps -XX:+PrintGCCause
```
- -XX:MaxTenuringThreshold  --- 年轻代升到老年代的年龄，默认值/最大值：15

### Parallel常用参数
- -XX:+UseParallelGC； -XX:+UseParallelOldGC  --- 使用Parallel垃圾回收器
- -XX:MaxTenuringThreshold  --- 年轻代升到老年代的年龄，默认值/最大值：15
- -XX:+ParallelGCThreads  --- 并行收集器的线程数，parallel可以设置为和CPU核数相当，因为parallel垃圾回收过程是STW的
- -XX:MaxGCPauseMillis;(设置垃圾回收器的最大停顿时间，即STW时间，单位毫秒)
- -XX:GCTimeRatio;(垃圾收集时间占总时间的比例，取值范围(0,100),默认值99)
- -XX:+UseAdaptiveSizePolicy;(设置Parallel Scavenge收集器具有自适应调节策略)

### CMS常用参数
- -XX:+UseConcMarkSweepGC  --- 使用CMS垃圾回收器
- -XX:ParallelCMSThreads --- 并行收集的线程数，cms不可以设置为和CPU核数相当,建议设置为cpu核数的一半，因为cms垃圾回收过程并不是完全STW的，如果占用所有的核，用户线程就停止执行了，相当于STW了,CMS默认启动线程数是：（年轻代并行收集器的线程数 + 3）/4;
- -XX:CMSInitiatingOccupancyFraction  --- 使用多少比例的老年代后开始CMS收集，默认是68%(近似值),如果频繁发生SerialOld卡顿，应该调小，（频繁CMS回收）
- -XX:+UseCMSCompactAtFullCollection --- 在FGC时进行内存压缩整理,解决碎片
- -XX:CMSFullGCsBeforeCompaction  --- 多少次FGC之后进行压缩整理
- -XX:GCTimeRatio  --- 设置GC时间占用程序运行时间的百分比
- -XX:MaxGCPauseMillis  --- 停顿时间，是一个建议时间，GC会尝试用各种手段达到这个时间，比如减小年轻代(该参数应谨慎使用。太小的值将导致系统花费过多的时间进行垃圾回收。原因是为满足最小暂停时间，VM将设置更小的堆，以存储相对少量的对象，来提升回收速率，会导致更高频率的GC)

### G1常用参数
- -XX:+UseG1GC  --- 使用G1垃圾回收器
- -XX:MaxGCPauseMillis  --- 建议值，G1会尝试调整Young区的块数来达到这个值
- -XX:+G1HeapRegionSize  --- 分区大小，建议逐渐增大该值，1 2 4 8 16 32
	随着size增加，垃圾的存活时间更长，GC间隔更长，但每次GC的时间也会更长,该值的设置需要谨慎，需要根据机器配置，进行一定压测后来决定具体设置为多少;
- -XX:G1NewSizePercent  --- 新生代最小比例，默认为5%
- -XX:G1MaxNewSizePercent  --- 新生代最大比例，默认为60%
- -XX:GCTimeRatio  --- GC时间建议比例，G1会根据这个值调整堆空间
- -XX:ConcGCThreads --- 并行收集的线程数，G1不可以设置为和CPU核数相当,建议设置为cpu核数的一半，因为G1垃圾回收过程并不是完全STW的，如果占用所有的核，用户线程就停止执行了，相当于STW了;
- -XX:InitiatingHeapOccupancyPercent  --- 启动G1的堆空间占用比例




