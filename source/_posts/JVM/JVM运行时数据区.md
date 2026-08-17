---
title: JVM运行时数据区
date: 2022-08-6 17:52:38
tags: JVM
---

### Program Counter(程序计数器)

### JVM stacks(JVM栈，用于存放栈帧)

### native method stacks(本地方法栈)

### Heap(堆)

### method area(方法区，用于存储class结构) ---include---> run-time constant pool
1. Perm Space是HotSpot在Java1.8之前方法区具体的实现；
	字符串常量位于PermSpace 
	FGC不会清理 
	大小启动的时候指定，不能变
2. Meta Space是HotSpot在Java1.8及以后方法区具体的实现；
	字符串常量位于堆 
	会触发FGC清理 
	不设定的话，最大就是物理内存

### Direct Memory(直接内存) 
- 用户空间JVM可以直接去访问内核空间的内存(OS管理的内存),NIO,提高效率，实现零拷贝

### 栈帧(Frame)
- 每个方法对应一个栈帧
	1.Local Variable Table(本地变量表)
	2.Operand Stack(操作数栈)
	3.Dynamic Linking(动态链接)：动态链接是一个将符号引用解析为直接引用的过程
	4.return address(返回值地址)：a() -> b()，方法a调用了方法b, b方法的返回值放在的地方，以及方法继续执行的地址