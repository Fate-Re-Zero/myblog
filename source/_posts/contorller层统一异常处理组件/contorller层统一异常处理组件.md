---
title: contorller层统一异常处理组件
date: 2020-06-25 19:39:22
tags:
---

### 实现原理: 
异常结果拦截逻辑 
contorller层统一异常处理组件是通过spring的ControllerAdvice和ExceptionHandler来 拦截系统controller方法执行抛异常的请求，然后对异常结果做统一的封装，底层还是spring的aop实现。

### 异常处理逻辑： 
配置文件指定异常处理策略：在系统启动时，加载exceptionCode.properties配置文件来 指定对特定异常进行统一错误响应码、统一错误消息的封装策略(通过 exceptionCode.properties指定的方式后续需要去掉)。 继承BuzzErrorException指定异常处理策 

### 异常处理类解析： 业务异常类BuzzErrorException 
在我们进行业务处理时，绝大多数时不会对业务执行过程中抛出的异常进行捕获后进行特殊 的业务处理，而是直接抛出，所以BuzzErrorException通过基础RuntimeException，这样 业务系统抛出的业务异常不要每次都去捕获后又原封不动抛出，或在方法签名上加上一个很长的异常列表。 在实现自己的业务异常类时需要继承BuzzErrorException，并且可以通过errorCode来指定返回给前端的错误码

```java
/**
 * 〈一句话功能简述〉<br>
 * Description: 统一业务异常处理类
 */
public class BuzzErrorException extends RuntimeException {
    private int errorCode = 500;

    public BuzzErrorException() {
        this("未知异常");
    }

    public BuzzErrorException(String message) {
        super(message);
    }

    public BuzzErrorException(String message, Throwable cause) {
        super(message, cause);
    }

    public BuzzErrorException(Throwable cause) {
        super(cause);
    }

    public BuzzErrorException(int errorCode) {
        this(errorCode,"未知异常");
    }

    public BuzzErrorException(String message, Throwable cause, boolean enableSuppression, boolean writableStackTrace) {
        super(message, cause, enableSuppression, writableStackTrace);
    }

    public BuzzErrorException(int errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public BuzzErrorException(int errorCode,String message, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }

    public BuzzErrorException(int errorCode,Throwable cause) {
        super(cause);
        this.errorCode = errorCode;
    }

    public int getErrorCode() {
        return errorCode;
    }

    public void setErrorCode(int errorCode) {
        this.errorCode = errorCode;
    }
}
```

### controller统一业务异常处类:GlobalExceptionHandler 
统一异常处理入口方法： 在拦截到controller方法执行异常时，会通过执行所抛出的异常生成异常信息和响应错误码 包装到GlobalExceptionHandler.ErrorMessage 类中，然后包装成响应结果对象返回给前端：

```java
@ExceptionHandler(value = Exception.class)
public ModelAndView defaultErrorHandler(HttpServletRequest request,HttpServletResponse response, Exception ex) throws Exception {
	logger.error(ex.getMessage(), ex);
	ErrorMessage mess = getMessage(ex);
	ResponseEntity result = returnException(mess);
	try {
		response.setContentType("text/plain; charset=UTF-8");
		response.getWriter().write(JSONObject.toJSONString(result));
	} catch (IOException e) {
		logger.error("返回异常",e.getMessage());
	}
	return new ModelAndView();
}
```

### 根据异常对象生成异常结果对象ErrorMessage: 
生成异常结果对象的步骤如下： 
1.通过配置文件指定的异常处理策略来生成异常结果对象;
2.如果是BuzzErrorException的子类，则通过BuzzErrorException的errorCode和 message来生成异常结果对象;
3.如果不为BuzzErrorException的子类但为包装异常类，则通过包装的异常类生成异常结果对象;
4.如果为其他情况，就按照Exception类生成默认的系统异常结果对象。

```java
private ErrorMessage getMessage(Throwable th) {
	ErrorMessage mess = null;
	if (th instanceof BuzzErrorException){
		BuzzErrorException buzzErrorException = (BuzzErrorException)th;
		mess = new ErrorMessage(buzzErrorException.getErrorCode(),buzzErrorException.getMessage());
	} else if (th instanceof BncErrorException) {
		BncErrorException bncErrorException = (BncErrorException)th;
		mess = new ErrorMessage(4002,bncErrorException.getMessage());
	} else if (th.getCause() != null){
		mess = getMessage(th.getCause());
	}else {
		ErrorMsgDetail errorMsgDetail = getErrorMsgDetail(th);
		String exceptionMsg = errorMsgDetail.getExceptionMsg();
		boolean hasMsg = StringUtils.isBlank(exceptionMsg) || exceptionMsg.equals("null");
		mess = new ErrorMessage(500, hasMsg ? "系统异常,请联系管理员!" : exceptionMsg, errorMsgDetail);
	}
	return mess;
}
```