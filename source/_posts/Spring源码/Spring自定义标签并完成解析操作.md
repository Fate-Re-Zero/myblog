---
title: Spring自定义标签并完成解析操作
date: 2022-09-04 22:10:38
tags: spring
---

### Spring自定义标签并完成解析操作
```java
public class User {
    private String userName;

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    private String email;

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}
```

```java
import org.springframework.beans.factory.support.BeanDefinitionBuilder;
import org.springframework.beans.factory.xml.AbstractSingleBeanDefinitionParser;
import org.springframework.util.StringUtils;
import org.w3c.dom.Element;

public class UserBeanDefinitionParser extends AbstractSingleBeanDefinitionParser {

    @SuppressWarnings("rawtypes")
    protected Class getBeanClass(Element element) {
        return User.class;
    }

    protected void doParse(Element element, BeanDefinitionBuilder bean) {
        String userName = element.getAttribute("userName");
        String email = element.getAttribute("email");
        if (StringUtils.hasText(userName)) {
            bean.addPropertyValue("userName", userName);
        }
        if (StringUtils.hasText(email)){
            bean.addPropertyValue("email", email);
        }

    }
}
```

```java
import org.springframework.beans.factory.xml.NamespaceHandlerSupport;

public class MyNamespaceHandler extends NamespaceHandlerSupport {

    public void init() {

        registerBeanDefinitionParser("msb", new UserBeanDefinitionParser());
    }

}
```

2.在resource目录下创建META-INF目录下，并创建三个文件
```java
Spring.handlers
	http\://www.lixiang.com/schema/user=com.lixiang.selftag.MyNamespaceHandler
Spring.schemas
	http\://www.lixiang.com/schema/user.xsd=META-INF/user.xsd
user.xsd
	<?xml version="1.0" encoding="UTF-8"?>
	<schema xmlns="http://www.w3.org/2001/XMLSchema"
	        targetNamespace="http://www.lixiang.com/schema/user"
	        xmlns:tns="http://www.lixiang.com/schema/user"
	        elementFormDefault="qualified">
	    <element name="lixiang">
	        <complexType>
	            <attribute name ="id" type = "string"/>
	            <attribute name ="userName" type = "string"/>
	            <attribute name ="email" type = "string"/>
	        </complexType>
	    </element>
	</schema>
```

3.创建配置文件
```java
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:aaa="http://www.lixiang.com/schema/user"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans.xsd
    http://www.lixiang.com/schema/user http://www.lixiang.com/schema/user.xsd">

    <aaa:lixiang id = "testbean" userName = "lee" email = "bbb"/>
</beans>
```

4.编写测试类
```java
public class MyTest {
    public static void main(String[] args) {
        ApplicationContext context = new MyClassPathXmlApplicationContext("test2.xml");
        User user=(User)context.getBean("testbean");
        System.out.println("username:"+user.getUserName()+"  "+"email:"+user.getEmail());
    }
}
```