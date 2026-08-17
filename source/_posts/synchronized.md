---
title: synchronized
date: 2022-07-19 21:00:38
tags:
---

###synchronized关键字：
	理解：
	（1）JMM使用了临界区（加锁）来保证程序的顺序执行，但是在临界区内是允许出现指令重排的（JMM不允许临界区内的代码“逸出”到临界区之外，那样会破坏监视器的语义）。
	（2）只有获取到synchronized锁对象的线程才可以执行临界区的代码；
	1.注意：不是锁住某段代码块，而是对某个对象加锁，只有持有这个对象锁的线程才可以执行synchronized代码块；
	2.synchronized(object),锁对象不要用String常量，Integer,Long
```java
public class MySynchronized {

    private int count = 10;

    public void m() {
        synchronized (this) {
            count --;
            System.out.println(Thread.currentThread().getName() + "count:" + count);
        }
    }

    // 与上面方法等价
    public synchronized void n() {
        count --;
        System.out.println(Thread.currentThread().getName() + "count:" + count);
    }

    // 这里等同于synchronized(MySynchronized.class)
    public synchronized static void k() {
        System.out.println(Thread.currentThread().getName());
    }

}
```

###关于synchronized的代码案例
```java
// synchronized可以保证原子性和可见性
public class T implements Runnable {
	// 不需要volatile
	private int count = 10;

	// synchronized可以保证原子性和可见性
	public synchronized void run() {
		count--;
		System.out.println(Thread.currentThread().getName() + " count = " + count);
	}
	
	public static void main(String[] args) {
		for(int i = 0; i < 5; i++) {
			T t = new T();
			new Thread(t, "THREAD" + i).start();
		}
	}
	
}

// 加了synchronized的m1方法不影响m2的执行
public class T {

	public synchronized void m1() { 
		System.out.println(Thread.currentThread().getName() + " m1 start...");
		try {
			Thread.sleep(10000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		System.out.println(Thread.currentThread().getName() + " m1 end");
	}
	
	public void m2() {
		try {
			Thread.sleep(5000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		System.out.println(Thread.currentThread().getName() + " m2 ");
	}
	
	public static void main(String[] args) {
		T t = new T();
		new Thread(t::m1, "t1").start();
		new Thread(t::m2, "t2").start();
	}
}

// 锁的可重入
public class T {
	synchronized void m1() {
		System.out.println("m1 start");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		m2();
		System.out.println("m1 end");
	}
	
	synchronized void m2() {
		try {
			TimeUnit.SECONDS.sleep(2);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		System.out.println("m2");
	}

	public static void main(String[] args) {
		new T().m1();
	}
}

// 在父类与子类中锁依然是可重入的
public class T {
	synchronized void m() {
		System.out.println("m start");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		System.out.println("m end");
	}
	
	public static void main(String[] args) {
		new TT().m();
	}
	
}

class TT extends T {
	@Override
	synchronized void m() {
		System.out.println("child m start");
		super.m();
		System.out.println("child m end");
	}
}
```

###锁和异常
	当持有锁的线程发生异常，会释放锁，导致其他线程持有锁，造成数据不一致
```java
public class T {
	int count = 0;
	synchronized void m() {
		System.out.println(Thread.currentThread().getName() + " start");
		while(true) {
			count ++;
			System.out.println(Thread.currentThread().getName() + " count = " + count);
			try {
				TimeUnit.SECONDS.sleep(1);
				
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			if(count == 5) {
				int i = 1/0; //此处抛出异常，锁将被释放，要想不被释放，可以在这里进行catch，然后让循环继续
				System.out.println(i);
			}
		}
	}
	
	public static void main(String[] args) {
		T t = new T();
		Runnable r = new Runnable() {
			@Override
			public void run() {
				t.m();
			}
		};
		new Thread(r, "t1").start();
		
		try {
			TimeUnit.SECONDS.sleep(3);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		
		new Thread(r, "t2").start();
	}
	
}
```

###synchronized的底层实现

自旋锁是在用户态去解决锁的问题，它不经过内核态，因此它在加锁和解锁要比经过内核态的效率高；
加锁代码块执行时间比较短，且线程数比较少，用自旋锁；
加锁代码块执行时间比较长，或者线程比较多，用系统锁（向操作申请的锁）;

###synchronized锁升级


###synchronized优化
1.锁粒度的控制
```java
public class FineCoarseLock {
	
	int count = 0;

	synchronized void m1() {
		//do sth need not sync
		try {
			TimeUnit.SECONDS.sleep(2);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		//业务逻辑中只有下面这句需要sync，这时不应该给整个方法上锁
		count ++;
		
		//do sth need not sync
		try {
			TimeUnit.SECONDS.sleep(2);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
	
	void m2() {
		//do sth need not sync
		try {
			TimeUnit.SECONDS.sleep(2);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		//业务逻辑中只有下面这句需要sync，这时不应该给整个方法上锁
		//采用细粒度的锁，可以使线程争用时间变短，从而提高效率
		synchronized(this) {
			count ++;
		}
		//do sth need not sync
		try {
			TimeUnit.SECONDS.sleep(2);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
}
```
2.synchronized锁的对象需要final修饰
```java
public class SyncSameObject {
	
	/*final*/ Object o = new Object();

	void m() {
		synchronized(o) {
			while(true) {
				try {
					TimeUnit.SECONDS.sleep(1);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
				System.out.println(Thread.currentThread().getName());
				
				
			}
		}
	}
	
	public static void main(String[] args) {
		SyncSameObject t = new SyncSameObject();
		new Thread(t::m, "t1").start();
		
		try {
			TimeUnit.SECONDS.sleep(3);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		Thread t2 = new Thread(t::m, "t2");

		t.o = new Object();
		
		t2.start();
		
	}
}
```
3.不要使用基本数据类型作为锁对象
```java
public class DoNotLockString {
	
	String s1 = "Hello";
	String s2 = "Hello";

	void m1() {
		synchronized(s1) {
			
		}
	}
	
	void m2() {
		synchronized(s2) {
			
		}
	}
}
```

