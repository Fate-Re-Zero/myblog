---
title: Java线程池
date: 2022-07-28 21:00:38
tags:
---

###Callable

###Future

###FUtureTask

###CompletableFuture

###Executors
	理解：线程池的工厂，可以构建各种线程池SingleThreadPool，newFixedThreadPool等

###线程池
	理解：线程主要分为两种：
	ThreadPoolExecutor
	ForkJoinPool: 分解汇总任务; 用很少的线程执行很多的任务(子任务)TPE做不到先执行子任务; CPU密集型;

###自定义线程池
	核心线程数：
	最大线程数：
	非核心线程最大空闲时间：
	时间单位：
	阻塞队列：
	自定义的ThreadFactory: 自定义创建线程的规范：指定线程组名称，指定线程名称，指定线程为非守护线程，
		指定线程的优先级，好处是为了排查问题更加方便，使用jstack命令可以很容易排查出问题；
	拒绝策略：JDK默认提供了四种，拒绝策略是可以自定义的
		Abort:抛异常
		Discard:扔掉，不抛异常
		DiscardOldest:扔掉排队时间最久的
		CallerRuns:调用者处理任务

	线程池执行任务的过程：先到来的任务由核心线程执行，当核心线程都在执行任务，来的新任务进入阻塞队列，当阻塞队列满了，再来的新任务则启动新线程来执行，当线程数达到最大线程数时，执行拒绝策略；

###不使用JDK自己提供的线程池的原因
	1.无法自定义拒绝策略；
	2.核心线程数，最大线程数等参数需要根据机器本身配置和业务本身的需要来决定的，所以自定义线程池能够更加灵活满足我们的需求；
	3.自定义线程池可以自己指定线程组名称，线程名称，更加有利于排查问题；

###SingleThreadPool
	理解：线程池里只有一个线程，能够保证任务顺序的执行；使用的默认线程工厂，默认拒绝策略；
	缺点：只有单个线程，使用的LinkedBlockingQueue作为阻塞队列
	为什么有单线程的线程池：相比较与自己创建线程，可以不用自己创建阻塞队列，池化思想有利线程资源的有效利用与生命周期管理；

###CachedPool
	理解：核心线程数为0，最大线程数为Integer的最大值，线程的最大空闲等待时间为60S,使用SynchronousQueue作为阻塞队列，
	SynchronousQueue的特点是，容量为0，当任务进入阻塞队列，如果没有其他线程处理，线程会一直阻塞住；使用的默认线程工厂，默认拒绝策略；
	缺点：最大线程为Integer的最大值，如果任务很多，会创建非常多的线程，可能导致服务器资源耗尽产生OOM;
	使用场景：不推荐使用，要使用的话，会在任务数量的多少随着时间的变化不稳定的时候，但是还需要保证任务不会堆积的时候可以使用

###FixedThreadPool
	理解：自己指定精确的线程数，核心线程数与最大线程数相等，也就是全是核心线程，使用的LinkedBlockingQueue作为阻塞队列，使用的默认线程工厂，默认拒绝策略；
	缺点：如果任务很多，任务队列的任务会堆积的非常多，最大为Integer的最大值，可能导致服务器占用大量内存而导致OOM;
	使用场景：不推荐使用，要使用的话，会在任务数量的多少随着时间的比较稳定的时候，但是还需要保证任务不会堆积的时候可以使用

###到底该使用那种线程池
	不推荐使用JDK提供的线程池，一般情况下都是自定义线程池

###线程池的线程该定义为多少
	线程池中线程过多：大量线程会竞争稀缺的处理器和内存资源，浪费大量的时间在上下文切换上；
	线程池中线程过少：会导致我们的服务器应用处理器的一些核可能无法充分利用到；
	线程数多少与处理器的利用率之比可以使用下面的公式进行估算：
	N(threads) = N(cpu) * U(cpu) * (1 + W/C)
	其中：
	N(cpu)是处理器的核的数目，可以通过Runtime.getRuntime().availableProcessors()得到
	U(cpu)是期望的CPU利用率(该值应该介于0和1之间)
	W/C是等待时间与计算时间的比率

###ScheduledPool
	理解：一般用于定时任务的场景，实现定时任务的其他方式还有quartz，cron

###并发与并行(concurrent与parallel)
	并发指任务的提交，并行指任务的执行
	并行是并发的子集
	理解：并发指非常多的任务线程同时提交任务到服务器程序，单个cpu核也可以去执行这些任务，但需要不断地做线程上下文切换，多核就可以并行的去执行这些任务；任务并行处理的时候才能真正的提高效率；

###自定义线程池拒绝策略
```java
public class MyRejectedHandler {
    public static void main(String[] args) {
        ExecutorService service = new ThreadPoolExecutor(4, 4,
                0, TimeUnit.SECONDS, new ArrayBlockingQueue<>(6),
                Executors.defaultThreadFactory(),
                new MyHandler());
    }

    static class MyHandler implements RejectedExecutionHandler {

        @Override
        public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
            int count = 3;
            //try 3 times
            while (count > 0) {
                if(executor.getQueue().size() < 6) {
                    //try put again();
                }
                count--;
            }
            // 打印日志
            // 将任务存到kafka 或者mysql，看具体的业务
        }
    }
}
```

###自定义线程工厂
	1.利用Spring 框架提供的轮子 CustomizableThreadFactory
```java
ThreadFactory springFactory = new CustomizableThreadFactory("spring-pool-");
ExecutorService exec = new ThreadPoolExecutor(1, 1,
        0L, TimeUnit.MILLISECONDS,
        new ArrayBlockingQueue<Runnable>(100), springFactory);
```

	2.使用Google 开源框架guava提供的 ThreadFactoryBuilder 可以快速给线程池里的线程设置有意义的名字
```java
ThreadFactory guavaFactory = new ThreadFactoryBuilder().setNameFormat("guava-pool-").build();
ExecutorService exec = new ThreadPoolExecutor(1, 1,
        0L, TimeUnit.MILLISECONDS,
        new LinkedBlockingQueue<Runnable>(100),guavaFactory );
```

	3.Apache commons-lang3 提供的 BasicThreadFactory
```java
ThreadFactory basicFactory = new BasicThreadFactory.Builder().namingPattern("basicFactory-pool-").build();
ExecutorService exec = new ThreadPoolExecutor(1, 1,
        0L, TimeUnit.MILLISECONDS,
        new LinkedBlockingQueue<Runnable>(100),basicFactory );
```

	4.自己定义TreadFactory, 实现ThreadFactory接口,定义自己的线程名称
```java
public class MyThreadFactory implements ThreadFactory {
    private static final AtomicInteger poolNumber = new AtomicInteger(1);
    private final ThreadGroup group;
    private final AtomicInteger threadNumber = new AtomicInteger(1);
    private final String namePrefix;

    MyThreadFactory() {
        SecurityManager s = System.getSecurityManager();
        group = (s != null) ? s.getThreadGroup() :
                Thread.currentThread().getThreadGroup();
        //此处只修改了一下名字前缀
        namePrefix = "业务名称-" +
                poolNumber.getAndIncrement() +
                "-thread-";
        System.out.println("--->"+namePrefix);
    }

    @Override
    public Thread newThread(Runnable r) {
        Thread t = new Thread(group, r,
                namePrefix + threadNumber.getAndIncrement(),
                0);
        if (t.isDaemon()){
            t.setDaemon(false);
        }
        if (t.getPriority() != Thread.NORM_PRIORITY){
            t.setPriority(Thread.NORM_PRIORITY);
        }
        return t;
    }
}
```

###WorkStealingPool

###ForkJoinPool

###Disruptor
	核心：内部使用的环形buffer来存放还没来得及处理的任务，这个环形buffer使用数组来实现，让数组的尾内存地址指向头内存地址，
	使用数组的好处：
	1.数组的遍历速度是要高于链表的，所以这里作者没有选择ConcurrentLinkedQueue来作为任务队列
	2.不需要像阻塞队列一样需要去维护头指针和尾指针，环形只需要维护一个指针指向下一个可用的位置
	3.使用EventFactory提前为buffer中的每个位置创建好了Event对象，当向里面添加任务时，只要去修改Event的属性，只需要覆盖，不需要清除旧的数据，大大的减少了GC的频率；




