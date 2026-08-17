---
title: Java容器类
date: 2022-07-25 21:00:38
tags:
---

###HashTable

###SynchronizedMap

###HashMap

###ConcurrentHashMap

###Vector

###ConcurrentLinkedQueue

###CopyOnWriteList

###ConcurrentSkipListMap

###LinkedBlockingQueue
	理解：无界队列，它的put(obj)方法如果容器满了会阻塞住，take()方法如果队列空了会阻塞住，使用这两个方法可以实现生产者，
	消费者模型；add()方法如果添加失败会报异常，offer()添加失败会返回false,天生的就是对线程友好的生产者消费者模型；
```java
public class MyLinkedBlockingQueue {

	static BlockingQueue<String> strs = new LinkedBlockingQueue<>();

	static Random r = new Random();

	public static void main(String[] args) {
		new Thread(() -> {
			for (int i = 0; i < 100; i++) {
				try {
					strs.put("a" + i); // 如果容器满了，会阻塞住(这里的阻塞是通过ReentrantLock的Condition实现的)
					TimeUnit.MILLISECONDS.sleep(r.nextInt(1000));
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
		}, "p1").start();

		for (int i = 0; i < 5; i++) {
			new Thread(() -> {
				for (;;) {
					try {
						System.out.println(Thread.currentThread().getName() + " take -" + strs.take()); // 如果队列空了会阻塞住
					} catch (InterruptedException e) {
						e.printStackTrace();
					}
				}
			}, "c" + i).start();
		}
	}
}
```

###ArrayBlockingQueue
	理解：有界队列，它的put(obj)方法如果容器满了会阻塞住，add()方法队列满了会报异常
```java
public class T06_ArrayBlockingQueue {

	static BlockingQueue<String> strs = new ArrayBlockingQueue<>(10);

	static Random r = new Random();

	public static void main(String[] args) throws InterruptedException {
		for (int i = 0; i < 10; i++) {
			strs.put("a" + i);
		}
		
		//strs.put("aaa"); // 如果容器满了会阻塞住
		//strs.add("aaa");
		//strs.offer("aaa");
		strs.offer("aaa", 1, TimeUnit.SECONDS); // 阻塞一秒尝试添加
		// List和Queue主要的区别在于添加put(),take(),offer()这些对线程友好的，或者阻塞，或者时间等待的方法
		
		System.out.println(strs);
	}
}
```

###DelayQueue
	理解：可以用于按照时间排序的任务调度，自定义Task实现Delayed接口,重写compareTo方法来实现任务排序；
```java
public class MyDelayQueue {

	static BlockingQueue<MyTask> tasks = new DelayQueue<>();

	static Random r = new Random();
	
	static class MyTask implements Delayed {
		String name;
		long runningTime;
		
		MyTask(String name, long rt) {
			this.name = name;
			this.runningTime = rt;
		}

		@Override
		public int compareTo(Delayed o) {
			if(this.getDelay(TimeUnit.MILLISECONDS) < o.getDelay(TimeUnit.MILLISECONDS))
				return -1;
			else if(this.getDelay(TimeUnit.MILLISECONDS) > o.getDelay(TimeUnit.MILLISECONDS)) 
				return 1;
			else 
				return 0;
		}

		@Override
		public long getDelay(TimeUnit unit) {
			
			return unit.convert(runningTime - System.currentTimeMillis(), TimeUnit.MILLISECONDS);
		}
		
		@Override
		public String toString() {
			return name + " " + runningTime;
		}
	}

	public static void main(String[] args) throws InterruptedException {
		long now = System.currentTimeMillis();
		MyTask t1 = new MyTask("t1", now + 1000);
		MyTask t2 = new MyTask("t2", now + 2000);
		MyTask t3 = new MyTask("t3", now + 1500);
		MyTask t4 = new MyTask("t4", now + 2500);
		MyTask t5 = new MyTask("t5", now + 500);
		
		tasks.put(t1);
		tasks.put(t2);
		tasks.put(t3);
		tasks.put(t4);
		tasks.put(t5);
		
		System.out.println(tasks);
		
		for(int i=0; i<5; i++) {
			System.out.println(tasks.take());
		}
	}
}
```

###SynchronousQueue
	理解：容量为0，主要用于实现数据传递，a线程向SynchronousQueue中put数据，b线程从Queue中取数据,如果没有线程取数据，
	a线程会一直阻塞住；
```java
public class MySynchronusQueue { // 容量为0
	public static void main(String[] args) throws InterruptedException {
		BlockingQueue<String> strs = new SynchronousQueue<>();
		
		new Thread(()->{
			try {
				System.out.println(strs.take());
			} catch (Exception e) {
				e.printStackTrace();
			}
		}).start();

		new Thread(()->{
			try {
				strs.put("aaa");
			} catch (Exception e) {
				e.printStackTrace();
			}
		}).start();

//		strs.put("aaa"); //阻塞等待其他线程取数据
//		strs.put("bbb");
//		strs.add("aaa");
		System.out.println(strs.size());
	}
}
```

###LinkedTransferQueue
	理解：生产者会一直阻塞直到所添加到队列的元素被某一个消费者所消费（不仅仅是添加到队列里就完事）,当我们不想生产者过度生产消息时，TransferQueue可能非常有用,生产完消息就阻塞住，等消费者消费完再生产
```java
public class T09_TransferQueue {
	public static void main(String[] args) throws InterruptedException {
		LinkedTransferQueue<String> strs = new LinkedTransferQueue<>();
		
		new Thread(() -> {
			try {
				System.out.println(strs.take());
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}).start();
		
		strs.transfer("aaa");
	}
}
```