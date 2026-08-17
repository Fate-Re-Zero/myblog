---
title: Redis分布式锁分析与实现
date: 2021-04-05 14:37:26
tags:
---

### 分布式锁注解类
```java
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface DistributeRedisLock {

    /**
    * key前缀
    */
    String  lockKey ();
    /**
     * 等待时间
     */
    int waitTime () default 60;

    /**
     * 获取锁后超时释放锁时间
     */
    int leaseTime() default  300;

}
```

### 分布式锁切面类
```java
@Aspect
public class DistributeRedisLockAspect {

    @Resource
    private RedissonClient redissonClient;

    private static final Logger logger = LoggerFactory.getLogger(DistributeRedisLockAspect.class);

    public DistributeRedisLockAspect() {
        // Do nothing because of X and Y.
    }

    @Around(
            value = "@annotation(com.banksteel.openerp.commons.redisson.DistributeRedisLock)"
    )
    public Object aroundHandle(ProceedingJoinPoint joinPoint) throws Throwable {
        Method targetMethod = AspectUtils.getTargetMethod(joinPoint);
        DistributeRedisLock distributeRedisLock = targetMethod.getAnnotation(DistributeRedisLock.class);
        Object[] args = joinPoint.getArgs();
        String memberId = SaasParameter.getMemberId();
        String arg0 = args[0].toString();
        StringBuffer s = new StringBuffer(distributeRedisLock.lockKey()).append("::").append(memberId)
                .append("::").append(arg0);
        RLock lock = null;
        try {
            lock = redissonClient.getLock(s.toString());
            if (lock != null) {
                if(lock.tryLock(distributeRedisLock.waitTime(), distributeRedisLock.leaseTime(), TimeUnit.SECONDS)) {
                    logger.info("获取切面redis锁成功{}",targetMethod.getName());
                    return joinPoint.proceed();
                }else{
                    throw new BuzzErrorException("系统正在处理，请勿频繁操作！");
                }
            }
            throw new BuzzErrorException("系统异常，请稍后再试！");
        } catch (Exception var6) {
            throw new BuzzErrorException(var6.getMessage());
        }finally {
            if (lock != null) {
                lock.unlock();
            }
        }
    }
}
```

### redis配置类
```java
@Configuration
@EnableConfigurationProperties(RedissonProperty.class)
@ConditionalOnClass({RedissonClient.class})
@ConditionalOnProperty("banksteel.redis.nodes")
public class MyRedissonAutoConfiguration {

    @Bean
    public RedissonClient redissonClient(RedissonProperty properties){
        Config config = new Config();
            String[] nodes = properties.getNodes().split(",");
        List<String> newNodes = new ArrayList(nodes.length);

        for(String node: nodes){
            newNodes.add(node.startsWith("redis://") ? node : "redis://" + node);
        }

        SentinelServersConfig serverConfig = config.useSentinelServers()
                    .addSentinelAddress(newNodes.toArray(new String[nodes.length]))
                    .setMasterName(properties.getMaster())
                    .setTimeout(properties.getTimeout())
                    .setMasterConnectionPoolSize(properties.getMasterSize())
                    .setSlaveConnectionPoolSize(properties.getSlaveSize())
                ;

            if (!StringUtils.isEmpty(properties.getPassword())) {
                serverConfig.setPassword(properties.getPassword());
            }

        return Redisson.create(config);
    }

    @Bean
    public RedissonUtil redissonUtil(RedissonProperty properties){
        return new RedissonUtil(redissonClient(properties));
    }

}
```

### RedissonProperty
```java
@Data
@ConfigurationProperties(prefix = "banksteel.redis")
public class RedissonProperty {
    private String password;
    private String master;
    private String nodes;
    private int timeout = 5000;
    private int masterSize = 10;
    private int slaveSize = 10;
}
```

### redis处理工具
```java
public class RedissonUtil {
    private RedissonClient redissonClient;

    public RedissonUtil(RedissonClient redissonClient) {
        this.redissonClient = redissonClient;
    }

    /**`
     * 获取字符串对象
     *
     * @param objectName
     * @return
     */
    public <T> RBucket<T> getRBucket(String objectName) {
        RBucket<T> bucket = redissonClient.getBucket(objectName);
        return bucket;
    }

    /**
     * 获取Map对象
     *
     * @param objectName
     * @return
     */
    public <K, V> RMap<K, V> getRMap(String objectName) {
        RMap<K, V> map = redissonClient.getMap(objectName);
        return map;
    }

    /**
     * 获取有序集合
     *
     * @param objectName
     * @return
     */
    public <V> RSortedSet<V> getRSortedSet(String objectName) {
        RSortedSet<V> sortedSet = redissonClient.getSortedSet(objectName);
        return sortedSet;
    }

    /**
     * 获取集合
     *
     * @param objectName
     * @return
     */
    public <V> RSet<V> getRSet(String objectName) {
        RSet<V> rSet = redissonClient.getSet(objectName);
        return rSet;
    }

    /**
     * 获取列表
     *
     * @param objectName
     * @return
     */
    public <V> RList<V> getRList(String objectName) {
        RList<V> rList = redissonClient.getList(objectName);
        return rList;
    }

    /**
     * 获取队列
     *
     * @param objectName
     * @return
     */
    public <V> RQueue<V> getRQueue(String objectName) {
        RQueue<V> rQueue = redissonClient.getQueue(objectName);
        return rQueue;
    }

    /**
     * 获取双端队列
     *
     * @param objectName
     * @return
     */
    public <V> RDeque<V> getRDeque(String objectName) {
        RDeque<V> rDeque = redissonClient.getDeque(objectName);
        return rDeque;
    }

    /**
     * 获取锁
     *
     * @param objectName
     * @return
     */
    public RLock getRLock(String objectName) {
        RLock rLock = redissonClient.getLock(objectName);
        return rLock;
    }

    /**
     * 获取读取锁
     *
     * @param objectName
     * @return
     */
    public RReadWriteLock getRWLock(String objectName) {
        RReadWriteLock rwlock = redissonClient.getReadWriteLock(objectName);
        return rwlock;
    }

    /**
     * 获取原子数
     *
     * @param objectName
     * @return
     */
    public RAtomicLong getRAtomicLong(String objectName) {
        RAtomicLong rAtomicLong = redissonClient.getAtomicLong(objectName);
        return rAtomicLong;
    }

    /**
     * 获取记数锁
     *
     * @param objectName
     * @return
     */
    public RCountDownLatch getRCountDownLatch(String objectName) {
        RCountDownLatch rCountDownLatch = redissonClient.getCountDownLatch(objectName);
        return rCountDownLatch;
    }

    /**
     * 获取消息的Topic
     *
     * @param objectName
     * @return
     */
    public <M> RTopic<M> getRTopic(String objectName) {
        RTopic<M> rTopic = redissonClient.getTopic(objectName);
        return rTopic;
    }
}
```

### redis配置文件
```java
banksteel.redis.master=publicredis
banksteel.redis.password =8clxNrcOgho!
banksteel.redis.nodes=redis1.public.banksteel.local:26379,redis2.public.banksteel.local:26379,redis3.public.banksteel.local:26379
banksteel.redis.timeout=50000

```



