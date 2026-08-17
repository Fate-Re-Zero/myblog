---
title: rabbitMQ实现广播
date: 2021-09-02 16:54:48
tags:
---

### 队列交换机配置
```java
import java.util.Random;
import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

/**
 * @Description
 * @Author lixiang
 * @Date Created in 2021/5/6 15:53
 */
@Configuration
@ComponentScan(basePackages = {"com.banksteel.openerp.rabbitmq.listener"})
public class MessageQueueConfigraction {

    @Value("${rmq.exchange}")
    private String todoMessageExchange;
    @Value("${todomessage.websocket.queue}")
    private String todoMessageQueue;
    @Value("${todomessage.routing.key}")
    private String todoMessageRoutingKey;

    @Bean
    DirectExchange createDirectExchange() {
        return new DirectExchange(todoMessageExchange,true,false);
    }

    @Bean
    public Queue createDirectQueue() {
        //System.out.println("aaa:" + exchange);
        // durable:是否持久化,默认是false,持久化队列：会被存储在磁盘上，当消息代理重启时仍然存在，暂存队列：当前连接有效
        // exclusive:默认也是false，只能被当前创建的连接使用，而且当连接关闭后队列即被删除。此参考优先级高于durable
        // autoDelete:是否自动删除，当没有生产者或者消费者使用此队列，该队列会自动删除。
        //一般设置一下队列的持久化就好,其余两个就是默认false
        // 实现队列名加上随机数
        return new Queue(todoMessageQueue + new Random().nextLong(), false);
    }

    //绑定  将队列和交换机绑定, 并设置用于匹配键：TestDirectRouting
    @Bean
    Binding bindingDirect() {
        return BindingBuilder.bind(createDirectQueue()).to(createDirectExchange()).with(todoMessageRoutingKey);
    }

    @Bean
    Binding bindingUpgradeMsgDirect() {
        return BindingBuilder.bind(createDirectQueue()).to(createDirectExchange()).with(upgradeRoutingKey);
    }

}
```

### 配置文件
```java
# 待办消息队列
todomessage.websocket.queue=openerp.saas.mpbp.todomessage
# 待办消息RoutingKey
todomessage.routing.key=todomessage_routing_key
# 交换机
rmq.exchange=openerp_saas_webapp_exchange
```

### rabbitMQ基本配置文件rabbitmq-context.xml
```java
<beans xmlns="http://www.springframework.org/schema/beans"
	xmlns:context="http://www.springframework.org/schema/context"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:rabbit="http://www.springframework.org/schema/rabbit"
	xsi:schemaLocation="http://www.springframework.org/schema/rabbit
	http://www.springframework.org/schema/rabbit/spring-rabbit-1.4.xsd
	http://www.springframework.org/schema/beans
	http://www.springframework.org/schema/beans/spring-beans.xsd
	http://www.springframework.org/schema/aop
	http://www.springframework.org/schema/aop/spring-aop-4.0.xsd
	http://www.springframework.org/schema/context
	http://www.springframework.org/schema/context/spring-context.xsd">


	<!-- 定义RabbitMQ的连接工厂 -->
<rabbit:connection-factory id="connectionFactory" addresses="${rmq.address}" username="${rmq.username}" password="${rmq.password}" />

	<!-- 定义Rabbit模板，指定连接工厂以及定义exchange -->
	<rabbit:template id="amqpTemplate" connection-factory="connectionFactory"
		exchange="${rmq.exchange}" />

	<!-- MQ的管理，包括队列、交换器等 -->
	<rabbit:admin connection-factory="connectionFactory" />

	<!-- 定义队列，并持久化、自动声明 -->
	<rabbit:queue name="${rmq.member.order.queue.name}"
		auto-declare="true" durable="true" />

	<!-- 定义队列，并持久化、自动声明(测试数据) -->
	<rabbit:queue name="${rmq.yunMember.queue.keyNameIn}"
		auto-declare="true" durable="true" />
	<!-- 合同中台新增、变更 -->
	<rabbit:queue name="${mq.contract.add}"
		auto-declare="true" durable="true" />
	<!-- 合同中台修改合同状态-->
	<rabbit:queue name="${mq.contract.status.change}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${mq.contract.handle.result}"
		auto-declare="true" durable="true" />


	<!-- 定义队列，并持久化、自动声明 (测试数据) -->
	<rabbit:queue name="${rmq.yunMember.queue.keyNameOut}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.yunMember.queue.keyNameAdjust}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.openerp.saas.log.business}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.openerp.saas.log.exception}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.openerp.saas.log.mq}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.pop.order.message}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.pop.order.deliveryapply}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.pop.order.revokeapply}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.pop.order.sellpay}"
		auto-declare="true" durable="true" />
	<!-- POP订单消息发送 -->
	<rabbit:queue name="${rmq.pop.order.sellaudit}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.pop.order.realdelivery.result}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.pop.order.deliveryapply.result}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.pop.order.revokeapply.result}"
		auto-declare="true" durable="true" />
	<!-- 钢银钱庄融资赎货合同 -->
	<rabbit:queue name="${rmq.finance.contract}" 
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.finance.inventory}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.finance.inventory.result}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.openerp.saas.goods}"
		auto-declare="true" durable="true" />
    <!-- saas进销存自己发送和接收MQ-自动完成-->
	<rabbit:queue name="${rmq.openerp.auto.complete.queue}"
		auto-declare="true" durable="true" />
	<rabbit:queue name="${openerp.saas.profit.report}" 
		auto-declare="true" durable="true"/>


	<!-- 推送钢银对接消息队列-->
	<rabbit:queue name="${rmq.openerp.saas.report}"
				  auto-declare="true" durable="true" />
  	<!-- 合同结算封装推送财务库存台账异常  -->
	<rabbit:queue name="${rmq.openerp.saas.contract.clearing.book.exception}"
				  auto-declare="true" durable="true" />
	<rabbit:queue name="${rmq.dingding.remind.queue}" auto-declare="true" durable="true" />
	<!-- 集团会员同步 -->
	<rabbit:queue name="${rmq.saas.member.synchronism}"
				  auto-declare="true" durable="true" />

	<!-- 定义交换器，并持久化、自动声明 -->
	<rabbit:direct-exchange name="${rmq.exchange}"
		auto-declare="true" durable="true" auto-delete="false" id="${rmq.exchange}">
		<rabbit:bindings>
			<!--  推送钢银对接消息队列 -->
			<rabbit:binding queue="${rmq.openerp.saas.report}"
				key="${rmq.openerp.saas.report}" />
			<rabbit:binding queue="${rmq.saas.delay.message}"
				key="${rmq.saas.delay.message}"/>
			<!-- 钢银合同订单消息接收 -->
			<rabbit:binding queue="${rmq.member.order.queue.name}"
				key="${rmq.member.order.queue.name}" />
			<!-- 自身模块日志发送 -->
			<rabbit:binding queue="${rmq.openerp.saas.log.business}"
				key="${rmq.openerp.saas.log.business}" />
			<rabbit:binding queue="${rmq.openerp.saas.log.exception}"
				key="${rmq.openerp.saas.log.exception}" />
			<rabbit:binding queue="${rmq.openerp.saas.log.mq}"
				key="${rmq.openerp.saas.log.mq}" />
			<!-- 云仓绑定消息接收 -->
			<rabbit:binding queue="${rmq.yunMember.queue.keyNameIn}"
				key="${rmq.yunMember.queue.keyNameIn}" />
			<rabbit:binding queue="${rmq.yunMember.queue.keyNameOut}"
				key="${rmq.yunMember.queue.keyNameOut}" />
			<rabbit:binding queue="${rmq.yunMember.queue.keyNameAdjust}"
				key="${rmq.yunMember.queue.keyNameAdjust}" />
			<!-- POP订单消息接收 -->
			<rabbit:binding queue="${rmq.pop.order.message}" 
				key="${rmq.pop.order.message}" />
			<rabbit:binding queue="${rmq.pop.order.deliveryapply}"
				key="${rmq.pop.order.deliveryapply}" />
			<rabbit:binding queue="${rmq.pop.order.revokeapply}"
				key="${rmq.pop.order.revokeapply}" />
			<rabbit:binding queue="${rmq.pop.order.sellpay}" 
				key="${rmq.pop.order.sellpay}" />
			<!-- POP订单消息推送 -->
			<rabbit:binding queue="${rmq.pop.order.deliveryapply.result}"
				key="${rmq.pop.order.deliveryapply.result}" />
			<rabbit:binding queue="${rmq.pop.order.revokeapply.result}"
				key="${rmq.pop.order.revokeapply.result}" />
			<rabbit:binding queue="${rmq.pop.order.realdelivery.result}"
				key="${rmq.pop.order.realdelivery.result}" />
			<!-- POP订单审核 -->
			<rabbit:binding queue="${rmq.pop.order.sellaudit}"
				key="${rmq.pop.order.sellaudit}" />
			<rabbit:binding queue="${rmq.finance.contract}" 
				key="${rmq.finance.contract}" />
			<rabbit:binding queue="${rmq.finance.inventory}" 
				key="${rmq.finance.inventory}" />
			<rabbit:binding queue="${rmq.finance.inventory.result}"
				key="${rmq.finance.inventory.result}" />
			<rabbit:binding queue="${rmq.openerp.saas.goods}"
				key="${rmq.openerp.saas.goods}" />
				<!-- saas进销存自己发送和接收MQ-自动完成-->
			<rabbit:binding queue="${rmq.openerp.auto.complete.queue}"
				key="${rmq.openerp.auto.complete.queue}" />
			<rabbit:binding queue="${mq.contract.add}"
				key="${mq.contract.add}" />
			<rabbit:binding queue="${mq.contract.status.change}"
				key="${mq.contract.status.change}" />
			<rabbit:binding queue="${mq.contract.handle.result}"
				key="${mq.contract.handle.result}" />
    		<!-- 合同结算封装推送财务库存台账异常-->
      		<rabbit:binding queue="${rmq.openerp.saas.contract.clearing.book.exception}"
              	key="${rmq.openerp.saas.contract.clearing.book.exception}" />
			<rabbit:binding queue="${openerp.saas.profit.report}" 
				key="${openerp.saas.profit.report}"/>
			<rabbit:binding queue="${rmq.dingding.remind.queue}" 
				key="${rmq.dingding.remind.queue}" />
			<rabbit:binding queue="${rmq.saas.member.synchronism}" 
				key="${rmq.saas.member.synchronism}" />
		</rabbit:bindings>
	</rabbit:direct-exchange>

	<!-- 进销存导入商品消息监听类 -->
	<bean id="importGoodsListener"
		class="com.banksteel.openerp.rabbitmq.listener.ImportGoodsListener" />
	<bean id="generateContractListener"
		class="com.banksteel.openerp.rabbitmq.listener.GenerateContractListener" />
	<!-- 队列监听容器,设置为手动ack,在业务代码中控制消息是否消费成功 -->
	<bean id="memberSynchronismListener"
		class="com.banksteel.openerp.rabbitmq.listener.MemberSynchronismListener"/>
		
	<rabbit:listener-container
		connection-factory="connectionFactory" acknowledge="manual">

		<rabbit:listener queues="${rmq.openerp.saas.goods}"
			ref="importGoodsListener" />
		<rabbit:listener queues="${mq.contract.handle.result}"
			ref="generateContractListener" />
		<rabbit:listener queues="${rmq.saas.member.synchronism}"
		 	ref="memberSynchronismListener"/>
	</rabbit:listener-container>

	<!-- 定义对接云仓mqTemplate -->
	<rabbit:template id="yucangAmqpTemplate" connection-factory="connectionFactory"
					 exchange="${rmq.openerp.yuncang.exchange}" />
	<!-- 定义对接云仓出库队列-->
	<rabbit:queue name="${rmq.openerp.yuncang.saas.out}"
				  auto-declare="true" durable="true" />
	<!-- 定义对接云仓入库队列-->
	<rabbit:queue name="${rmq.openerp.yuncang.saas.in}"
				  auto-declare="true" durable="true" />

	<!-- 定义云仓交换器，并持久化、自动声明 -->
	<rabbit:direct-exchange name="${rmq.openerp.yuncang.exchange}"
							auto-declare="true" durable="true" auto-delete="false" id="${rmq.openerp.yuncang.exchange}">
		<rabbit:bindings>
			<!-- saas进销存自己发送和接收MQ-自动完成-->
			<rabbit:binding queue="${rmq.openerp.yuncang.saas.out}" key="${rmq.openerp.yuncang.saas.out}" />
		</rabbit:bindings>
	</rabbit:direct-exchange>


	<!-- 定义对接云仓mqTemplate -->
	<rabbit:template id="bncAmqpTemplate" connection-factory="connectionFactory"
		exchange="${rmq.saas.exchange}" />

	<!-- 定义对接帮你采队列-->
	<rabbit:queue name="${rmq.saas.sale.4agent.push}"
		auto-declare="true" durable="true"/>

	<!--定义延时弹窗队列-->
	<rabbit:queue name="${rmq.saas.delay.message}"
		auto-declare="true" durable="true" queue-arguments="delayQueueArguments"/>
	<rabbit:queue-arguments id="delayQueueArguments">
		<entry key="x-message-ttl" value="10000" value-type="java.lang.Integer"/>
		<entry key="x-dead-letter-exchange" value="${rmq.exchange}"/>
		<entry key="x-dead-letter-routing-key" value="${upgrade.msg.routing.key}"/>
	</rabbit:queue-arguments>

	<!-- 定义推送帮你采队列 -->
	<rabbit:direct-exchange name="${rmq.saas.exchange}"
		auto-declare="true" durable="true" auto-delete="false" id="${rmq.saas.exchange}">
		<rabbit:bindings>
			<!-- saas进销存自己发送和接收MQ-自动完成-->
			<rabbit:binding queue="${rmq.saas.sale.4agent.push}"
				key="${rmq.saas.sale.4agent.push}" />
		</rabbit:bindings>
	</rabbit:direct-exchange>
</beans>
```

### 消费者
```java
import com.alibaba.fastjson.JSONObject;
import com.banksteel.openerp.common.framework.WebsocketEndPoint;
import com.banksteel.openerp.commons.queue.MessageEntity;
import com.rabbitmq.client.Channel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;

import java.nio.charset.StandardCharsets;

/**
 * @Description
 * @Author lixiang
 * @Date Created in 2021/4/30 14:22
 */
@Configuration
public class WebSocketMessageConsumer {

    private static final Logger logger = LoggerFactory.getLogger(WebSocketMessageConsumer.class);

    @Autowired
    private WebsocketEndPoint websocketEndPoint;

    @RabbitListener(queues = "#{createDirectQueue.name}")
    public void consumer(Message message, Channel channel) throws Exception {
        try {
            String body = new String(message.getBody(), StandardCharsets.UTF_8);
            logger.info("============================自动完成接收信息:{}", body);
            MessageEntity mess = JSONObject.parseObject(body, MessageEntity.class);
            if (mess != null) {
                websocketEndPoint.handleAllMessage(mess);
            } else {
                logger.error("消息传输异常body={}", message);
            }
        } catch (Exception e) {
            logger.error("弹窗队列异常：{}", e.getMessage());
        } finally {
            channel.basicAck(message.getMessageProperties().getDeliveryTag(), false);
        }
    }
}
```

### webSocket的使用及配置
```java
import com.banksteel.openerp.commons.framework.exception.EntityNotFoundException;
import com.banksteel.openerp.commons.queue.MessageEntity;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import javax.websocket.server.ServerEndpoint;
import java.util.Hashtable;
import java.util.Map;
import java.util.Timer;

/**
 * @version 1.0
 * @description:创建websocket处理类
 * @projectName:openerp-webapp
 * @className:WebsocketEndPoint.java
 * @author:商家进销存项目组 饶亮
 * @createTime:2017年10月11日 上午10:54:23
 */
@ServerEndpoint(value = "/api/websocket")
public class WebsocketEndPoint extends TextWebSocketHandler {

	private Timer timer;

	private Logger logger = (Logger) LoggerFactory.getLogger(this.getClass());
	private static Map<String, String> sessionIds = new Hashtable<String, String>();
	private static Map<String, WebSocketSession> onlineSessions = new Hashtable<String, WebSocketSession>();

	@Override
	protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
		if (!session.isOpen()) {
			logger.info("获取session失败=======");
			timer.cancel();
			return;
		}
		logger.info("获取session成功=======");
		logger.info("主动触发用户信息:{}", session.getUri().getQuery());
		super.handleTextMessage(session, message);
		TextMessage returnMessage = new TextMessage(message.getPayload());
		synchronized (WebsocketEndPoint.class) {
			if ("ping".equals(message.getPayload())) {
				TextMessage pong = new TextMessage("pong");
				logger.info("{},{},{}", "心跳重连", "消息推送", String.valueOf(pong));
				session.sendMessage(pong);
			} else {
				logger.info("{},{},{},{}", "主动触发", "消息推送", "首页消息完成", returnMessage);
				session.sendMessage(returnMessage);
			}
		}
	}

	@Override
	public void afterConnectionEstablished(WebSocketSession session) {
		logger.info("===========用户正在连接============");
		String userId = session.getUri().getQuery().split("=")[1];
		logger.info("===========用户正在连接Id={}============", userId);
		if (userId != null && !userId.equals("")) {
			onlineSessions.put(userId, session);
			sessionIds.put(session.getId(), userId);
		} else {
			throw new EntityNotFoundException("未传入当前登录人id");
		}

	}

	public void handleAllMessage(MessageEntity mess) throws Exception {
		for (String userId : mess.getUserIds()) {
			WebSocketSession session = onlineSessions.get(userId);
			if (session != null) {
				logger.info("MQ触发用户信息:{}", session.getUri().getQuery());
				TextMessage textMessage = new TextMessage(mess.getMessage());
				logger.info("{},{},{},{},{}", "MQ触发handleAllMessage",
					"消息推送", "弹窗消息推送", textMessage, userId);
				handleMessage(session, textMessage);
			}
		}
	}

	@Override
	public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
		String userId = sessionIds.get(session.getId());
		onlineSessions.remove(userId);
		sessionIds.remove(session.getId());
		logger.info("用户websocket断开id={}", userId);
	}
}
```

### webSocket配置文件
```java
<beans xmlns="http://www.springframework.org/schema/beans"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:websocket="http://www.springframework.org/schema/websocket"
	xsi:schemaLocation="  
        http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd  
        http://www.springframework.org/schema/websocket http://www.springframework.org/schema/websocket/spring-websocket.xsd">

	<bean id="websocket"
		class="com.banksteel.openerp.common.framework.WebsocketEndPoint" />

	<websocket:handlers allowed-origins="*">
		<websocket:mapping path="/websocket" handler="websocket" />
		<websocket:handshake-interceptors>
			<bean
				class="com.banksteel.openerp.common.interceptors.HandshakeInterceptor" />
		</websocket:handshake-interceptors>
	</websocket:handlers>
</beans>
```