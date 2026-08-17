---
title: Spring MVC 源码学习
date: 2020-03-22 18:39:49
tags: MVC
---

Spring MVC请求处理的流程(以下源码中注释了每一步干了那些事情)
![](/images/MVC执行流程.jpg)
```java
protected void doDispatch(HttpServletRequest request, HttpServletResponse response) throws Exception {
        HttpServletRequest processedRequest = request;
        HandlerExecutionChain mappedHandler = null;
        boolean multipartRequestParsed = false;
        WebAsyncManager asyncManager = WebAsyncUtils.getAsyncManager(request);

        try {
            try {
                ModelAndView mv = null;
                Object dispatchException = null;

                try {
                    // 1.检查是否是文件上传请求
                    processedRequest = this.checkMultipart(request);
                    multipartRequestParsed = processedRequest != request;

                    // 2.找到处理当前请求的处理器
                    mappedHandler = this.getHandler(processedRequest);
                    if (mappedHandler == null) {
                        // 如果没有找到则直接抛异常
                        this.noHandlerFound(processedRequest, response);
                        return;
                    }
                    // 3.拿到当前处理器所有方法的适配器（相当于反射工具）
                    HandlerAdapter ha = this.getHandlerAdapter(mappedHandler.getHandler());
                    // 4.获取到方法的请求方式
                    String method = request.getMethod();
                    boolean isGet = "GET".equals(method);
                    if (isGet || "HEAD".equals(method)) {
                        long lastModified = ha.getLastModified(request, mappedHandler.getHandler());
                        if ((new ServletWebRequest(request, response)).checkNotModified(lastModified) && isGet) {
                            return;
                        }
                    }

                    if (!mappedHandler.applyPreHandle(processedRequest, response)) {
                        return;
                    }

                    // 5.使用适配器执行目标将目标方法执行完后的返回值作为视图名，不管目标方法是何种类型的返回值，最终适配器执行完后都是将执行后的信息封装到ModelAndView中并返回，
                    mv = ha.handle(processedRequest, response, mappedHandler.getHandler());
                    if (asyncManager.isConcurrentHandlingStarted()) {
                        return;
                    }

                    // 6.如果没有视图名称返回一个默认的视图名称
                    this.applyDefaultViewName(processedRequest, mv);
                    mappedHandler.applyPostHandle(processedRequest, response, mv);
                } catch (Exception var20) {
                    dispatchException = var20;
                } catch (Throwable var21) {
                    dispatchException = new NestedServletException("Handler dispatch failed", var21);
                }

                // 7.将方法最终执行完成后的ModelAndView转发到对应的页面，而且ModelAndView中的数据可以在请求域中获取
                this.processDispatchResult(processedRequest, response, mappedHandler, mv, (Exception)dispatchException);
            } catch (Exception var22) {
                this.triggerAfterCompletion(processedRequest, response, mappedHandler, var22);
            } catch (Throwable var23) {
                this.triggerAfterCompletion(processedRequest, response, mappedHandler, new NestedServletException("Handler processing failed", var23));
            }

        } finally {
            if (asyncManager.isConcurrentHandlingStarted()) {
                if (mappedHandler != null) {
                    mappedHandler.applyAfterConcurrentHandlingStarted(processedRequest, response);
                }
            } else if (multipartRequestParsed) {
                this.cleanupMultipart(processedRequest);
            }

        }
    }


```

结合源码详细解析一下上述主要步骤：
// 2.如何找到处理当前请求的处理器
mappedHandler = this.getHandler(processedRequest)返回目标方法的执行链（内部还封装了拦截器等信息）
handlerMappings:IOC容器启动时创键Controller对象扫描到每个处理器都能处理那些请求，保存在HanlerMaping的handlerMap中，每过来一个请求，拿到该请求对应的HandlerMapping的请求映射信息就行；
下面这段就是根据请求获取请求对应的HandlerMapping映射信息的源码
（目前MVC支持RequestMappingHandlerMapping、 BeanNameUrlHandlerMapping、 RouterFunctionMapping三种)

```java
@Nullable
    protected HandlerExecutionChain getHandler(HttpServletRequest request) throws Exception {
        if (this.handlerMappings != null) {
            for (HandlerMapping mapping : this.handlerMappings) {
                HandlerExecutionChain handler = mapping.getHandler(request);
                if (handler != null) {
                    return handler;
                }
            }
        }
        return null;
    }
```


// 3.如何拿到当前处理器所有方法的适配器（相当于反射工具）
（目前MVC支持RequestMappingHandlerAdapter、 HandlerFunctionAdapter、 HttpRequestHandlerAdapter、 SimpleControllerHandlerAdapter四种)
```java
protected HandlerAdapter getHandlerAdapter(Object handler) throws ServletException {
        if (this.handlerAdapters != null) {
            for (HandlerAdapter adapter : this.handlerAdapters) {
                if (adapter.supports(handler)) {
                    return adapter;
                }
            }
        }
        throw new ServletException("No adapter for handler [" + handler +
                "]: The DispatcherServlet configuration needs to include a HandlerAdapter that supports this handler");
    }
```

DispatcherServlet中的几种引用类型的属性：Spring MVC的九大组件
```java
    /** MultipartResolver used by this servlet. */
    @Nullable
    private MultipartResolver multipartResolver;  

    /** LocaleResolver used by this servlet. */
    @Nullable
    private LocaleResolver localeResolver;

    /** ThemeResolver used by this servlet. */
    @Nullable
    private ThemeResolver themeResolver;

    /** List of HandlerMappings used by this servlet. */
    @Nullable
    private List<HandlerMapping> handlerMappings;

    /** List of HandlerAdapters used by this servlet. */
    @Nullable
    private List<HandlerAdapter> handlerAdapters;

    /** List of HandlerExceptionResolvers used by this servlet. */
    @Nullable
    private List<HandlerExceptionResolver> handlerExceptionResolvers;

    /** RequestToViewNameTranslator used by this servlet. */
    @Nullable
    private RequestToViewNameTranslator viewNameTranslator;

    /** FlashMapManager used by this servlet. */
    @Nullable
    private FlashMapManager flashMapManager;

    /** List of ViewResolvers used by this servlet. */
    @Nullable
    private List<ViewResolver> viewResolvers;

```

Spring MVC九大组件初始化

```java
/**
     * This implementation calls {@link #initStrategies}.
     */
    @Override
    protected void onRefresh(ApplicationContext context) {
        initStrategies(context);
    }

    /**
     * Initialize the strategy objects that this servlet uses.
     * <p>May be overridden in subclasses in order to initialize further strategy objects.
     */
    protected void initStrategies(ApplicationContext context) {
        initMultipartResolver(context);
        initLocaleResolver(context);
        initThemeResolver(context);
        initHandlerMappings(context);
        initHandlerAdapters(context);
        initHandlerExceptionResolvers(context);
        initRequestToViewNameTranslator(context);
        initViewResolvers(context);
        initFlashMapManager(context);
    }
```





MVC支持Rest风格原理(源码解析)
```java
    public static final String DEFAULT_METHOD_PARAM = "_method";

    private String methodParam = DEFAULT_METHOD_PARAM;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        HttpServletRequest requestToUse = request;
        if ("POST".equals(request.getMethod()) && request.getAttribute(WebUtils.ERROR_EXCEPTION_ATTRIBUTE) == null) {
            String paramValue = request.getParameter(this.methodParam);
            if (StringUtils.hasLength(paramValue)) {
                String method = paramValue.toUpperCase(Locale.ENGLISH);
                if (ALLOWED_METHODS.contains(method)) {
                    requestToUse = new HttpMethodRequestWrapper(request, method);
                }
            }
        }
        filterChain.doFilter(requestToUse, response);
    }

    /**
     * Simple {@link HttpServletRequest} wrapper that returns the supplied method for
     * {@link HttpServletRequest#getMethod()}.
     */
    private static class HttpMethodRequestWrapper extends HttpServletRequestWrapper {

        private final String method;

        public HttpMethodRequestWrapper(HttpServletRequest request, String method) {
            super(request);
            this.method = method;
        }

        @Override
        public String getMethod() {
            return this.method;
        }
    }


    public class HttpServletRequestWrapper extends ServletRequestWrapper implements HttpServletRequest {
        、、、
    }
```

### 从上述源码中可以看到：
MVC实现Rest风格的是通过HiddenHttpMethodFilter这个拦截器实现的，在该拦截器的doFilterInternal方法中通过获取到参数中"method"对应的属性值来拿到请求类型，然后调用HttpMethodRequestWrapper构造方法，而HttpMethodRequestWrapper继承了HttpServletRequest可以看出这里其实就是通过传入的request,method两个参数构造了一个request,而method就是我们所传的参数，从而达到对Rest四种请求方式的支持。

@RequestParam(value = "", required = false, defaultValue = "")
@RequestHeader(value = "", required = false, defaultValue = "")
@CookieValue(value = "", required = false)

Spring MVC解决乱码问题
处理字符编码的Filter一定要在其他Filter之前，不然其他Filter已经获取的请求参数，此时再去处理字符编码没有任何意义
```java
public class CharacterEncodingFilter extends OncePerRequestFilter {

    @Nullable
    private String encoding;

    private boolean forceRequestEncoding = false;

    private boolean forceResponseEncoding = false;

    public boolean isForceResponseEncoding() {
        return this.forceResponseEncoding;
    }


    @Override
    protected void doFilterInternal(
            HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String encoding = getEncoding();
        if (encoding != null) {
            if (isForceRequestEncoding() || request.getCharacterEncoding() == null) {
                request.setCharacterEncoding(encoding);
            }
            if (isForceResponseEncoding()) {
                response.setCharacterEncoding(encoding);
            }
        }
        filterChain.doFilter(request, response);
    }
}
```


Spring MVC如何把数据带给页面
不管是传入Map, Model, MOdelMap,最终都是BindingAwareModelMap在工作，相当于在BindingAwareModelMap中保存的数据都放在请求域中

