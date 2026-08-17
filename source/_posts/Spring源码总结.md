---
title: Spring源码总结
date: 2022-06-18 20:30:38
tags:
---

我们会在 web.xml 中配置 ContextLoaderListener 监听器，当 Tomcat 启动时，会触发 ContextLoaderListener 的 contextInitialized 方法，但是在执行该方法前，会去先执行父类的静态代码块
```java
static {
		// Load default strategy implementations from properties file.
		// This is currently strictly internal and not meant to be customized
		// by application developers.
		try {
			// 1.根据 DEFAULT_STRATEGIES_PATH（ContextLoader.properties） 和 ContextLoader.class 构建 ClassPathResource，
			// path在这边为相对路径，全路径为：org.springframework.web.context.ContextLoader.properties
			ClassPathResource resource = new ClassPathResource(DEFAULT_STRATEGIES_PATH, ContextLoader.class);
			// 2.加载resource的属性，在这边我们拿到了默认的WebApplicationContext，即：XmlWebApplicationContext
			defaultStrategies = PropertiesLoaderUtils.loadProperties(resource);
		}
		catch (IOException ex) {
			throw new IllegalStateException("Could not load 'ContextLoader.properties': " + ex.getMessage());
		}
	}
```
这段代码主要作用是，根据spring-web工程下的ContextLoader.properties文件构建ClassPathResource，然后根据文件内容初始化ContextLoader的defaultStrategies属性；

接下来就回去执行ContextLoaderListener的contextInitialized方法：
```java
/**
 * Initialize the root web application context.
 */
@Override
public void contextInitialized(ServletContextEvent event) {
	initWebApplicationContext(event.getServletContext());
}

public WebApplicationContext initWebApplicationContext(ServletContext servletContext) {
		// 1.校验WebApplicationContext 是否已经初始化过，如果已经初始化，则抛出异常
		if (servletContext.getAttribute(WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE) != null) {
			throw new IllegalStateException(
					"Cannot initialize context because there is already a root application context present - " +
					"check whether you have multiple ContextLoader* definitions in your web.xml!");
		}

		servletContext.log("Initializing Spring root WebApplicationContext");
		Log logger = LogFactory.getLog(ContextLoader.class);
		if (logger.isInfoEnabled()) {
			logger.info("Root WebApplicationContext: initialization started");
		}
		long startTime = System.currentTimeMillis();

		try {
			// Store context in local instance variable, to guarantee that
			// it is available on ServletContext shutdown.
			if (this.context == null) {
				// 2.创建一个WebApplicationContext并保存到context属性
				this.context = createWebApplicationContext(servletContext);
			}
			if (this.context instanceof ConfigurableWebApplicationContext) {
				ConfigurableWebApplicationContext cwac = (ConfigurableWebApplicationContext) this.context;
				if (!cwac.isActive()) {
					// The context has not yet been refreshed -> provide services such as
					// setting the parent context, setting the application context id, etc
					if (cwac.getParent() == null) {
						// The context instance was injected without an explicit parent ->
						// determine parent for root web application context, if any.
						ApplicationContext parent = loadParentContext(servletContext);
						cwac.setParent(parent);
					}
					// 3.配置和刷新web应用上下文
					configureAndRefreshWebApplicationContext(cwac, servletContext);
				}
			}
			servletContext.setAttribute(WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE, this.context);

			ClassLoader ccl = Thread.currentThread().getContextClassLoader();
			if (ccl == ContextLoader.class.getClassLoader()) {
				currentContext = this.context;
			}
			else if (ccl != null) {
				currentContextPerThread.put(ccl, this.context);
			}

			if (logger.isInfoEnabled()) {
				long elapsedTime = System.currentTimeMillis() - startTime;
				logger.info("Root WebApplicationContext initialized in " + elapsedTime + " ms");
			}

			return this.context;
		}
		catch (RuntimeException | Error ex) {
			logger.error("Context initialization failed", ex);
			servletContext.setAttribute(WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE, ex);
			throw ex;
		}
	}
```
该方法的核心内容在第3步：配置和刷新web应用上下文(见下面代码块)，
其中第2步：创建一个WebApplicationContext并保存到context属性会用到defaultStrategies属性


```java
protected void configureAndRefreshWebApplicationContext(ConfigurableWebApplicationContext wac, ServletContext sc) {
		// 1.如果应用上下文id是原始默认值，则根据相关信息生成一个更有用的
		if (ObjectUtils.identityToString(wac).equals(wac.getId())) {
			// The application context id is still set to its original default value
			// -> assign a more useful id based on available information
			// 1.1 从servletContext中解析初始化参数contextId(可以在web.xml中配置)
			String idParam = sc.getInitParameter(CONTEXT_ID_PARAM);
			if (idParam != null) {
				// 1.1.1 如果idParam不为空, 则设置为wac的Id属性
				wac.setId(idParam);
			}
			else {
				// Generate default id...
				// 1.1.2 如果idParam为空, 则生成默认的id, 例如: org.springframework.web.context.WebApplicationContext:
				wac.setId(ConfigurableWebApplicationContext.APPLICATION_CONTEXT_ID_PREFIX +
						ObjectUtils.getDisplayString(sc.getContextPath()));
			}
		}

		// 2.为应用上下文设置servletContext
		wac.setServletContext(sc);
		// 3.从servletContext中解析初始化参数contextConfigLocation(可以在web.xml中配置, 这个参数一般我们都会设置)
		String configLocationParam = sc.getInitParameter(CONFIG_LOCATION_PARAM);
		if (configLocationParam != null) {
			// 4.设置wac的configLocations属性值为configLocationParam,还会初始化环境属性
			wac.setConfigLocation(configLocationParam);
		}

		// The wac environment's #initPropertySources will be called in any case when the context
		// is refreshed; do it eagerly here to ensure servlet property sources are in place for
		// use in any post-processing or initialization that occurs below prior to #refresh
		ConfigurableEnvironment env = wac.getEnvironment();
		if (env instanceof ConfigurableWebEnvironment) {
			// 5.初始化属性源(主要是将servletContextInitParams的占位类替换成sc)
			((ConfigurableWebEnvironment) env).initPropertySources(sc, null);
		}
		// 6.自定义上下文
		customizeContext(sc, wac);
		// 7.应用上下文的刷新
		wac.refresh();
	}
```
4.设置 wac 的 configLocations 属性值为 configLocationParam，

5.初始化属性源，见代码块11详解。

6.自定义上下文，见代码块12详解。

7.应用上下文的刷新，IoC 核心内容

总结：初始化IOC容器之前的一些操作：
	1.根据spring-web工程下的ContextLoader.properties文件构建ClassPathResource，然后根据文件内容初始化ContextLoader的defaultStrategies属性；
	2.根据defaultStrategies属性创建WebApplicationContext，这里创建的是XmlWebApplicationContext并强转为ConfigurableWebApplicationContext;
	3.将web.xml配置文件中的属性都初始化到ConfigurableWebApplicationContext中，创建并初始化环境属性；
	4.将ServletContext替换掉ConfigurableWebEnvironment环境中的占位符；
	5.自定义上下文，开发者可以自己创建ApplicationContextInitializer的实现类，重写initialize，向ConfigurableApplicationContext上下文中添加自己的逻辑实现；并在web.xml中定义 contextInitializerClasses 或 globalInitializerClasses 参数，参数值为自定义实现类的全路径；此处是Spring提供的自定义应用上下文 ConfigurableApplicationContext 的扩展点；
	6.执行应用上下文的刷新，也就是核心方法refresh()方法；

obtainFreshBeanFactory方法：
总结：
	1.创建DefaultListableBeanFactory；
	2.为指定BeanFactory创建XmlBeanDefinitionReader；
	3.获取配置文件路径集合，遍历文件路径；（就是为了将配置文件封装成Resource对象和获取到inputStream）
		3.1.根据路径拿到该路径下所有符合的配置文件，并封装成Resource集合;
		3.2.遍历Resource集合，构建EncodedResource，并获取到Resource的inputStream
		3.3.将inputStream封装成org.xml.sax.InputSource
	4.解析配置文件，注册Bean；
		4.1.根据inputSource和resource加载XML文件，并封装成Document
			4.1.1.获取XML配置文件的验证模式。XML文件的验证模式是用来保证XML文件的正确性，常见的验证模式有两种：DTD和XSD
		4.2.根据返回的Document注册Bean信息(对配置文件的解析，核心逻辑)
			4.2.1.根据resource创建一个XmlReaderContext,用于存放解析时会用到的一些上下文信息,并且会去构建NamespaceHandlerResolver,DefaultNamespaceHandlerResolver的handlerMappingsLocation属性会使用默认的值"META-INF/spring.handlers"，
			并且这边有个重要的属性 handlerMappings，handlerMappings 用于存放命名空间和该命名空间handler类的映射
			4.2.2.根据Document的节点信息和XmlReaderContext构建BeanDefinitionParserDelegate，并赋值给DefaultBeanDefinitionDocumentReader的delegate属性；
			4.2.3.解析处理profile属性,profile属性主要用于多环境开发,可以在配置文件中同时写上多套配置来适用于开发环境、测试环境、生产环境，这样可以方便的进行切换开发、部署环境，最常用的就是更换不同的数据库。具体使用哪个环境在 web.xml 中通过参数 spring.profiles.active 来配置；
			4.2.4.解析前处理, 留给子类实现；
			4.2.5.解析并注册bean定义;
				4.2.5.1.遍历root的子节点列表;
				4.2.5.1.如果节点的命名空间是 Spring 默认的命名空间，则走 parseDefaultElement(ele, delegate) 方法进行解析，例如最常见的：<bean>;
				4.2.5.2.如果节点的命名空间不是 Spring 默认的命名空间，也就是自定义命名空间，则走 delegate.parseCustomElement(ele) 方法进行解析，例如常见的：<context:component-scan/>、<aop:aspectj-autoproxy/>;
			4.2.6.解析后处理, 留给子类实现；

parseDefaultElement(ele, delegate)总结：
	先将 xml 中的 bean 配置信息进行了解析，并构建了 AbstractBeanDefinition（GenericBeanDefinition） 对象来存放所有解析出来的属性。
	然后，我们将 AbstractBeanDefinition 、beanName、aliasesArray 构建成 BeanDefinitionHolder 对象并返回。
	最后，我们通过 BeanDefinitionHolder 将 BeanDefinition 和 beanName 注册到 BeanFactory 中，也就是存放到缓存中。
	执行完 parseDefaultElement 方法，我们得到了两个重要的缓存：
		beanDefinitionNames 缓存；
		beanDefinitionMap 缓存；
		aliasMap缓存；
	beanDefinitionMap：DefaultListableBeanFactory的属性,用于存放bean name与BeanDefinition的映射关系
```java
/** Map of bean definition objects, keyed by bean name. */
private final Map<String, BeanDefinition> beanDefinitionMap = new ConcurrentHashMap<>(256);
```
	beanDefinitionNames:DefaultListableBeanFactory的属性,用于存放bean name集合
```java
/** List of bean definition names, in registration order. */
private volatile List<String> beanDefinitionNames = new ArrayList<>(256);
```
	aliasMap:SimpleAliasRegistry的属性，用于别名和beanName的映射
```java
/** Map from alias to canonical name. */
private final Map<String, String> aliasMap = new ConcurrentHashMap<>(16);
```

BeanDefinition是什么：
	BeanDefinition主要是用来描述Bean，存储Bean的相关信息，主要包括：Bean的属性、是否单例、延迟加载、Bean的名称、构造方法等；
		1.BeanDefinition继承了AttributeAccessor，具备处理属性的能力；
		2.BeanDefinition继承了BeanMetadataElement，可以持有Bean元数据元素，作用是可以持有XML文件的一个bean标签对应的Object；
