---
title: Spring源码-BeanFactoryPostProcessor
date: 2022-09-15 09:18:38
tags: spring
---

### BeanFactoryPostProcessor
理解：BeanFactoryPostProcessor的执行与容器已经创建完毕,xml中的bean定义信息已经解析完毕,但bean还没有实例化阶段,该接口的作用主要在于添加或者修改容器中的bean定义信息,我们日常开发中使用@Configuration,@Bean,@Component,@ComponentScan,@Import,@ImportSource这些注解向容器中添加bean,其实Spring是借助与一个非常重要的类ConfigurationClassPostProcessor,该类实现了BeanDefinitionRegistryPostProcessor,在postProcessBeanDefinitionRegistry中通过解析该bean是否标注了这些注解,进而添加使用注解引入的bean的定义信息到beanFactory
```java
@FunctionalInterface
public interface BeanFactoryPostProcessor {

	/**
	 * Modify the application context's internal bean factory after its standard
	 * initialization. All bean definitions will have been loaded, but no beans
	 * will have been instantiated yet. This allows for overriding or adding
	 * properties even to eager-initializing beans.
	 * @param beanFactory the bean factory used by the application context
	 * @throws org.springframework.beans.BeansException in case of errors
	 */
	void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException;

}

```

### BeanDefinitionRegistryPostProcessor
理解：主要用于对容器中的Beandefinition信息进行添加和修改
```java
public interface BeanDefinitionRegistryPostProcessor extends BeanFactoryPostProcessor {

	/**
	 * Modify the application context's internal bean definition registry after its
	 * standard initialization. All regular bean definitions will have been loaded,
	 * but no beans will have been instantiated yet. This allows for adding further
	 * bean definitions before the next post-processing phase kicks in.
	 * @param registry the bean definition registry used by the application context
	 * @throws org.springframework.beans.BeansException in case of errors
	 */
	void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) throws BeansException;

}
```

### spring如何实现注入注解标记的bean
当spring需要开启注解扫描时,需要在xml文件配置<context:component-scan base-package="" annotation-config="true" />加上context标签并配置要扫描的包,这个标签中其实有一个默认属性annotation-config,默认值为true,所以我们一般不会去主动设置它,当容器启动,去解析xml文件的时候,当解析到context标签, 会将标注了@Component注解的BeanDefinition信息注册到容器,并根据annotatiion-config的值是否为true判断是否将ConfigurationClassPostProcessor, AutowiredAnnotationBeanPostProcessor, CommonAnnotationBeanPostProcessor等后置处理器的BeanDefinition信息到容器,主要用于后续将标注了@Configuration,@Bean,@Component,@ComponentScan,@Import,@ImportSource等注解bean的BeanDefinition信息添加到容器

#### 第一阶段,扫描包阶段

1. 注册bean的定义信息
```java
protected void doRegisterBeanDefinitions(Element root) {
	BeanDefinitionParserDelegate parent = this.delegate;
	// 构建BeanDefinitionParserDelegate
	this.delegate = createDelegate(getReaderContext(), root, parent);

	// 1.校验root节点的命名空间是否为默认的命名空间（默认命名空间http://www.springframework.org/schema/beans）
	if (this.delegate.isDefaultNamespace(root)) {
		// 2.处理profile属性
		String profileSpec = root.getAttribute(PROFILE_ATTRIBUTE);
		if (StringUtils.hasText(profileSpec)) {
			String[] specifiedProfiles = StringUtils.tokenizeToStringArray(
					profileSpec, BeanDefinitionParserDelegate.MULTI_VALUE_ATTRIBUTE_DELIMITERS);
			// We cannot use Profiles.of(...) since profile expressions are not supported
			// in XML config. See SPR-12458 for details.
			// 校验当前节点的 profile 是否符合当前环境定义的, 如果不是则直接跳过, 不解析该节点下的内容
			if (!getReaderContext().getEnvironment().acceptsProfiles(specifiedProfiles)) {
					if (logger.isDebugEnabled()) {
					logger.debug("Skipped XML bean definition file due to specified profiles [" + profileSpec +
							"] not matching: " + getReaderContext().getResource());
				}
				return;
			}
		}
	}
	// 3.解析前处理, 留给子类实现
	preProcessXml(root);
	// 4.解析并注册bean定义
	parseBeanDefinitions(root, this.delegate);
	// 5.解析后处理, 留给子类实现
	postProcessXml(root);

	this.delegate = parent;
}
```

2. 解析xml文件,context属于自定义命名空间
```java
protected void parseBeanDefinitions(Element root, BeanDefinitionParserDelegate delegate) {
	// 1.默认命名空间的处理
	if (delegate.isDefaultNamespace(root)) {
		NodeList nl = root.getChildNodes();
		// 遍历root的子节点列表
		for (int i = 0; i < nl.getLength(); i++) {
			Node node = nl.item(i);
			if (node instanceof Element) {
				Element ele = (Element) node;
				// 1.1 默认命名空间节点的处理，例如：<bean id="test" class="" />
				if (delegate.isDefaultNamespace(ele)) {
					parseDefaultElement(ele, delegate);
				}
				else {
					// 1.2 自定义命名空间节点的处理，例如：<context:component-scan/>、<aop:aspectj-autoproxy/>
					delegate.parseCustomElement(ele);
				}
			}
		}
	}
	else {
		// 2.自定义命名空间的处理
		delegate.parseCustomElement(root);
	}
}
```

3. 拿到命名空间对应的的handler
```java
public BeanDefinition parseCustomElement(Element ele) {
	return parseCustomElement(ele, null);
}

public BeanDefinition parseCustomElement(Element ele, @Nullable BeanDefinition containingBd) {
	// 1.拿到节点ele的命名空间，例如常见的:
	// <context> 节点对应命名空间: http://www.springframework.org/schema/context
	// <aop> 节点对应命名空间: http://www.springframework.org/schema/aop
	String namespaceUri = getNamespaceURI(ele);
	if (namespaceUri == null) {
		return null;
	}
	// 2.拿到命名空间对应的的handler, 例如：http://www.springframework.org/schema/context 对应 ContextNameSpaceHandler
	// 2.1 getNamespaceHandlerResolver: 拿到namespaceHandlerResolver
	// 2.2 resolve: 使用namespaceHandlerResolver解析namespaceUri, 拿到namespaceUri对应的NamespaceHandler
	NamespaceHandler handler = this.readerContext.getNamespaceHandlerResolver().resolve(namespaceUri);
	if (handler == null) {
		error("Unable to locate Spring NamespaceHandler for XML schema namespace [" + namespaceUri + "]", ele);
		return null;
	}
	// 3.使用拿到的handler解析节点（ParserContext用于存放解析需要的一些上下文信息）
	return handler.parse(ele, new ParserContext(this.readerContext, this, containingBd));
}	
```

4. 拿到对应的BeanDefinition解析器
```java
public BeanDefinition parse(Element element, ParserContext parserContext) {
	// 1.findParserForElement: 给element寻找对应的BeanDefinition解析器
	// 2.使用BeanDefinition解析器解析element节点
	BeanDefinitionParser parser = findParserForElement(element, parserContext);
	return (parser != null ? parser.parse(element, parserContext) : null);
}
```

5. 使用解析器解析出包下所有符合要求的bean, 并注册bean定义信息到容器
```java
public BeanDefinition parse(Element element, ParserContext parserContext) {
	// 1.拿到<context:component-scan>节点的base-package属性值
	String basePackage = element.getAttribute(BASE_PACKAGE_ATTRIBUTE);
	// 2.解析占位符, 例如 ${basePackage}
	basePackage = parserContext.getReaderContext().getEnvironment().resolvePlaceholders(basePackage);
	// 3.解析base-package（允许通过 ",; \t\n" 中的任一符号填写多个），例如: com.joonwhee.open.one;com.joonwhee.open.two
	String[] basePackages = StringUtils.tokenizeToStringArray(basePackage,
			ConfigurableApplicationContext.CONFIG_LOCATION_DELIMITERS);

	// Actually scan for bean definitions and register them.
	// 4.构建和配置ClassPathBeanDefinitionScanner
	ClassPathBeanDefinitionScanner scanner = configureScanner(parserContext, element);
	// 5.使用scanner在指定的basePackages包中执行扫描，返回已注册的bean定义
	Set<BeanDefinitionHolder> beanDefinitions = scanner.doScan(basePackages);
	// 6.组件注册（包括注册一些内部的注解后置处理器、触发注册事件）
	registerComponents(parserContext.getReaderContext(), beanDefinitions, element);

	return null;
}
```

6. 扫描包下所有的bean,这里主要处理了标注了@Component的bean
```java
protected Set<BeanDefinitionHolder> doScan(String... basePackages) {
	Assert.notEmpty(basePackages, "At least one base package must be specified");
	Set<BeanDefinitionHolder> beanDefinitions = new LinkedHashSet<>();
	// 1.遍历basePackages
	for (String basePackage : basePackages) {
		// 2.扫描basePackage，将符合要求的bean定义全部找出来（这边符合要求最常见的就是使用Component注解）
		Set<BeanDefinition> candidates = findCandidateComponents(basePackage);
		// 3.遍历所有候选的bean定义
		for (BeanDefinition candidate : candidates) {
			// 4.解析@Scope注解, 包括scopeName(默认为singleton，常见的还有prototype), 和proxyMode(默认不使用代理, 可选接口代理/类代理)
			ScopeMetadata scopeMetadata = this.scopeMetadataResolver.resolveScopeMetadata(candidate);
			candidate.setScope(scopeMetadata.getScopeName());
			// 5.使用beanName生成器来生成beanName
			String beanName = this.beanNameGenerator.generateBeanName(candidate, this.registry);
			if (candidate instanceof AbstractBeanDefinition) {
				// 6.进一步处理BeanDefinition对象，比如: 此bean是否可以自动装配到其他bean中
				postProcessBeanDefinition((AbstractBeanDefinition) candidate, beanName);
			}
			if (candidate instanceof AnnotatedBeanDefinition) {
				// 7.处理定义在目标类上的通用注解，包括@Lazy, @Primary, @DependsOn, @Role, @Description
				AnnotationConfigUtils.processCommonDefinitionAnnotations((AnnotatedBeanDefinition) candidate);
			}
			// 8.检查beanName是否已经注册过，如果注册过，检查是否兼容
			if (checkCandidate(beanName, candidate)) {
				// 9.将当前遍历bean的 bean定义和beanName封装成BeanDefinitionHolder
				BeanDefinitionHolder definitionHolder = new BeanDefinitionHolder(candidate, beanName);
				// 10.根据proxyMode的值(步骤4中解析), 选择是否创建作用域代理
				definitionHolder =
						AnnotationConfigUtils.applyScopedProxyMode(scopeMetadata, definitionHolder, this.registry);
				beanDefinitions.add(definitionHolder);
				// 11.注册BeanDefinition（注册到beanDefinitionMap、beanDefinitionNames、aliasMap缓存）
				registerBeanDefinition(definitionHolder, this.registry);
			}
		}
	}
	return beanDefinitions;
}
```

7. 根据component-scan标签的annotation-config属性值(默认为true), 判断是否注册处理注解的后置处理器的BeanDefinition
```java
protected void registerComponents(
		XmlReaderContext readerContext, Set<BeanDefinitionHolder> beanDefinitions, Element element) {

	Object source = readerContext.extractSource(element);
	// 1.使用注解的tagName（例如: context:component-scan）和source 构建CompositeComponentDefinition
	CompositeComponentDefinition compositeDef = new CompositeComponentDefinition(element.getTagName(), source);

	// 2.将扫描到的所有BeanDefinition添加到compositeDef的nestedComponents属性中
	for (BeanDefinitionHolder beanDefHolder : beanDefinitions) {
		compositeDef.addNestedComponent(new BeanComponentDefinition(beanDefHolder));
	}

	// Register annotation config processors, if necessary.
	boolean annotationConfig = true;
	if (element.hasAttribute(ANNOTATION_CONFIG_ATTRIBUTE)) {
		// 3.获取component-scan标签的annotation-config属性值（默认为true）
		annotationConfig = Boolean.parseBoolean(element.getAttribute(ANNOTATION_CONFIG_ATTRIBUTE));
	}
	if (annotationConfig) {
		// 4.如果annotation-config属性值为true，在给定的注册表中注册所有用于注解的Bean后置处理器
		Set<BeanDefinitionHolder> processorDefinitions =
				AnnotationConfigUtils.registerAnnotationConfigProcessors(readerContext.getRegistry(), source);
		for (BeanDefinitionHolder processorDefinition : processorDefinitions) {
			// 5.将注册的注解后置处理器的BeanDefinition添加到compositeDef的nestedComponents属性中
			compositeDef.addNestedComponent(new BeanComponentDefinition(processorDefinition));
		}
	}

	// 6.触发组件注册事件，默认实现为EmptyReaderEventListener（空实现，没有具体操作）
	readerContext.fireComponentRegistered(compositeDef);
}
```

8. 注册ConfigurationClassPostProcessor, AutowiredAnnotationBeanPostProcessor, CommonAnnotationBeanPostProcessor
等后置处理器的BeanDefinition信息到容器,这三个是Spring内部对象,他们的beanName定义信息在
```java
public static Set<BeanDefinitionHolder> registerAnnotationConfigProcessors(
		BeanDefinitionRegistry registry, @Nullable Object source) {

	DefaultListableBeanFactory beanFactory = unwrapDefaultListableBeanFactory(registry);
	if (beanFactory != null) {
		if (!(beanFactory.getDependencyComparator() instanceof AnnotationAwareOrderComparator)) {
			// 1.设置dependencyComparator属性
			beanFactory.setDependencyComparator(AnnotationAwareOrderComparator.INSTANCE);
		}
		if (!(beanFactory.getAutowireCandidateResolver() instanceof ContextAnnotationAutowireCandidateResolver)) {
			// 2.设置autowireCandidateResolver属性（设置自动注入候选对象的解析器，用于判断BeanDefinition是否为候选对象）
			beanFactory.setAutowireCandidateResolver(new ContextAnnotationAutowireCandidateResolver());
		}
	}

	Set<BeanDefinitionHolder> beanDefs = new LinkedHashSet<>(8);

	// 3.注册内部管理的用于处理@Configuration注解的后置处理器的bean
	if (!registry.containsBeanDefinition(CONFIGURATION_ANNOTATION_PROCESSOR_BEAN_NAME)) {
		RootBeanDefinition def = new RootBeanDefinition(ConfigurationClassPostProcessor.class);
		def.setSource(source);
		// 3.1 registerPostProcessor: 注册BeanDefinition到注册表中
		beanDefs.add(registerPostProcessor(registry, def, CONFIGURATION_ANNOTATION_PROCESSOR_BEAN_NAME));
	}

	// 4.注册内部管理的用于处理@Autowired、@Value、@Inject以及@Lookup注解的后置处理器的bean
	if (!registry.containsBeanDefinition(AUTOWIRED_ANNOTATION_PROCESSOR_BEAN_NAME)) {
		RootBeanDefinition def = new RootBeanDefinition(AutowiredAnnotationBeanPostProcessor.class);
		def.setSource(source);
		beanDefs.add(registerPostProcessor(registry, def, AUTOWIRED_ANNOTATION_PROCESSOR_BEAN_NAME));
	}

	// 6.注册内部管理的用于处理JSR-250注解（例如@Resource, @PostConstruct, @PreDestroy）的后置处理器的bean
	// Check for JSR-250 support, and if present add the CommonAnnotationBeanPostProcessor.
	if (jsr250Present && !registry.containsBeanDefinition(COMMON_ANNOTATION_PROCESSOR_BEAN_NAME)) {
		RootBeanDefinition def = new RootBeanDefinition(CommonAnnotationBeanPostProcessor.class);
		def.setSource(source);
		beanDefs.add(registerPostProcessor(registry, def, COMMON_ANNOTATION_PROCESSOR_BEAN_NAME));
	}

	// 7.注册内部管理的用于处理JPA注解的后置处理器的bean
	// Check for JPA support, and if present add the PersistenceAnnotationBeanPostProcessor.
	if (jpaPresent && !registry.containsBeanDefinition(PERSISTENCE_ANNOTATION_PROCESSOR_BEAN_NAME)) {
		RootBeanDefinition def = new RootBeanDefinition();
		try {
			def.setBeanClass(ClassUtils.forName(PERSISTENCE_ANNOTATION_PROCESSOR_CLASS_NAME,
					AnnotationConfigUtils.class.getClassLoader()));
		}
		catch (ClassNotFoundException ex) {
			throw new IllegalStateException(
					"Cannot load optional framework class: " + PERSISTENCE_ANNOTATION_PROCESSOR_CLASS_NAME, ex);
		}
		def.setSource(source);
		beanDefs.add(registerPostProcessor(registry, def, PERSISTENCE_ANNOTATION_PROCESSOR_BEAN_NAME));
	}

	// 8.注册内部管理的用于处理@EventListener注解的后置处理器的bean
	if (!registry.containsBeanDefinition(EVENT_LISTENER_PROCESSOR_BEAN_NAME)) {
		RootBeanDefinition def = new RootBeanDefinition(EventListenerMethodProcessor.class);
		def.setSource(source);
		beanDefs.add(registerPostProcessor(registry, def, EVENT_LISTENER_PROCESSOR_BEAN_NAME));
	}

	// 9.注册内部管理用于生产ApplicationListener对象的EventListenerFactory对象
	if (!registry.containsBeanDefinition(EVENT_LISTENER_FACTORY_BEAN_NAME)) {
		RootBeanDefinition def = new RootBeanDefinition(DefaultEventListenerFactory.class);
		def.setSource(source);
		beanDefs.add(registerPostProcessor(registry, def, EVENT_LISTENER_FACTORY_BEAN_NAME));
	}

	return beanDefs;
}
```

9. ConfigurationClassPostProcessor, AutowiredAnnotationBeanPostProcessor, CommonAnnotationBeanPostProcessor,
这三个是Spring内部对象,他们的beanName定义信息在AnnotationConfigUtils中,当开启了注解,这三个类对象将会被加载到容器;
```java
public abstract class AnnotationConfigUtils {

	public static final String CONFIGURATION_ANNOTATION_PROCESSOR_BEAN_NAME =
			"org.springframework.context.annotation.internalConfigurationAnnotationProcessor";

	public static final String CONFIGURATION_BEAN_NAME_GENERATOR =
			"org.springframework.context.annotation.internalConfigurationBeanNameGenerator";

	public static final String AUTOWIRED_ANNOTATION_PROCESSOR_BEAN_NAME =
			"org.springframework.context.annotation.internalAutowiredAnnotationProcessor";

	@Deprecated
	public static final String REQUIRED_ANNOTATION_PROCESSOR_BEAN_NAME =
			"org.springframework.context.annotation.internalRequiredAnnotationProcessor";

	public static final String COMMON_ANNOTATION_PROCESSOR_BEAN_NAME =
			"org.springframework.context.annotation.internalCommonAnnotationProcessor";

	public static final String PERSISTENCE_ANNOTATION_PROCESSOR_BEAN_NAME =
			"org.springframework.context.annotation.internalPersistenceAnnotationProcessor";

	private static final String PERSISTENCE_ANNOTATION_PROCESSOR_CLASS_NAME =
			"org.springframework.orm.jpa.support.PersistenceAnnotationBeanPostProcessor";

	public static final String EVENT_LISTENER_PROCESSOR_BEAN_NAME =
			"org.springframework.context.event.internalEventListenerProcessor";

	public static final String EVENT_LISTENER_FACTORY_BEAN_NAME =
			"org.springframework.context.event.internalEventListenerFactory";
}
```

![](/images/spring/BeanDefinition继承关系图.jpg)

#### 第二阶段,调用处理注解的后置处理器阶段
1. 容器创建完成，调用所有的BeanFactoryPostProcessor
```java
protected void invokeBeanFactoryPostProcessors(ConfigurableListableBeanFactory beanFactory) {
	PostProcessorRegistrationDelegate.invokeBeanFactoryPostProcessors(beanFactory, getBeanFactoryPostProcessors());

	// Detect a LoadTimeWeaver and prepare for weaving, if found in the meantime
	// (e.g. through an @Bean method registered by ConfigurationClassPostProcessor)
	if (beanFactory.getTempClassLoader() == null && beanFactory.containsBean(LOAD_TIME_WEAVER_BEAN_NAME)) {
		beanFactory.addBeanPostProcessor(new LoadTimeWeaverAwareProcessor(beanFactory));
		beanFactory.setTempClassLoader(new ContextTypeMatchClassLoader(beanFactory.getBeanClassLoader()));
	}
}
```

2. 调用ConfigurationClassPostProcessor的postProcessBeanDefinitionRegistry方法
```java
public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) {
	int registryId = System.identityHashCode(registry);
	if (this.registriesPostProcessed.contains(registryId)) {
		throw new IllegalStateException(
				"postProcessBeanDefinitionRegistry already called on this post-processor against " + registry);
	}
	if (this.factoriesPostProcessed.contains(registryId)) {
		throw new IllegalStateException(
				"postProcessBeanFactory already called on this post-processor against " + registry);
	}
	this.registriesPostProcessed.add(registryId);

	processConfigBeanDefinitions(registry);
}
```

3. 将标注相应注解的BeanDefinition信息注册进容器
```java
public void processConfigBeanDefinitions(BeanDefinitionRegistry registry) {
	List<BeanDefinitionHolder> configCandidates = new ArrayList<>();
	String[] candidateNames = registry.getBeanDefinitionNames();

	for (String beanName : candidateNames) {
		BeanDefinition beanDef = registry.getBeanDefinition(beanName);
		if (beanDef.getAttribute(ConfigurationClassUtils.CONFIGURATION_CLASS_ATTRIBUTE) != null) {
			if (logger.isDebugEnabled()) {
				logger.debug("Bean definition has already been processed as a configuration class: " + beanDef);
			}
		}
		else if (ConfigurationClassUtils.checkConfigurationClassCandidate(beanDef, this.metadataReaderFactory)) {
			configCandidates.add(new BeanDefinitionHolder(beanDef, beanName));
		}
	}

	// Return immediately if no @Configuration classes were found
	if (configCandidates.isEmpty()) {
		return;
	}

	// Sort by previously determined @Order value, if applicable
	configCandidates.sort((bd1, bd2) -> {
		int i1 = ConfigurationClassUtils.getOrder(bd1.getBeanDefinition());
		int i2 = ConfigurationClassUtils.getOrder(bd2.getBeanDefinition());
		return Integer.compare(i1, i2);
	});

	// Detect any custom bean name generation strategy supplied through the enclosing application context
	SingletonBeanRegistry sbr = null;
	if (registry instanceof SingletonBeanRegistry) {
		sbr = (SingletonBeanRegistry) registry;
		if (!this.localBeanNameGeneratorSet) {
			BeanNameGenerator generator = (BeanNameGenerator) sbr.getSingleton(
					AnnotationConfigUtils.CONFIGURATION_BEAN_NAME_GENERATOR);
			if (generator != null) {
				this.componentScanBeanNameGenerator = generator;
				this.importBeanNameGenerator = generator;
			}
		}
	}

	if (this.environment == null) {
		this.environment = new StandardEnvironment();
	}

	// Parse each @Configuration class
	ConfigurationClassParser parser = new ConfigurationClassParser(
			this.metadataReaderFactory, this.problemReporter, this.environment,
			this.resourceLoader, this.componentScanBeanNameGenerator, registry);

	Set<BeanDefinitionHolder> candidates = new LinkedHashSet<>(configCandidates);
	Set<ConfigurationClass> alreadyParsed = new HashSet<>(configCandidates.size());
	do {
		parser.parse(candidates);
		parser.validate();

		Set<ConfigurationClass> configClasses = new LinkedHashSet<>(parser.getConfigurationClasses());
		configClasses.removeAll(alreadyParsed);

		// Read the model and create bean definitions based on its content
		if (this.reader == null) {
			this.reader = new ConfigurationClassBeanDefinitionReader(
					registry, this.sourceExtractor, this.resourceLoader, this.environment,
					this.importBeanNameGenerator, parser.getImportRegistry());
		}
		this.reader.loadBeanDefinitions(configClasses);
		alreadyParsed.addAll(configClasses);

		candidates.clear();
		if (registry.getBeanDefinitionCount() > candidateNames.length) {
			String[] newCandidateNames = registry.getBeanDefinitionNames();
			Set<String> oldCandidateNames = new HashSet<>(Arrays.asList(candidateNames));
			Set<String> alreadyParsedClasses = new HashSet<>();
			for (ConfigurationClass configurationClass : alreadyParsed) {
				alreadyParsedClasses.add(configurationClass.getMetadata().getClassName());
			}
			for (String candidateName : newCandidateNames) {
				if (!oldCandidateNames.contains(candidateName)) {
					BeanDefinition bd = registry.getBeanDefinition(candidateName);
					if (ConfigurationClassUtils.checkConfigurationClassCandidate(bd, this.metadataReaderFactory) &&
							!alreadyParsedClasses.contains(bd.getBeanClassName())) {
						candidates.add(new BeanDefinitionHolder(bd, candidateName));
					}
				}
			}
			candidateNames = newCandidateNames;
		}
	}
	while (!candidates.isEmpty());

	// Register the ImportRegistry as a bean in order to support ImportAware @Configuration classes
	if (sbr != null && !sbr.containsSingleton(IMPORT_REGISTRY_BEAN_NAME)) {
		sbr.registerSingleton(IMPORT_REGISTRY_BEAN_NAME, parser.getImportRegistry());
	}

	if (this.metadataReaderFactory instanceof CachingMetadataReaderFactory) {
		// Clear cache in externally provided MetadataReaderFactory; this is a no-op
		// for a shared cache since it'll be cleared by the ApplicationContext.
		((CachingMetadataReaderFactory) this.metadataReaderFactory).clearCache();
	}
}
```

4. 检查是否被@Configuration,@Component,@ComponentScan,@Import,@ImportResource,@Bean标注
```java
public static boolean checkConfigurationClassCandidate(
		BeanDefinition beanDef, MetadataReaderFactory metadataReaderFactory) {

	String className = beanDef.getBeanClassName();
	if (className == null || beanDef.getFactoryMethodName() != null) {
		return false;
	}

	AnnotationMetadata metadata;
	if (beanDef instanceof AnnotatedBeanDefinition &&
			className.equals(((AnnotatedBeanDefinition) beanDef).getMetadata().getClassName())) {
		// Can reuse the pre-parsed metadata from the given BeanDefinition...
		metadata = ((AnnotatedBeanDefinition) beanDef).getMetadata();
	}
	else if (beanDef instanceof AbstractBeanDefinition && ((AbstractBeanDefinition) beanDef).hasBeanClass()) {
		// Check already loaded Class if present...
		// since we possibly can't even load the class file for this Class.
		Class<?> beanClass = ((AbstractBeanDefinition) beanDef).getBeanClass();
		if (BeanFactoryPostProcessor.class.isAssignableFrom(beanClass) ||
				BeanPostProcessor.class.isAssignableFrom(beanClass) ||
				AopInfrastructureBean.class.isAssignableFrom(beanClass) ||
				EventListenerFactory.class.isAssignableFrom(beanClass)) {
			return false;
		}
		metadata = AnnotationMetadata.introspect(beanClass);
	}
	else {
		try {
			MetadataReader metadataReader = metadataReaderFactory.getMetadataReader(className);
			metadata = metadataReader.getAnnotationMetadata();
		}
		catch (IOException ex) {
			if (logger.isDebugEnabled()) {
				logger.debug("Could not find class file for introspecting configuration annotations: " +
						className, ex);
			}
			return false;
		}
	}

	Map<String, Object> config = metadata.getAnnotationAttributes(Configuration.class.getName());
	// 判断是否被@Configuration标注
	if (config != null && !Boolean.FALSE.equals(config.get("proxyBeanMethods"))) {
		beanDef.setAttribute(CONFIGURATION_CLASS_ATTRIBUTE, CONFIGURATION_CLASS_FULL);
	}
	// 判断是否被@Component,@ComponentScan,@Import,@ImportResource,@Bean标注
	else if (config != null || isConfigurationCandidate(metadata)) {
		beanDef.setAttribute(CONFIGURATION_CLASS_ATTRIBUTE, CONFIGURATION_CLASS_LITE);
	}
	else {
		return false;
	}

	// It's a full or lite configuration candidate... Let's determine the order value, if any.
	Integer order = getOrder(metadata);
	if (order != null) {
		beanDef.setAttribute(ORDER_ATTRIBUTE, order);
	}

	return true;
}

public static boolean isConfigurationCandidate(AnnotationMetadata metadata) {
	// Do not consider an interface or an annotation...
	if (metadata.isInterface()) {
		return false;
	}

	// Any of the typical annotations found?
	for (String indicator : candidateIndicators) {
		if (metadata.isAnnotated(indicator)) {
			return true;
		}
	}

	// Finally, let's look for @Bean methods...
	try {
		return metadata.hasAnnotatedMethods(Bean.class.getName());
	}
	catch (Throwable ex) {
		if (logger.isDebugEnabled()) {
			logger.debug("Failed to introspect @Bean methods on class [" + metadata.getClassName() + "]: " + ex);
		}
		return false;
	}
}

private static final Set<String> candidateIndicators = new HashSet<>(8);

static {
	candidateIndicators.add(Component.class.getName());
	candidateIndicators.add(ComponentScan.class.getName());
	candidateIndicators.add(Import.class.getName());
	candidateIndicators.add(ImportResource.class.getName());
}
```

### 自定义BeanFactoryPostProcessor扩展代码案例
```java
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.beans.factory.support.DefaultListableBeanFactory;
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class MyClassPathXmlApplicationContext extends ClassPathXmlApplicationContext {


    public MyClassPathXmlApplicationContext(String... configLocations){
        super(configLocations);
    }

    @Override
    protected void initPropertySources() {
        System.out.println("扩展initPropertySource");
        getEnvironment().setRequiredProperties("username");
    }

    @Override
    protected void customizeBeanFactory(DefaultListableBeanFactory beanFactory) {
        super.setAllowBeanDefinitionOverriding(false);
        super.setAllowCircularReferences(false);
        super.addBeanFactoryPostProcessor(new MyBeanFactoryPostProcessor());
        super.customizeBeanFactory(beanFactory);
    }

}
```

### 自定义BeanDefinitionRegistryPostProcessor扩展代码案例
```java
import org.springframework.beans.BeansException;
import org.springframework.beans.MutablePropertyValues;
import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.beans.factory.config.ConstructorArgumentValues;
import org.springframework.beans.factory.support.BeanDefinitionRegistry;
import org.springframework.beans.factory.support.BeanDefinitionRegistryPostProcessor;
import org.springframework.core.Ordered;
import org.springframework.core.PriorityOrdered;
import org.springframework.core.ResolvableType;

public class MyBeanDefinition implements BeanDefinitionRegistryPostProcessor, Ordered {
    private String name;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return "MyBeanDefinition{" +
                "name='" + name + '\'' +
                '}';
    }

    @Override
    public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) throws BeansException {
        System.out.println("postProcessBeanDefinitionRegistry----------------------");
    }

    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
        System.out.println("postProcessBeanFactory========================");
    }

    @Override
    public int getOrder() {
        return 0;
    }
}
```

```java
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.beans.factory.support.BeanDefinitionBuilder;
import org.springframework.beans.factory.support.BeanDefinitionRegistry;
import org.springframework.beans.factory.support.BeanDefinitionRegistryPostProcessor;
import org.springframework.core.Ordered;
import org.springframework.core.PriorityOrdered;

public class MyBeanDefinitionRegistryPostProcessor implements BeanDefinitionRegistryPostProcessor, Ordered {
    @Override
    public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) throws BeansException {
        BeanDefinitionBuilder builder = BeanDefinitionBuilder.rootBeanDefinition(MyBeanDefinition.class);
        builder.addPropertyValue("name","zhangsan");
        registry.registerBeanDefinition("aa",builder.getBeanDefinition());
    }

    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
        System.out.println("MyBeanDefinitionRegistryPostProcessor-------");
    }

    @Override
    public int getOrder() {
        return 0;
    }
}
```

```java
<bean class="com.mashibing.MyBeanDefinitionRegistryPostProcessor"></bean>
```