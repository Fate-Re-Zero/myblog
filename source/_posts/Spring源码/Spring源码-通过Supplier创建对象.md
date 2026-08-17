---
title: Spring源码-通过Supplier创建对象
date: 2022-09-13 15:35:38
tags: spring
---

### 通过Supplier创建对象
理解:在spring实例化之前,可以通过RootBeanDefinition.getInstanceSupplier()获取Supplier<?>进行对象创建,Supplier
只是BeanDefinition的一个属性值

1.获取Supplier实例
```java
protected BeanWrapper createBeanInstance(String beanName, RootBeanDefinition mbd, 
	@Nullable Object[] args) {
	// Make sure bean class is actually resolved at this point.
	Class<?> beanClass = resolveBeanClass(mbd, beanName);

	if (beanClass != null && !Modifier.isPublic(beanClass.getModifiers()) && 
	!mbd.isNonPublicAccessAllowed()) {
		throw new BeanCreationException(mbd.getResourceDescription(), beanName,
				"Bean class isn't public, and non-public access not allowed: " 
				+ beanClass.getName());
	}

	// 获取Supplier实例
	Supplier<?> instanceSupplier = mbd.getInstanceSupplier();
	if (instanceSupplier != null) {
		return obtainFromSupplier(instanceSupplier, beanName);
	}
}
```

2.调用instanceSupplier的get()方法获取实例,这里get()方法调用的是函数式接口Supplier的内部方法
```java
protected BeanWrapper obtainFromSupplier(Supplier<?> instanceSupplier, String beanName) {
	Object instance;

	String outerBean = this.currentlyCreatedBean.get();
	this.currentlyCreatedBean.set(beanName);
	try {
		instance = instanceSupplier.get();
	}
	finally {
		if (outerBean != null) {
			this.currentlyCreatedBean.set(outerBean);
		}
		else {
			this.currentlyCreatedBean.remove();
		}
	}

	if (instance == null) {
		instance = new NullBean();
	}
	BeanWrapper bw = new BeanWrapperImpl(instance);
	initBeanWrapper(bw);
	return bw;
}
```

```java
@FunctionalInterface
public interface Supplier<T> {

    T get();
}
```

### 代码案例
```java
public class CreateSupplier {

    public static User createUser(){
        return new User("张三");
    }
}
```

```java
public class User {

    private String username;

    public User() {
    }

    public User(String username) {
        this.username = username;
    }
}
```

```java
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.beans.factory.config.BeanFactoryPostProcessor;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.beans.factory.support.GenericBeanDefinition;

public class UserBeanFactoryPostProcessor implements BeanFactoryPostProcessor {

    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) 
    throws BeansException {
        BeanDefinition user = beanFactory.getBeanDefinition("user");
        GenericBeanDefinition beanDefinition = (GenericBeanDefinition) user;
        beanDefinition.setInstanceSupplier(CreateSupplier::createUser);
        beanDefinition.setBeanClass(User.class);
    }
}
```

```java
 <bean id="user" class="com.lixiang.supplier.User"></bean>
 <bean class="com.lixiang.supplier.UserBeanFactoryPostProcessor"></bean>
```

```java
MyClassPathXmlApplicationContext ac = new MyClassPathXmlApplicationContext("applicationContext.xml");
User bean = ac.getBean(User.class);
System.out.println(bean.getUsername());
```

### 总结
BeanFactory是抽象出一个接口规范, 创建的对象必须通过getObject方法获取,而Supplier只是BeanDefinition的一个属性值,
可以随便定义创建对象的方法;