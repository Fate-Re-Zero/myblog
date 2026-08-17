---
title: Spring源码(一)
date: 2022-09-04 09:00:38
tags: spring
---

### prepareRefresh(容器刷新前的准备工作)
```java
protected void prepareRefresh() {
	// 设置容器启动时间
	this.startupDate = System.currentTimeMillis();
	// 设置关闭标志位为false和活跃标志位为true
	this.closed.set(false);
	this.active.set(true);

	if (logger.isDebugEnabled()) {
		if (logger.isTraceEnabled()) {
			logger.trace("Refreshing " + this);
		}
		else {
			logger.debug("Refreshing " + getDisplayName());
		}
	}

	// Initialize any placeholder property sources in the context environment.
	initPropertySources();

	// 1.获取Environment对象,并加载当前系统属性值到Environment对象中
	getEnvironment().validateRequiredProperties();

	// 准备监听器和事件的集合对象,默认为空集合
	if (this.earlyApplicationListeners == null) {
		this.earlyApplicationListeners = new LinkedHashSet<>(this.applicationListeners);
	}
	else {
		// Reset local application listeners to pre-refresh state.
		this.applicationListeners.clear();
		this.applicationListeners.addAll(this.earlyApplicationListeners);
	}

	// Allow for the collection of early ApplicationEvents,
	// to be published once the multicaster is available...
	this.earlyApplicationEvents = new LinkedHashSet<>();
}
```

### 1.获取Environment对象,并加载当前系统属性值到Environment对象中
```java
public ConfigurableEnvironment getEnvironment() {
	if (this.environment == null) {
		// 1.创建Environment
		this.environment = createEnvironment();
	}
	return this.environment;
}

protected ConfigurableEnvironment createEnvironment() {
	return new StandardEnvironment();
}

构造StandardEnvironment对象首先会创建父类对象AbstractEnvironment
public AbstractEnvironment() {
	// 1.自定义属性源
	customizePropertySources(this.propertySources);
}
// 空方法,由字类具体实现
protected void customizePropertySources(MutablePropertySources propertySources) {
}

子类StandardEnvironment中具体实现customizePropertySources方法
public static final String SYSTEM_ENVIRONMENT_PROPERTY_SOURCE_NAME = "systemEnvironment";
	
public static final String SYSTEM_PROPERTIES_PROPERTY_SOURCE_NAME = "systemProperties";

protected void customizePropertySources(MutablePropertySources propertySources) {
	// 添加systemProperties属性源
	propertySources.addLast(
			new PropertiesPropertySource(SYSTEM_PROPERTIES_PROPERTY_SOURCE_NAME, getSystemProperties()));
	// 添加systemEnvironment属性源
	propertySources.addLast(
			new SystemEnvironmentPropertySource(SYSTEM_ENVIRONMENT_PROPERTY_SOURCE_NAME, getSystemEnvironment()));
}
```

### obtainFreshBeanFactory
1. 创建容器对象：DefaultListableBeanFactory
2. 加载xml配置文件属性到当前工厂中，
	主要属性有：
	beanDefinitionNames缓存：所有被加载到BeanFactory中的bean的beanName集合;
	beanDefinitionMap缓存：所有被加载到BeanFactory中的bean的beanName和BeanDefinition映射;
	aliasMap缓存：所有被加载到BeanFactory中的bean的beanName和别名映射;

```java
protected ConfigurableListableBeanFactory obtainFreshBeanFactory() {
	// 1.刷新BeanFactory，由AbstractRefreshableApplicationContext实现
	refreshBeanFactory();
	// 2.拿到刷新后的BeanFactory
	return getBeanFactory();
}


protected final void refreshBeanFactory() throws BeansException {
	// 1.判断是否已经存在BeanFactory，如果存在则先销毁、关闭该BeanFactory
	if (hasBeanFactory()) {
		destroyBeans();
		closeBeanFactory();
	}
	try {
		// 2.创建一个新的BeanFactory
		DefaultListableBeanFactory beanFactory = createBeanFactory();
		beanFactory.setSerializationId(getId());
		customizeBeanFactory(beanFactory);
		// 3.加载bean定义,并将相关bean信息添加到beanDefinitionNames,beanDefinitionMap,aliasMap中
		loadBeanDefinitions(beanFactory);
		this.beanFactory = beanFactory;
	}
	catch (IOException ex) {
		throw new ApplicationContextException("I/O error parsing bean definition source for " + getDisplayName(), ex);
	}
}
```

### prepareBeanFactory
1. 为BeanFactory设置一些属性,增强BeanFactory
```java
protected void prepareBeanFactory(ConfigurableListableBeanFactory beanFactory) {
	// Tell the internal bean factory to use the context's class loader etc.
	beanFactory.setBeanClassLoader(getClassLoader());
	beanFactory.setBeanExpressionResolver(new StandardBeanExpressionResolver(beanFactory.getBeanClassLoader()));
	beanFactory.addPropertyEditorRegistrar(new ResourceEditorRegistrar(this, getEnvironment()));

	// Configure the bean factory with context callbacks.
	beanFactory.addBeanPostProcessor(new ApplicationContextAwareProcessor(this));
	beanFactory.ignoreDependencyInterface(EnvironmentAware.class);
	beanFactory.ignoreDependencyInterface(EmbeddedValueResolverAware.class);
	beanFactory.ignoreDependencyInterface(ResourceLoaderAware.class);
	beanFactory.ignoreDependencyInterface(ApplicationEventPublisherAware.class);
	beanFactory.ignoreDependencyInterface(MessageSourceAware.class);
	beanFactory.ignoreDependencyInterface(ApplicationContextAware.class);

	// BeanFactory interface not registered as resolvable type in a plain factory.
	// MessageSource registered (and found for autowiring) as a bean.
	beanFactory.registerResolvableDependency(BeanFactory.class, beanFactory);
	beanFactory.registerResolvableDependency(ResourceLoader.class, this);
	beanFactory.registerResolvableDependency(ApplicationEventPublisher.class, this);
	beanFactory.registerResolvableDependency(ApplicationContext.class, this);

	// Register early post-processor for detecting inner beans as ApplicationListeners.
	beanFactory.addBeanPostProcessor(new ApplicationListenerDetector(this));

	// Detect a LoadTimeWeaver and prepare for weaving, if found.
	if (beanFactory.containsBean(LOAD_TIME_WEAVER_BEAN_NAME)) {
		beanFactory.addBeanPostProcessor(new LoadTimeWeaverAwareProcessor(beanFactory));
		// Set a temporary ClassLoader for type matching.
		beanFactory.setTempClassLoader(new ContextTypeMatchClassLoader(beanFactory.getBeanClassLoader()));
	}

	// Register default environment beans.
	if (!beanFactory.containsLocalBean(ENVIRONMENT_BEAN_NAME)) {
		beanFactory.registerSingleton(ENVIRONMENT_BEAN_NAME, getEnvironment());
	}
	if (!beanFactory.containsLocalBean(SYSTEM_PROPERTIES_BEAN_NAME)) {
		beanFactory.registerSingleton(SYSTEM_PROPERTIES_BEAN_NAME, getEnvironment().getSystemProperties());
	}
	if (!beanFactory.containsLocalBean(SYSTEM_ENVIRONMENT_BEAN_NAME)) {
		beanFactory.registerSingleton(SYSTEM_ENVIRONMENT_BEAN_NAME, getEnvironment().getSystemEnvironment());
	}
}
```

### postProcessBeanFactory
1. Spring提供的模板方法，常用的spring扩展点之一,常被称之为后置处理器
```java
protected void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) {
}
```

### invokeBeanFactoryPostProcessors
1. 实例化所有的BeanFactoryPostProcessors对象并注册到容器中;
