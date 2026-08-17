---
title: 分布式session实现场景
date: 2020-12-26 18:14:58
tags:
---

### saas分布式session实现方式 
在用户登录时，为当前登录用户生成一个全局唯一的token，并通过redis以这个token为 key登录用户信息为value保存到redis，并将token写到域名下的cookies中达到分布式session共享。 

具体实现时序图如下：
![](/images/具体实现时序图.jpg)

前端请求访问处理流程：
![](/images/前端请求处理流程.jpg)

分布式session实现类图：
![](/images/分布式session实现类图.jpg)

### 主要类讲解 

### 1.分布式session管理接口:TokenManager

```java
/**
 * 〈一句话功能简述〉<br>
 * Description: token管理器统一入口
 */
public interface TokenManager<U> {
    /**
     * 创建token并保存到redis和cookie中
     * @param userInfo
     * @return
     */
    String createAndSaveToken(U userInfo);

    /**
     * 延长用户token的有效时间
     */
    void extendUserToken();

    /**
     * 用户退出登陆
     */
    void loginOff();

    /**
     * 获取用户信息
     * @return
     */
    U getUserByToken(Class<U> clazz);

    /**
     * Description: 通过http上下文cookies中的token获取当前登录用户信息，如果存在登录用户，则延迟登录用户登录状态的有效时间，并返回，否则返回空
     *
     */
    default U getAndExtendUserByToken(Class<U> clazz){
        U currentUser = getUserByToken(clazz);
        saveCurrentLoginUser(currentUser);
        extendUserToken();
        return currentUser;
    }

    /**
     * Description: 保存当前登录用户人信息
     */
    void saveCurrentLoginUser(U currentUser);
}
```

### 2.用户登录处理扩展接口：TokenUserLoginHandler

```java
/**
 * Description: 用户登录处理扩展接口
 */
public interface TokenUserLoginHandler<U> {
    /**
     * 执行用户登录并创建token
     * @param loginUser
     * @return
     */
    default String loginAndCreateToken(U loginUser){
        return StringConvertUtils.shortUuid();
    }

    /**
     * 验证用户登录状态有效时间
     * @param loginUser
     */
    default int extend(U loginUser){
    	return 0;
    }

    /**
     * 用户登出
     * @param loginUser
     */
    default void loginOff(U loginUser){}
}
```

### 3.redis实现分布式session配置类：RedisTokenManagerConfig

```java
import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 〈一句话功能简述〉<br>
 * Description: token配置类
 */
@ConfigurationProperties(prefix = "openerp.auth.token")
public class RedisTokenManagerConfig {

    /**
     * token前缀:可通过auth.token.keyPrefix配置
     */
    private String keyPrefix = "openerp:token:";

    /**
     * token有效期,单位为秒,默认1小时:可通过auth.token.expires配置
     */
    private int expires = 60 * 60 ;
    /**
     * 浏览器的cookie名称:可通过auth.token.cookieKey配置
     */
    private String cookieKey = "saasToken";

    public String getKeyPrefix() {
        return keyPrefix;
    }

    public void setKeyPrefix(String keyPrefix) {
        this.keyPrefix = keyPrefix;
    }

    public int getExpires() {
        return expires;
    }

    public int getExpires(String token) {
        return token.contains(AuthorizationConstants.IS_APP_KEY) ? expires * 24 * 7 : expires;
    }

    public void setExpires(int expires) {
        this.expires = expires;
    }

    public String getCookieKey() {
        return cookieKey;
    }

    public void setCookieKey(String cookieKey) {
        this.cookieKey = cookieKey;
    }
}
```

### 4.redis实现分布式session类： RedisTokenManager 
获取当前请求上下文中的token：先从请求参数中获取，再从header中获取，最后从cookie中获取

```java
import com.alibaba.fastjson.JSONObject;
import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.Objects;

/**
 * 〈一句话功能简述〉<br>
 * Description: redis 实现session共享的token管理器
 */
public class RedisTokenManager<U> implements TokenManager<U> {

    private Logger logger = Logger.getLogger(RedisTokenManager.class);

    private AbstractRedisCache redisUtils;
    private RedisTokenManagerConfig tokenManagerConfig;
    private ThreadLocal<U> currentLoginUser = new ThreadLocal<>();
    private TokenUserLoginHandler<U> tokenUserLoginHandler;

    public RedisTokenManager(AbstractRedisCache redisUtils, RedisTokenManagerConfig tokenManagerConfig) {
        this( redisUtils,tokenManagerConfig,new TokenUserLoginHandler<U>(){});
    }

    public RedisTokenManager(AbstractRedisCache redisUtils, RedisTokenManagerConfig tokenManagerConfig, TokenUserLoginHandler<U> tokenUserLoginHandler) {
        this.redisUtils = redisUtils;
        if (tokenManagerConfig == null) {
            tokenManagerConfig = new RedisTokenManagerConfig();
        }
        this.tokenManagerConfig = tokenManagerConfig;
        this.tokenUserLoginHandler = tokenUserLoginHandler;
    }

    @Override
    public void extendUserToken() {
        String token = getToken();
        String tokenKey = createTokenKey(token);
        if (redisUtils.exists(tokenKey)) {
            U u = getCurrentLoginUser();
            if (Objects.nonNull(u)){
                int extendTime = this.tokenUserLoginHandler.extend(u);
                redisUtils.expire(tokenKey, extendTime);
            } else {
            	redisUtils.expire(tokenKey, tokenManagerConfig.getExpires());
            }
            saveToCookie(token);
        }
    }

    @Override
    public void loginOff() {
        String token = getToken();
        if (StringUtils.isNotBlank(token)){
            String tokenKey = createTokenKey(token);
            loginOff(tokenKey);
            clearCookieToken();
            U u = getCurrentLoginUser();
            if (Objects.nonNull(u)){
                this.tokenUserLoginHandler.loginOff(u);
                saveCurrentLoginUser(null);
            }
        }
    }

    private void loginOff(String token) {
        String tokenKey = createTokenKey(token);
        redisUtils.del(tokenKey);
    }

    @Override
    public U getUserByToken(Class<U> clazz) {
        String token = getToken();
        String tokenKey = createTokenKey(token);
        String userStr = redisUtils.get(tokenKey, "");
        if (StringUtils.isNotBlank(userStr)) {
            return JSONObject.parseObject(userStr, clazz);
        }
        return null;
    }

    @Override
    public String createAndSaveToken(U userInfo) {
        try {
            String token = createToken(userInfo);
            saveToCookie(token);
            return token;
        } catch (Exception e) {
            logger.error("token异常createAndSaveToken():" + e);
            throw e;
        }
    }

    private void saveToCookie(String token) {
        logger.info("开始创建token:" + token);
        HttpServletResponse resp = getResponse();
        //设置cookie
        Cookie cookie = new Cookie(tokenManagerConfig.getCookieKey(), token);

        cookie.setMaxAge(tokenManagerConfig.getExpires(token));
        cookie.setPath("/");
        resp.addCookie(cookie);
    }

    private void clearCookieToken() {
        HttpServletResponse resp = getResponse();
        //设置cookie
        Cookie cookie = new Cookie(tokenManagerConfig.getCookieKey(), "");
        cookie.setMaxAge(0);
        cookie.setPath("/");
        resp.addCookie(cookie);
    }

    private String createTokenKey(String token) {
        return tokenManagerConfig.getKeyPrefix() + token;
    }


    private String createToken(U userInfo) {
        Objects.requireNonNull(userInfo, "用户信息不能为空");
        //使用uuid作为源token
        String token = this.tokenUserLoginHandler.loginAndCreateToken(userInfo);
        String tokenKey = createTokenKey(token);
        logger.info("用户登录信息缓存{}:"+JSONObject.toJSONString(userInfo));
        redisUtils.set(tokenKey, JSONObject.toJSONString(userInfo), tokenManagerConfig.getExpires(token));
        return token;
    }

    /**
     * 获取上下午的response
     * @return
     */
    private HttpServletResponse getResponse() {
        return ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getResponse();
    }

    /**
     * 获取上下文的request
     * @return
     */
    private HttpServletRequest getRequest() {
        return ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getRequest();
    }

    /**
     * 获取请求中的token
     * @return
     */
    private String getToken() {
        HttpServletRequest request = getRequest();

        // 先从请求参数中获取token
        String token = request.getParameter(tokenManagerConfig.getCookieKey());
        // 如果没有获取到,则从head中获取
        if (StringUtils.isBlank(token)) {
            token = request.getHeader(tokenManagerConfig.getCookieKey());
        }
        // 如果没有获取到,则从cookie中获取
        if (StringUtils.isBlank(token)) {
            token = getCookie(request, tokenManagerConfig.getCookieKey());
        }

        return token;

    }

    /**
     * 从response中获取指定cookie名的cookie值
     * @param request
     * @param cookieKey
     * @return
     */
    private String getCookie(HttpServletRequest request, String cookieKey) {
        Cookie[] cookies = request.getCookies();
        if (cookies == null) {
            return "";
        }
        for (Cookie cookie : cookies) {
            if (cookie.getName().equals(cookieKey)) {
                return cookie.getValue();
            }
        }

        return "";
    }

    @Override
    public void saveCurrentLoginUser(U currentUser) {
        currentLoginUser.set(currentUser);
    }

    private U getCurrentLoginUser(){
        return currentLoginUser.get();
    }
}
```

创建并保存token：生成token,保存登录用户信息到redis中和保存token到cookie中

```java
@Override
public String createAndSaveToken(U userInfo) {
    try {
        String token = createToken(userInfo);
        saveToCookie(token);
        return token;
    } catch (Exception e) {
        logger.error("token异常createAndSaveToken():" + e);
        throw e;
    }
}
```

### 3.禁止用户多地登录扩展处理器:DuplicateCheckUserLoginHandler

```java
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang.StringUtils;

@Slf4j
public class DuplicateCheckUserLoginHandler implements TokenUserLoginHandler<AuthUser> {
    private AbstractRedisCache redisUtils;
    private RedisTokenManagerConfig tokenManagerConfig;
    private final String userTokenRedisKeyTemplate = "logincheck:";
    private final String appUserTokenRedisKeyTemplate = "app:logincheck:";

    public DuplicateCheckUserLoginHandler(AbstractRedisCache redisUtils, RedisTokenManagerConfig tokenManagerConfig) {
        this.redisUtils = redisUtils;
        this.tokenManagerConfig = tokenManagerConfig;
    }

    @Override
    public String loginAndCreateToken(AuthUser loginUser) {
        String loginKey = getRedisKey(loginUser.getUserId(), loginUser.isApp());
        String token = redisUtils.get(loginKey,"");
        if (StringUtils.isNotBlank(token)){
            redisUtils.del(createTokenKey(token));
            log.info(String.format("用户%s对应的token[%s]被强制登出",loginUser.getUserName(),token));
        }
        String newToken =  StringConvertUtils.shortUuid();
        if (loginUser.isApp()){
            newToken = AuthorizationConstants.IS_APP_KEY + newToken;
        }
        redisUtils.set(loginKey,newToken,getExpires(loginKey));
        return newToken;
    }

    @Override
    public int extend(AuthUser loginUser) {
        String loginKey = getRedisKey(loginUser.getUserId());
        if (redisUtils.exists(loginKey)) {
            redisUtils.expire(loginKey, getExpires(loginKey));
        }
        return loginUser.isApp() ? tokenManagerConfig.getExpires() * 24 * 7 : tokenManagerConfig.getExpires();
    }

    @Override
    public void loginOff(AuthUser loginUser) {
        String loginKey = getRedisKey(loginUser.getUserId());
        redisUtils.del(loginKey);
    }

    private String getRedisKey(long userId){
        return this.getRedisKey(userId, false);
    }

    private String getRedisKey(long userId, boolean isApp){
        if (isApp) {
            return appUserTokenRedisKeyTemplate + userId;
        } else {
            return userTokenRedisKeyTemplate + userId;
        }
    }

    private String createTokenKey(String token) {
        return tokenManagerConfig.getKeyPrefix() + token;
    }

    private int getExpires(String key){
        return key.contains("app") ? tokenManagerConfig.getExpires() * 24 * 7 : tokenManagerConfig.getExpires();
    }

}
```

RedisTokenManager的spring上下文加载器:AppAutoConfiguraction

```java
@Bean
public TokenManager<AuthUser> tokenManager(AbstractRedisCache abstractRedisCache,RedisTokenManagerConfig redisTokenManagerConfig){
	DuplicateCheckUserLoginHandler duplicateCheckUserLoginHandler = new DuplicateCheckUserLoginHandler(abstractRedisCache, redisTokenManagerConfig);
	return new RedisTokenManager<>(abstractRedisCache,redisTokenManagerConfig,duplicateCheckUserLoginHandler);
}
```


