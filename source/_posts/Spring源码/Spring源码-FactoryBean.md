---
title: Spring源码-FactoryBean
date: 2022-09-13 13:28:38
tags: spring
---

### BeanFactory与FactoryBean

理解: 如果使用BeanFactory接口,那么必须遵守springbean的生命周期,从实例化,到初始化,到invokeAwareMethod.invokeInitMethod,postProcessBeforeInitialization, postProcessAfterInitialization, 此流程非常复杂且麻烦，如果需要一种更加便捷简单的方式创建，就可以使用FactoryBean接口,不需要遵循此创建顺序;

### FactoryBean接口
```java
public interface FactoryBean<T> {

	String OBJECT_TYPE_ATTRIBUTE = "factoryBeanObjectType";

	// 获取实例对象
	@Nullable
	T getObject() throws Exception;

	// 返回对象类型
	@Nullable
	Class<?> getObjectType();

	// 返回对象是否为单例
	default boolean isSingleton() {
		return true;
	}

}
```

### FactoryBean的执行流程
1.在对象实例化之前，需要检查bean是否为FactoryBean;
```java
public boolean isFactoryBean(String name) throws NoSuchBeanDefinitionException {
	// 1.拿到真正的beanName（去掉&前缀、解析别名）
	String beanName = transformedBeanName(name);
	// 2.尝试从缓存获取Bean实例对象
	Object beanInstance = getSingleton(beanName, false);
	if (beanInstance != null) {
		// 3.beanInstance存在，则直接判断类型是否为FactoryBean
		return (beanInstance instanceof FactoryBean);
	}
	// No singleton instance found -> check bean definition.
	if (!containsBeanDefinition(beanName) && getParentBeanFactory() instanceof ConfigurableBeanFactory) {
		// No bean definition found in this factory -> delegate to parent.
		// 5.如果缓存中不存在此beanName && 父beanFactory是ConfigurableBeanFactory，则调用父BeanFactory判断是否为FactoryBean
		return ((ConfigurableBeanFactory) getParentBeanFactory()).isFactoryBean(name);
	}
	// 6.通过MergedBeanDefinition来检查beanName对应的Bean是否为FactoryBean
	return isFactoryBean(beanName, getMergedLocalBeanDefinition(beanName));
}
```

2.获取实现了FacotryBean接口的bean对象,正常执行Bean的创建过程创建该对象并放入缓存, 对象的key为& + bean的名称, value为实现了FactoryBean的实例对象;
```java
if (isFactoryBean(beanName)) {
	// 5.1 通过beanName获取FactoryBean实例
	// 通过getBean(&beanName)拿到的是FactoryBean本身；通过getBean(beanName)拿到的是FactoryBean创建的Bean实例
	Object bean = getBean(FACTORY_BEAN_PREFIX + beanName);
}
```

3.从容器获取实现了FactoryBean接口的实例对象的getObject方法返回的对象,直接使用通过Bean的名称即可获取到该对象;
```java
ApplicationContext context = new ClassPathXmlApplicationContext("test.xml");
Car car=(Car)context.getBean("car");
System.out.println(car);
```

```java
@Override
public Object getBean(String name) throws BeansException {
	// 获取name对应的bean实例，如果不存在，则创建一个
	return doGetBean(name, null, null, false);
}
```

4.这里从缓存中获取到的是实现了FactoryBean接口的实例对象而不是getObject返回的实例对象
```java
protected <T> T doGetBean(String name, @Nullable Class<T> requiredType, @Nullable Object[] args, boolean  typeCheckOnly) throws BeansException {
	// 1.解析beanName，主要是解析别名、去掉FactoryBean的前缀“&”
	String beanName = transformedBeanName(name);
	Object bean;

	// Eagerly check singleton cache for manually registered singletons.
	// 2.尝试从缓存中获取beanName对应的实例
	Object sharedInstance = getSingleton(beanName);
	// 3.如果beanName的实例存在于缓存中
	if (sharedInstance != null && args == null) {
		if (logger.isTraceEnabled()) {
			if (isSingletonCurrentlyInCreation(beanName)) {
				logger.trace("Returning eagerly cached instance of singleton bean '" + beanName +
						"' that is not fully initialized yet - a consequence of a circular reference");
			}
			else {
				logger.trace("Returning cached instance of singleton bean '" + beanName + "'");
			}
		}
		// 3.1 返回beanName对应的实例对象（主要用于FactoryBean的特殊处理，普通Bean会直接返回sharedInstance本身）
		bean = getObjectForBeanInstance(sharedInstance, name, beanName, null);
	}
}
```

5.检查对象是否为FactoryBean并强转为FactoryBean
```java
protected Object getObjectForBeanInstance(Object beanInstance, String name, String beanName, @Nullable RootBeanDefinition mbd) {
	// Don't let calling code try to dereference the factory if the bean isn't a factory.
	// 1.如果name以“&”为前缀，但是beanInstance不是FactoryBean，则抛异常
	if (BeanFactoryUtils.isFactoryDereference(name)) {
		// 2.1 如果beanInstance不是FactoryBean（也就是普通bean），则直接返回beanInstance
		// 2.2 如果beanInstance是FactoryBean，并且name以“&”为前缀，则直接返回beanInstance（以“&”为前缀代表想获取的是FactoryBean本身）
		if (beanInstance instanceof NullBean) {
			return beanInstance;
		}
		if (!(beanInstance instanceof FactoryBean)) {
			throw new BeanIsNotAFactoryException(beanName, beanInstance.getClass());
		}
		if (mbd != null) {
			mbd.isFactoryBean = true;
		}
		return beanInstance;
	}

	// Now we have the bean instance, which may be a normal bean or a FactoryBean.
	// If it's a FactoryBean, we use it to create a bean instance, unless the
	// caller actually wants a reference to the factory.
	if (!(beanInstance instanceof FactoryBean)) {
		return beanInstance;
	}

	// 3.走到这边，代表beanInstance是FactoryBean，但name不带有“&”前缀，表示想要获取的是FactoryBean创建的对象实例
	Object object = null;
	if (mbd != null) {
		// 4.如果mbd为空，则尝试从factoryBeanObjectCache缓存中获取该FactoryBean创建的对象实例
		mbd.isFactoryBean = true;
	}
	else {
		object = getCachedObjectForFactoryBean(beanName);
	}
	if (object == null) {
		// Return bean instance from factory.
		// 5.只有beanInstance是FactoryBean才能走到这边，因此直接强转
		FactoryBean<?> factory = (FactoryBean<?>) beanInstance;
		// Caches object obtained from FactoryBean if it is a singleton.
		if (mbd == null && containsBeanDefinition(beanName)) {
			// 6.mbd为空，但是该bean的BeanDefinition在缓存中存在，则获取该bean的MergedBeanDefinition
			mbd = getMergedLocalBeanDefinition(beanName);
		}
		// 7.mbd是否是合成的（这个字段比较复杂，mbd正常情况都不是合成的，也就是false，有兴趣的可以自己查阅资料看看）
		boolean synthetic = (mbd != null && mbd.isSynthetic());
		// 8.从FactoryBean获取对象实例
		object = getObjectFromFactoryBean(factory, beanName, !synthetic);
	}
	// 9.返回对象实例
	return object;
}
```

6.尝试从factoryBeanObjectCache缓存中获取, 获取不到调用getObject方法返回对象并放入缓存
```java
protected Object getObjectFromFactoryBean(FactoryBean<?> factory, String beanName, boolean shouldPostProcess) {
	// 1.如果是单例，并且已经存在于单例对象缓存中
	if (factory.isSingleton() && containsSingleton(beanName)) {
		synchronized (getSingletonMutex()) {
			// 2.从FactoryBean创建的单例对象的缓存中获取该bean实例
			Object object = this.factoryBeanObjectCache.get(beanName);
			if (object == null) {
				// 3.调用FactoryBean的getObject方法获取对象实例
				object = doGetObjectFromFactoryBean(factory, beanName);
				// Only post-process and store if not put there already during getObject() call above
				// (e.g. because of circular reference processing triggered by custom getBean calls)
				Object alreadyThere = this.factoryBeanObjectCache.get(beanName);
				// 4.如果该beanName已经在缓存中存在，则将object替换成缓存中的
				if (alreadyThere != null) {
					object = alreadyThere;
				}
				else {
					if (shouldPostProcess) {
						if (isSingletonCurrentlyInCreation(beanName)) {
							// Temporarily return non-post-processed object, not storing it yet..
							return object;
						}
						beforeSingletonCreation(beanName);
						try {
							// 5.对bean实例进行后置处理，执行所有已注册的BeanPostProcessor的postProcessAfterInitialization方法
							object = postProcessObjectFromFactoryBean(object, beanName);
						}
						catch (Throwable ex) {
							throw new BeanCreationException(beanName,
									"Post-processing of FactoryBean's singleton object failed", ex);
						}
						finally {
							afterSingletonCreation(beanName);
						}
					}
					// 6.将beanName和object放到factoryBeanObjectCache缓存中
					if (containsSingleton(beanName)) {
						this.factoryBeanObjectCache.put(beanName, object);
					}
				}
			}
			// 7.返回object对象实例
			return object;
		}
	}
	else {
		// 8.调用FactoryBean的getObject方法获取对象实例
		Object object = doGetObjectFromFactoryBean(factory, beanName);
		if (shouldPostProcess) {
			try {
				// 9.对bean实例进行后置处理，执行所有已注册的BeanPostProcessor的postProcessAfterInitialization方法
				object = postProcessObjectFromFactoryBean(object, beanName);
			}
			catch (Throwable ex) {
				throw new BeanCreationException(beanName, "Post-processing of FactoryBean's object failed", ex);
			}
		}
		// 10.返回object对象实例
		return object;
	}
}
```

7.调用FactoryBean的getObject方法获取实例对象
```java
private Object doGetObjectFromFactoryBean(FactoryBean<?> factory, String beanName) throws BeanCreationException {
	Object object;
	try {
		// 1.调用FactoryBean的getObject方法获取bean对象实例
		if (System.getSecurityManager() != null) {
			AccessControlContext acc = getAccessControlContext();
			try {
				// 1.1 带有权限验证的
				object = AccessController.doPrivileged((PrivilegedExceptionAction<Object>) factory::getObject, acc);
			}
			catch (PrivilegedActionException pae) {
				throw pae.getException();
			}
		}
		else {
			// 1.2 不带权限
			object = factory.getObject();
		}
	}
	catch (FactoryBeanNotInitializedException ex) {
		throw new BeanCurrentlyInCreationException(beanName, ex.toString());
	}
	catch (Throwable ex) {
		throw new BeanCreationException(beanName, "FactoryBean threw exception on object creation", ex);
	}

	// Do not accept a null value for a FactoryBean that's not fully
	// initialized yet: Many FactoryBeans just return null then.
	// 2.getObject返回的是空值，并且该FactoryBean正在初始化中，则直接抛异常，不接受一个尚未完全初始化的FactoryBean的getObject返回的空值
	if (object == null) {
		if (isSingletonCurrentlyInCreation(beanName)) {
			throw new BeanCurrentlyInCreationException(
					beanName, "FactoryBean which is currently in creation returned null from getObject");
		}
		object = new NullBean();
	}
	// 3.返回创建好的bean对象实例
	return object;
}
```

### 代码案例
```java
@Data
public class Car {

    private String name;
    private String brand;
    private Integer speed;
}
```

```java
import org.springframework.beans.factory.FactoryBean;

public class CarFactoryBean implements FactoryBean<Car> {

    private String carInfo;

    public String getCarInfo() {
        return carInfo;
    }

    public void setCarInfo(String carInfo) {
        this.carInfo = carInfo;
    }

    @Override
    public Car getObject() throws Exception {

        Car car = new Car();
        String[] split = carInfo.split(",");
        car.setName(split[0]);
        car.setBrand(split[1]);
        car.setSpeed(Integer.valueOf(split[2]));
        return  car;
    }

    @Override
    public Class<?> getObjectType() {
        return Car.class;
    }

    @Override
    public boolean isSingleton() {
        return true;
    }
}
```

```java
<bean id="car" class="com.lixiang.test.CarFactoryBean" >
    <property name="carInfo" value="大黄蜂,玛莎拉蒂,250"></property>
</bean>
```

```java
public class MyTest {
    public static void main(String[] args) {
        ApplicationContext context = new ClassPathXmlApplicationContext("test.xml");
        Car car=(Car)context.getBean("car");
        System.out.println(car);
    }
}
```


