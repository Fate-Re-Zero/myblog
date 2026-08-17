---
title: Java技术总结
date: 2021-07-29 18:42:38
tags:
---

### 基础题目一（反射）
```java
public class TestString {

    public static void main(String[] args) throws Exception {
        String s = new String("abc");
        // 在这之间可以添加N行代码，但必须保证s引用的指向不变，最终将输出变成abcd

        // 1.使用stringBuilder追加d字符串，这种方式不可取，stringBuilder底层其实是创建了一个新的String数组，并没有改变现有字符串的值
        // StringBuilder stringBuilder = new StringBuilder(s);
        // stringBuilder.append("d");

        // 2.replace方法底层实际上是new了一个StringBuffer,然后返回这个StringBuffer的toString,这种方式也是不可取的
        // s.replace("abc", "abcd");

        // 3.使用暴力反射修改String对象的value值
        Field value = s.getClass().getDeclaredField("value");
        value.setAccessible(true);
        value.set(s, "abcd".toCharArray());
        System.out.println(s);
    }
}
```

### 基础题目二（字符串相关）
```java
public class TestString2 {

    public static void main(String[] args) {
        // 1.new String 是会生成两个对象，一个是abc这个字符串常量对象，字符串常量对象是放在字符串常量池里的
        // 另外一个是String 对象，它是放在堆里面的
        String s1 = new String("abc");
        // s2这边会去字符串常量池里面找，找到了abc就会赋值给s2,所以说这是两个不同的对象
        String s2 = "abc";
        // s1 == s2 ? true or false
        // System.out.println(s1 == s2)   false;

        // 2.String对象的intern方法，首先会检查字符串常量池中是否存在abc,如果存在则返回该常量的引用，如果不存在，
        // 则把abc添加到字符串常量池中，并返回该字符串常量的引用
        String s3 = s1.intern();
        // s2 == s3 ? true or false
        // System.out.println(s2 == s3)   true;
    }
}
```

### 基础题目三（Integer相关）
```java
public class TestInteger {

    public static void main(String[] args) {
        // Integer内部是有一个IntegerCache的静态内部类，这个内中的静态代码块会初始化-128到127的所有数据放到该静态内部类的cache数组中
        // 所以-128到127之间的所有值直接从cache数组中取值，在这个区间之外的值都是重新new的
        Integer i1 = 100;
        Integer i2 = 100;
        // i1 == i2 ? true or false
        // System.out.println(i1 == i2)  true;
        Integer i3 = 128;
        Integer i4 = 128;
        // i3 == i4 ? true or false
        // System.out.println(i3 == i4)  false;
    }
}
```

### 基础题目四（StringBuffer和StringBuilder的区别）
```java
public class TestStringBufferAndStringBuilder {

    public static void main(String[] args) {
        // 1.String, StringBuffer, StringBuilder的区别是什么
        String s = "abc";
        // String是不可变的，如果尝试去修改，会生成一个新的字符串对象，StringBuffer和StringBuilder是可变的
        s = "abcd";
        // StringBuffer是线程安全的，StringBuilder是线程不安全的，单线程环境下StringBuilder效率更高
        StringBuilder stringBuilder = new StringBuilder(s);
        stringBuilder.append("d");
        // stringBuffer底层方法都是加上了synchronized关键字的
        StringBuffer stringBuffer = new StringBuffer(s);
        stringBuffer.append("d");
    }
}
```

### 基础题目五（ArrayList和LinkList相关）
```java
public class TestArrayAndLinkedList {

    public static void main(String[] args) {
        // ArrayList和LinkedList的区别
        // 两者都实现了List接口，但是LinkList额外的实现了Deque接口，所以linkedList还可以当作队列来使用
        // ArrayList底层是使用数组来实现，LinkedList底层是使用链表来实现的
        // 数组查询块，增删慢； 链表增删块，查询慢，一定是这样吗？
        // 数组添加数据的时候还会涉及到扩容的一个问题，但是链表是没有这个问题
        // 当在固定下标添加数据的时候，ArrayList虽然能够快速获取到下标，但是它内部的copy方法实际上是一个将该下标后面的元素都向后移动一位
        // 而且还有可能会产生扩容操作，所以说元素的移动加上可能的扩容效率不一定高于linkedList
        // linkedList在指定位置添加元素，只需要改变一些指针的指向，但是它也有一个非常耗性能的操作就是它只知道头节点，需要去遍历链表查找这个指定下标
        List<String> arrayList = new ArrayList<String>();
        arrayList.add("1");
        arrayList.add(3, "1");

        List<String> linkedList = new LinkedList<String>();
        linkedList.add("1");
        linkedList.add(3, "1");
    }
}
```

### 基础题目六（CopyOnWriteList相关）
```java
public class TestCopyOnWriteArrayList {

    public static void main(String[] args) {
        // 多线程环境下，当一个线程正在向List尾节点插入数据，但是动作还没有完成，此时另一个线程也向尾结点插入数据，
        // 此时就会出现后插入的数据覆盖了先插入的数据，出现了线程不安全问题
        ArrayList<String> arrayList = new ArrayList<String>();
        arrayList.add("li");
        arrayList.add("xiang");

        // CopyOnWriteArrayList的执行add方法首先会去获取ReentrantLock这个独占锁，多个线程调用add方法时，只有一个线程会获取到该锁，
        // 其他线程会被阻塞，直到锁被释放，这样保证了整个add过程是一个原子性的操作，而且在添加元素时，首先复制了一个原数组的一个快照，在
        // 快照上添加元素，而不是直接在原数组上进行添加，然后使用新数组替换原数组，并在返回数组前释放锁
        // CopyOnWriteArrayList读操作是在原数组上进行没有锁机制的，所以读操作效率非常快的
        // CopyOnWriteArrayList在写操作时来读取数据，从而提高了读取数据的性能，因此适合读多写少的场景
        // CopyOnWriteArrayList因为在写操作的时候会去复制一份原数组，所以比较占内存，同时也会出现读取的数据不是最新的数据，所以不适合
        // 实时性要求很高的场景
        CopyOnWriteArrayList<String> copyOnWriteArrayList = new CopyOnWriteArrayList<String>();
        copyOnWriteArrayList.add("li");
        copyOnWriteArrayList.add("xiang");
    }
}
```
