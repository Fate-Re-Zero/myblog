---
title: Spring源码-通过FactoryMethod创建对象
date: 2022-09-13 16:59:38
tags: spring
---

### 通过FactoryMethod创建对象
理解: spring提供了通过静态工厂和实例工厂两种方式来创建对象;

```java
protected BeanWrapper createBeanInstance(String beanName, RootBeanDefinition mbd, @Nullable Object[] args) {
	// Make sure bean class is actually resolved at this point.
	Class<?> beanClass = resolveBeanClass(mbd, beanName);

	if (beanClass != null && !Modifier.isPublic(beanClass.getModifiers()) && !mbd.isNonPublicAccessAllowed()) {
		throw new BeanCreationException(mbd.getResourceDescription(), beanName,
				"Bean class isn't public, and non-public access not allowed: " + beanClass.getName());
	}

	// 获取Supplier实例
	Supplier<?> instanceSupplier = mbd.getInstanceSupplier();
	if (instanceSupplier != null) {
		return obtainFromSupplier(instanceSupplier, beanName);
	}

	// 获取FactoryMethod名称
	if (mbd.getFactoryMethodName() != null) {
		return instantiateUsingFactoryMethod(beanName, mbd, args);
	}
}
```

```java
protected BeanWrapper instantiateUsingFactoryMethod(
		String beanName, RootBeanDefinition mbd, @Nullable Object[] explicitArgs) {

	return new ConstructorResolver(this).instantiateUsingFactoryMethod(beanName, mbd, explicitArgs);
}
```

```java
public BeanWrapper instantiateUsingFactoryMethod(
		String beanName, RootBeanDefinition mbd, @Nullable Object[] explicitArgs) {

	BeanWrapperImpl bw = new BeanWrapperImpl();
	this.beanFactory.initBeanWrapper(bw);

	Object factoryBean;
	Class<?> factoryClass;
	boolean isStatic;

	String factoryBeanName = mbd.getFactoryBeanName();
	if (factoryBeanName != null) {
		if (factoryBeanName.equals(beanName)) {
			throw new BeanDefinitionStoreException(mbd.getResourceDescription(), beanName,
					"factory-bean reference points back to the same bean definition");
		}
		factoryBean = this.beanFactory.getBean(factoryBeanName);
		if (mbd.isSingleton() && this.beanFactory.containsSingleton(beanName)) {
			throw new ImplicitlyAppearedSingletonException();
		}
		factoryClass = factoryBean.getClass();
		isStatic = false;
	}
	else {
		// It's a static factory method on the bean class.
		if (!mbd.hasBeanClass()) {
			throw new BeanDefinitionStoreException(mbd.getResourceDescription(), beanName,
					"bean definition declares neither a bean class nor a factory-bean reference");
		}
		factoryBean = null;
		factoryClass = mbd.getBeanClass();
		isStatic = true;
	}

	Method factoryMethodToUse = null;
	ArgumentsHolder argsHolderToUse = null;
	Object[] argsToUse = null;

	if (explicitArgs != null) {
		argsToUse = explicitArgs;
	}
	else {
		Object[] argsToResolve = null;
		synchronized (mbd.constructorArgumentLock) {
			factoryMethodToUse = (Method) mbd.resolvedConstructorOrFactoryMethod;
			if (factoryMethodToUse != null && mbd.constructorArgumentsResolved) {
				// Found a cached factory method...
				argsToUse = mbd.resolvedConstructorArguments;
				if (argsToUse == null) {
					argsToResolve = mbd.preparedConstructorArguments;
				}
			}
		}
		if (argsToResolve != null) {
			argsToUse = resolvePreparedArguments(beanName, mbd, bw, factoryMethodToUse, argsToResolve, true);
		}
	}

	if (factoryMethodToUse == null || argsToUse == null) {
		// Need to determine the factory method...
		// Try all methods with this name to see if they match the given arguments.
		factoryClass = ClassUtils.getUserClass(factoryClass);

		List<Method> candidates = null;
		if (mbd.isFactoryMethodUnique) {
			if (factoryMethodToUse == null) {
				factoryMethodToUse = mbd.getResolvedFactoryMethod();
			}
			if (factoryMethodToUse != null) {
				candidates = Collections.singletonList(factoryMethodToUse);
			}
		}
		if (candidates == null) {
			candidates = new ArrayList<>();
			Method[] rawCandidates = getCandidateMethods(factoryClass, mbd);
			for (Method candidate : rawCandidates) {
				if (Modifier.isStatic(candidate.getModifiers()) == isStatic && mbd.isFactoryMethod(candidate)) {
					candidates.add(candidate);
				}
			}
		}

		if (candidates.size() == 1 && explicitArgs == null && !mbd.hasConstructorArgumentValues()) {
			Method uniqueCandidate = candidates.get(0);
			if (uniqueCandidate.getParameterCount() == 0) {
				mbd.factoryMethodToIntrospect = uniqueCandidate;
				synchronized (mbd.constructorArgumentLock) {
					mbd.resolvedConstructorOrFactoryMethod = uniqueCandidate;
					mbd.constructorArgumentsResolved = true;
					mbd.resolvedConstructorArguments = EMPTY_ARGS;
				}
				bw.setBeanInstance(instantiate(beanName, mbd, factoryBean, uniqueCandidate, EMPTY_ARGS));
				return bw;
			}
		}

		if (candidates.size() > 1) {  // explicitly skip immutable singletonList
			candidates.sort(AutowireUtils.EXECUTABLE_COMPARATOR);
		}

		ConstructorArgumentValues resolvedValues = null;
		boolean autowiring = (mbd.getResolvedAutowireMode() == AutowireCapableBeanFactory.AUTOWIRE_CONSTRUCTOR);
		int minTypeDiffWeight = Integer.MAX_VALUE;
		Set<Method> ambiguousFactoryMethods = null;

		int minNrOfArgs;
		if (explicitArgs != null) {
			minNrOfArgs = explicitArgs.length;
		}
		else {
			// We don't have arguments passed in programmatically, so we need to resolve the
			// arguments specified in the constructor arguments held in the bean definition.
			if (mbd.hasConstructorArgumentValues()) {
				ConstructorArgumentValues cargs = mbd.getConstructorArgumentValues();
				resolvedValues = new ConstructorArgumentValues();
				minNrOfArgs = resolveConstructorArguments(beanName, mbd, bw, cargs, resolvedValues);
			}
			else {
				minNrOfArgs = 0;
			}
		}

		LinkedList<UnsatisfiedDependencyException> causes = null;

		for (Method candidate : candidates) {
			int parameterCount = candidate.getParameterCount();

			if (parameterCount >= minNrOfArgs) {
				ArgumentsHolder argsHolder;

				Class<?>[] paramTypes = candidate.getParameterTypes();
				if (explicitArgs != null) {
					// Explicit arguments given -> arguments length must match exactly.
					if (paramTypes.length != explicitArgs.length) {
						continue;
					}
					argsHolder = new ArgumentsHolder(explicitArgs);
				}
				else {
					// Resolved constructor arguments: type conversion and/or autowiring necessary.
					try {
						String[] paramNames = null;
						ParameterNameDiscoverer pnd = this.beanFactory.getParameterNameDiscoverer();
						if (pnd != null) {
							paramNames = pnd.getParameterNames(candidate);
						}
						argsHolder = createArgumentArray(beanName, mbd, resolvedValues, bw,
								paramTypes, paramNames, candidate, autowiring, candidates.size() == 1);
					}
					catch (UnsatisfiedDependencyException ex) {
						if (logger.isTraceEnabled()) {
							logger.trace("Ignoring factory method [" + candidate + "] of bean '" + beanName + "': " + ex);
						}
						// Swallow and try next overloaded factory method.
						if (causes == null) {
							causes = new LinkedList<>();
						}
						causes.add(ex);
						continue;
					}
				}

				int typeDiffWeight = (mbd.isLenientConstructorResolution() ?
						argsHolder.getTypeDifferenceWeight(paramTypes) : argsHolder.getAssignabilityWeight(paramTypes));
				// Choose this factory method if it represents the closest match.
				if (typeDiffWeight < minTypeDiffWeight) {
					factoryMethodToUse = candidate;
					argsHolderToUse = argsHolder;
					argsToUse = argsHolder.arguments;
					minTypeDiffWeight = typeDiffWeight;
					ambiguousFactoryMethods = null;
				}
				// Find out about ambiguity: In case of the same type difference weight
				// for methods with the same number of parameters, collect such candidates
				// and eventually raise an ambiguity exception.
				// However, only perform that check in non-lenient constructor resolution mode,
				// and explicitly ignore overridden methods (with the same parameter signature).
				else if (factoryMethodToUse != null && typeDiffWeight == minTypeDiffWeight &&
						!mbd.isLenientConstructorResolution() &&
						paramTypes.length == factoryMethodToUse.getParameterCount() &&
						!Arrays.equals(paramTypes, factoryMethodToUse.getParameterTypes())) {
					if (ambiguousFactoryMethods == null) {
						ambiguousFactoryMethods = new LinkedHashSet<>();
						ambiguousFactoryMethods.add(factoryMethodToUse);
					}
					ambiguousFactoryMethods.add(candidate);
				}
			}
		}

		if (factoryMethodToUse == null || argsToUse == null) {
			if (causes != null) {
				UnsatisfiedDependencyException ex = causes.removeLast();
				for (Exception cause : causes) {
					this.beanFactory.onSuppressedException(cause);
				}
				throw ex;
			}
			List<String> argTypes = new ArrayList<>(minNrOfArgs);
			if (explicitArgs != null) {
				for (Object arg : explicitArgs) {
					argTypes.add(arg != null ? arg.getClass().getSimpleName() : "null");
				}
			}
			else if (resolvedValues != null) {
				Set<ValueHolder> valueHolders = new LinkedHashSet<>(resolvedValues.getArgumentCount());
				valueHolders.addAll(resolvedValues.getIndexedArgumentValues().values());
				valueHolders.addAll(resolvedValues.getGenericArgumentValues());
				for (ValueHolder value : valueHolders) {
					String argType = (value.getType() != null ? ClassUtils.getShortName(value.getType()) :
							(value.getValue() != null ? value.getValue().getClass().getSimpleName() : "null"));
					argTypes.add(argType);
				}
			}
			String argDesc = StringUtils.collectionToCommaDelimitedString(argTypes);
			throw new BeanCreationException(mbd.getResourceDescription(), beanName,
					"No matching factory method found: " +
					(mbd.getFactoryBeanName() != null ?
						"factory bean '" + mbd.getFactoryBeanName() + "'; " : "") +
					"factory method '" + mbd.getFactoryMethodName() + "(" + argDesc + ")'. " +
					"Check that a method with the specified name " +
					(minNrOfArgs > 0 ? "and arguments " : "") +
					"exists and that it is " +
					(isStatic ? "static" : "non-static") + ".");
		}
		else if (void.class == factoryMethodToUse.getReturnType()) {
			throw new BeanCreationException(mbd.getResourceDescription(), beanName,
					"Invalid factory method '" + mbd.getFactoryMethodName() +
					"': needs to have a non-void return type!");
		}
		else if (ambiguousFactoryMethods != null) {
			throw new BeanCreationException(mbd.getResourceDescription(), beanName,
					"Ambiguous factory method matches found in bean '" + beanName + "' " +
					"(hint: specify index/type/name arguments for simple parameters to avoid type ambiguities): " +
					ambiguousFactoryMethods);
		}

		if (explicitArgs == null && argsHolderToUse != null) {
			mbd.factoryMethodToIntrospect = factoryMethodToUse;
			argsHolderToUse.storeCache(mbd, factoryMethodToUse);
		}
	}

	bw.setBeanInstance(instantiate(beanName, mbd, factoryBean, factoryMethodToUse, argsToUse));
	return bw;
}
```

### 代码案例
```java
@Data
public class Person {
    private int id;
    private String name;
    private int age;
    private String gender;
}
```

```java
public class PersonInstanceFactory {
    public Person getPerson(String name){
        Person person = new Person();
        person.setId(1);
        person.setName(name);
        return person;
    }
}
```

```java
public class PersonStaticFactory {

    public static Person getPerson(String name){
        Person person = new Person();
        person.setId(1);
        person.setName(name);
        return person;
    }
}
```

```java
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
    <bean id="person5" class="com.lixiang.factoryMethod.PersonStaticFactory" factory-method="getPerson">
        <!--constructor-arg：可以为方法指定参数-->
        <constructor-arg value="lisi"></constructor-arg>
    </bean>
    <bean id="personInstanceFactory" class="com.lixiang.factoryMethod.PersonInstanceFactory"></bean>
    <!--
    factory-bean:指定使用哪个工厂实例
    factory-method:指定使用哪个工厂实例的方法
    -->
    <bean id="person6" class="com.lixiang.factoryMethod.Person" factory-bean="personInstanceFactory" factory-method="getPerson">
        <constructor-arg value="wangwu"></constructor-arg>
    </bean>
</beans>
```

```java
public class Test {
    public static void main(String[] args) {
        MyClassPathXmlApplicationContext ac = new MyClassPathXmlApplicationContext("factoryMethod.xml");
    }
}
```

