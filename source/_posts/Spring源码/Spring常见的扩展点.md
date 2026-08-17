---
title: Spring常见的扩展点
date: 2022-09-04 14:39:38
tags: spring
---

### 扩展initPropertySources方法
理解:在refresh方法中的prepareRefresh方法，执行刷新前的准备工作中提供了initPropertySources模板方法,一般用于一些环境变量的设置

源码出处：
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
	// AbstractApplicationContext提供的模板方法,可以继承它或者其子类进行具体实现
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

1. 继承具体的类并扩展实现,ClassPathXmlApplicationContext为AbstractApplicationContext的字类,可以进行一些环境变量的设置
```java
public class MyClassPathXmlApplicationContext extends ClassPathXmlApplicationContext {
    public MyClassPathXmlApplicationContext(String... configLocations){
        super(configLocations);
    }

    @Override
    protected void initPropertySources() {
        getEnvironment().setRequiredProperties("OS");
    }
}

public class MyTest {
    public static void main(String[] args) {
        ApplicationContext context = new MyClassPathXmlApplicationContext("test2.xml");
        User user=(User)context.getBean("testbean");
        System.out.println("username:"+user.getUserName()+"  "+"email:"+user.getEmail());
    }
}
```

2. 该扩展点在Spring MVC中的具体应用
```java
public class StandardServletEnvironment extends StandardEnvironment implements ConfigurableWebEnvironment {

	/** Servlet context init parameters property source name: {@value}. */
	public static final String SERVLET_CONTEXT_PROPERTY_SOURCE_NAME = "servletContextInitParams";

	/** Servlet config init parameters property source name: {@value}. */
	public static final String SERVLET_CONFIG_PROPERTY_SOURCE_NAME = "servletConfigInitParams";

	/** JNDI property source name: {@value}. */
	public static final String JNDI_PROPERTY_SOURCE_NAME = "jndiProperties";

	@Override
	protected void customizePropertySources(MutablePropertySources propertySources) {
		// 1.添加servletConfigInitParams属性源(作为占位符, 之后会被替换)
		propertySources.addLast(new StubPropertySource(SERVLET_CONFIG_PROPERTY_SOURCE_NAME));
		// 2.添加servletContextInitParams属性源(作为占位符, 之后会被替换)
		propertySources.addLast(new StubPropertySource(SERVLET_CONTEXT_PROPERTY_SOURCE_NAME));
		if (JndiLocatorDelegate.isDefaultJndiEnvironmentAvailable()) {
			// 3.添加jndiProperties属性源
			propertySources.addLast(new JndiPropertySource(JNDI_PROPERTY_SOURCE_NAME));
		}
		// 4.调用父类中的customizePropertySources方法
		super.customizePropertySources(propertySources);
	}

	@Override
	public void initPropertySources(@Nullable ServletContext servletContext, @Nullable ServletConfig servletConfig) {
		WebApplicationContextUtils.initServletPropertySources(getPropertySources(), servletContext, servletConfig);
	}
}

public abstract class WebApplicationContextUtils {
	public static void initServletPropertySources(MutablePropertySources propertySources, ServletContext servletContext) {
		initServletPropertySources(propertySources, servletContext, null);
	}

	public static void initServletPropertySources(MutablePropertySources sources,
			@Nullable ServletContext servletContext, @Nullable ServletConfig servletConfig) {

		Assert.notNull(sources, "'propertySources' must not be null");
		String name = StandardServletEnvironment.SERVLET_CONTEXT_PROPERTY_SOURCE_NAME;
		if (servletContext != null && sources.get(name) instanceof StubPropertySource) {
			// 1.如果servletContext不为null && propertySources中包含servletContextInitParams数据源 && 该数据源的类型为StubPropertySource,
			// 则将servletContextInitParams的数据源替换成servletContext
			sources.replace(name, new ServletContextPropertySource(name, servletContext));
		}
		name = StandardServletEnvironment.SERVLET_CONFIG_PROPERTY_SOURCE_NAME;
		if (servletConfig != null && sources.get(name) instanceof StubPropertySource) {
			// 2.如果servletConfig不为null && propertySources中包含servletConfigInitParams数据源 && 该数据源的类型为StubPropertySource,
			// 则将servletConfigInitParams的数据源替换成servletConfig
			sources.replace(name, new ServletConfigPropertySource(name, servletConfig));
		}
	}
}
```

### 扩展实现customizeBeanFactory方法
1. 在创建BeanFactory后, 可以重写该方法, 为BeanFactory设置属性,源码出处:
```java
public abstract class AbstractApplicationContext extends DefaultResourceLoader
		implements ConfigurableApplicationContext {
	public void refresh() throws BeansException, IllegalStateException {
		......
		// Tell the subclass to refresh the internal bean factory.
		ConfigurableListableBeanFactory beanFactory = obtainFreshBeanFactory();
		......
	}
}

public abstract class AbstractApplicationContext extends DefaultResourceLoader
		implements ConfigurableApplicationContext {
	protected ConfigurableListableBeanFactory obtainFreshBeanFactory() {
		// 1.刷新 BeanFactory，由AbstractRefreshableApplicationContext实现
		refreshBeanFactory();
		// 2.拿到刷新后的 BeanFactory
		return getBeanFactory();
	}
}

public abstract class AbstractRefreshableApplicationContext extends AbstractApplicationContext {
	@Override
	protected final void refreshBeanFactory() throws BeansException {
		// 1.判断是否已经存在 BeanFactory，如果存在则先销毁、关闭该 BeanFactory
		if (hasBeanFactory()) {
			destroyBeans();
			closeBeanFactory();
		}
		try {
			// 2.创建一个新的BeanFactory
			DefaultListableBeanFactory beanFactory = createBeanFactory();
			beanFactory.setSerializationId(getId());
			// 可以继承该类或者其字类，重写该方法
			customizeBeanFactory(beanFactory);
			// 3.加载 bean 定义。
			loadBeanDefinitions(beanFactory);
			this.beanFactory = beanFactory;
		}
		catch (IOException ex) {
			throw new ApplicationContextException("I/O error parsing bean definition source for " + getDisplayName(), ex);
		}
	}
}

public abstract class AbstractRefreshableApplicationContext extends AbstractApplicationContext {
	protected void customizeBeanFactory(DefaultListableBeanFactory beanFactory) {
		if (this.allowBeanDefinitionOverriding != null) {
			beanFactory.setAllowBeanDefinitionOverriding(this.allowBeanDefinitionOverriding);
		}
		if (this.allowCircularReferences != null) {
			beanFactory.setAllowCircularReferences(this.allowCircularReferences);
		}
	}
}
```

2. 此方法是用来实现BeanFactory的属性设置，主要是设置两个属性：
​	allowBeanDefinitionOverriding：是否允许覆盖同名称的不同定义的对象
​	allowCircularReferences：是否允许bean之间的循环依赖
```java
public class MyClassPathXmlApplicationContext extends ClassPathXmlApplicationContext {

    MyClassPathXmlApplicationContext(String... locations){
        super(locations);
    }

    @Override
    protected void customizeBeanFactory(DefaultListableBeanFactory beanFactory) {
        super.setAllowBeanDefinitionOverriding(true);
        super.setAllowCircularReferences(true);
        super.customizeBeanFactory(beanFactory);
    }
}
```

### preProcessXml(root),postProcessXml(root)




### Spring如何扩展实现自定义属性编辑器
在日常的工作中，我们经常遇到一些特殊的案例需要自定义属性的解析器来完成对应的属性解析工作，大家需要理解它的本质来进行随意的扩展工作,但是此处的扩展没有大家想象的那么简单，详细的流程讲课的时候我大概讲一下，但是要复杂很多。主要有两种方式：

```java
class Address {
    private String district;
    private String city;
    private String province;

    public String getDistrict() {
        return district;
    }

    public void setDistrict(String district) {
        this.district = district;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getProvince() {
        return province;
    }

    public void setProvince(String province) {
        this.province = province;
    }

    public String toString() {
        return this.province + "省" + this.city + "市" + this.district + "区";
    }
}

public class Customer {
    private String name;
    private Address address;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Address getAddress() {
        return address;
    }

    public void setAddress(Address address) {
        this.address = address;
    }
}

import java.beans.PropertyEditorSupport;

public class AddressPropertyEditor extends PropertyEditorSupport {
    @Override
    public void setAsText(String text) {
        try {
            String[] adds = text.split("-");
            Address address = new Address();
            address.setProvince(adds[0]);
            address.setCity(adds[1]);
            address.setDistrict(adds[2]);
            this.setValue(address);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

import org.springframework.beans.PropertyEditorRegistrar;
import org.springframework.beans.PropertyEditorRegistry;

public class MyPropertyEditorRegistrar implements PropertyEditorRegistrar {
    @Override
    public void registerCustomEditors(PropertyEditorRegistry registry) {
        registry.registerCustomEditor(Address.class,new AddressPropertyEditor());
    }
}

<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
    <bean id="customer" class="com.lixiang.propertyEditor.Customer">
        <property name="name" value="Jack" />
        <property name="address" value="浙江-杭州-西湖" />
    </bean>
    <!--第一种方式-->
    <bean class="org.springframework.beans.factory.config.CustomEditorConfigurer">
        <property name="propertyEditorRegistrars">
            <list>
                <bean class="com.lixiang.propertyEditor.MyPropertyEditorRegistrar"></bean>
            </list>
        </property>
    </bean>
    <!--第二种方式-->
    <bean class="org.springframework.beans.factory.config.CustomEditorConfigurer">
        <property name="customEditors">
            <map>
                <entry key="com.lixiang.propertyEditor.Address">
                    <value>com.lixiang.propertyEditor.AddressPropertyEditor</value>
                </entry>
            </map>
        </property>
    </bean>
</beans>

public class Test3 {

    public static void main(String[] args) {
        ApplicationContext ac = new ClassPathXmlApplicationContext("propertyEditor.xml");
        Customer c = ac.getBean("customer", Customer.class);
        //输出
        System.out.println(c.getAddress());
    }
}
```

### postProcessBeanFactory进行继承重写该方法，可以对beanFactory进行扩展操作；

### BeanDefinitionRegistryPostProcessor和BeanFactoryPostProcessor

### 可以产生循环依赖的点：Autowirte, Import