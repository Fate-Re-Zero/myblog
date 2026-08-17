---
title: 自定义转发Servlet
date: 2021-09-02 16:44:26
tags:
---

### 自定义转发servlet，用来处理前端发送过来的请求
```java
import static com.banksteel.openerp.commons.permission.PermissionContext.checkIsLegalReq;
import static com.banksteel.openerp.commons.permission.PermissionContext.checkIsUrlReq;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.servlet.DispatcherServlet;

import com.alibaba.fastjson.JSONObject;
import com.banksteel.openerp.commons.framework.entiy.RequestEntiy;
import com.banksteel.openerp.commons.framework.entiy.RequestEntiyFace;
import com.banksteel.openerp.commons.framework.entiy.ResponseEntity;
import com.banksteel.openerp.commons.framework.exception.CommondNotFoundException;
import com.banksteel.openerp.commons.permission.PermissionContext;
import com.banksteel.openerp.commons.permission.PermissionRequest;

/**
 * @description:自定义转发servlet，用来处理前端发送过来的请求
 * @projectName:openerp-commons
 * @className:CustomDispatcherServlet.java
 * @author:xuxiepeg@banksteel
 * @createTime:2016年6月29日 下午1:55:58
 * @version 1.0
 */
public class CustomDispatcherServlet extends DispatcherServlet {
    public static final String QUOT = "&quot;";
    private static final long serialVersionUID = -3983568685367864966L;
    public static final String REQUEST_COMMAND = "request_command";
    private static Logger LOGGER = LoggerFactory.getLogger(CustomDispatcherServlet.class);
    private static final List<String> PARAMS = new ArrayList<String>();

    static {
        PARAMS.add("announcementContent");
        PARAMS.add("xmlFilePath");
    }

    @Override
    protected void doService(HttpServletRequest request, HttpServletResponse response) throws Exception {
        String requestUrl = request.getRequestURI();
        String method = request.getMethod();
        try{
            request.setCharacterEncoding("UTF-8");
            if (!checkIsUrlReq(PermissionContext.getApiPath(requestUrl) , method) && checkIsLegalReq(requestUrl)) {
                // 非过滤URL
                RequestEntiyFace requestEntiyface = null;
                RequestEntiy requestEntiy = getRequestEntiy(request);
                if (requestEntiy != null) {
                    // 请求参数可以正常解析
                    request.setAttribute(REQUEST_COMMAND, requestEntiy.getCommand());
                    String command = requestEntiy.getCommand();
                    LOGGER.info("请求命令：" + command);
                    if (StringUtils.isBlank(command)){
                        throw new CommondNotFoundException(String.format("请求[%s,%s]不为url直接访问的请求,请求参数中不存在command",method,requestUrl));
                    }

                    if (!PermissionContext.containsCommand(command)){
                        throw new CommondNotFoundException("命令:"+command);
                    }
                    requestEntiyface = doRequestPath(requestEntiy);
                    if (requestEntiyface != null) {
                        request = new HttpResquestWrapper(request, requestEntiyface);
                    }
                }
            }
            super.doService(request, response);
        }catch(Exception e) {
            LOGGER.error(String.format("请求[%s,%s]分发失败",method,requestUrl),e);
            ResponseEntity result=returnException("4001","请求分发失败"+","+e.getMessage(),"");
            response.setContentType("application/json; charset=UTF-8");
            try
			{
            	response.getWriter().write(JSONObject.toJSONString(result));
			} catch (Exception e2)
			{
				throw new IOException(e2.getMessage());
			}
        }
    }

    protected RequestEntiyFace doRequestPath(RequestEntiy requestEntiy) {
            RequestEntiyFace requestEntiyface = new RequestEntiyFace();
            String command = requestEntiy.getCommand();

            PermissionRequest request = PermissionContext.getPermissionByCommand(command);

            if (request.getRequestMethod() != null){
                requestEntiyface.setMethod(request.getRequestMethod().toString());// 设置请求方法
            }

            requestEntiyface.setURI(request.getRequestPath());// 设置请求路径
            Map<String, String> heads = new HashMap<String, String>();
            heads.put("x-openerp-token", requestEntiy.getAccessToken());
            requestEntiyface.setHeads(heads);

            if (StringUtils.startsWith(requestEntiy.getData(),"{")){ // 说明data数据是对象
                JSONObject json = JSONObject.parseObject(requestEntiy.getData());
                json = (JSONObject) objectFilter(json);
                requestEntiy.setData(json.toJSONString());
                Map<String, String[]> params = new HashMap<String, String[]>();
                for (String key : json.keySet()) {
                    String[] param = new String[1];
                    param[0] = json.get(key) + "";
                    params.put(key, param);
                }
                requestEntiyface.setGetParam(params);
            }
            requestEntiyface.setBodyData(requestEntiy.getData());
            return requestEntiyface;
    }

    /**
     *
     * @description:获取请求数据为对象
     * @param request
     * @return
     * @throws Exception
     * @author:商家进销存项目组 xuxp
     * @createTime:2016年8月8日 下午2:09:04
     */
    private RequestEntiy getRequestEntiy(HttpServletRequest request) throws Exception {
        String encode = "UTF-8";
        InputStream inputStream = request.getInputStream();
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        byte[] tmp = new byte[2048];
        int i = inputStream.read(tmp);
        while (i > 0) {
            baos.write(tmp, 0, i);
            i = inputStream.read(tmp);
        }
        String value = new String(baos.toByteArray(), encode);
        if(value != null && !"".equals(value)){
            RequestEntiy requestEntiy = JSONObject.parseObject(value, RequestEntiy.class);
            requestEntiy.setData(requestEntiy.getData());
            return requestEntiy;
        }
       return null;
    }

    /**
     * @description:过滤特殊字符串
     * @param needToFormat
     * @return
     * @author:商家进销存项目组 xuxp
     * @createTime:2016年8月8日 下午2:06:54
     */
    public static String formatHtml(String needToFormat) {
        if (needToFormat != null && needToFormat.length() > 0) {
            needToFormat = needToFormat.replace("<script>", "");
            needToFormat = needToFormat.replace("&", "&amp;");
            needToFormat = needToFormat.replace("\"", QUOT);
            needToFormat = needToFormat.replace("“", QUOT);
            needToFormat = needToFormat.replace("”", QUOT);
            needToFormat = needToFormat.replace("<", "&lt;");
            needToFormat = needToFormat.replace(">", "&gt;");
            needToFormat = needToFormat.replace("'", "&#39;");
            needToFormat = needToFormat.replace("\r\n", "");
            return needToFormat;
        }
        return "";
    }

    private Object objectFilter(Object json) {
        Object result = null;
        if (json == null) {
            result = "";
        }
        else if (json instanceof JSONObject) {
            JSONObject jsono = (JSONObject) json;
            Set<String> keys = jsono.keySet();
            if (!keys.isEmpty())
            {
                for (String k : keys)
                {
                    if (PARAMS.indexOf(k) != -1)
                    {
                        continue;
                    }
                    jsono.put(k, objectFilter(jsono.get(k)));
                }
            }
            result = jsono;
        }
        else if (json instanceof String) {
            result = formatHtml(json.toString());
        }
        else {
            result = json;
        }
        return result;
    }
    private ResponseEntity returnException(String code, String mess, Object data) {
        ResponseEntity responseEntity = new ResponseEntity();
        responseEntity.setCode(Integer.parseInt(code));
        Calendar calendar = Calendar.getInstance(Locale.CHINA);
        responseEntity.setTimeStamp(calendar.getTimeInMillis());
        responseEntity.setResult("exception");
        responseEntity.setMess(mess);
        responseEntity.setData(data);
        return responseEntity;
    }

}
```

### 改变请求使得他适应前端发送的请求
```java
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.Map;

import javax.servlet.ReadListener;
import javax.servlet.ServletInputStream;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletRequestWrapper;

import com.banksteel.openerp.commons.framework.entiy.RequestEntiyFace;
import com.banksteel.openerp.commons.utils.Func;

/**
 * @description:改变请求使得他适应前端发送的请求
 * @projectName:openerp-commons
 * @className:HttpResquestWrapper.java
 * @author:xuxiepeg@banksteel
 * @createTime:2016年6月29日 下午1:56:43
 * @version 1.0
 */
public class HttpResquestWrapper extends HttpServletRequestWrapper
{

	private RequestEntiyFace requestEntiyface = null;

	public HttpResquestWrapper(HttpServletRequest request, RequestEntiyFace requestEntiyface) throws IOException
	{
		super(request);
		this.requestEntiyface = requestEntiyface;
	}

	@Override
	public String getMethod()
	{
		return requestEntiyface.getMethod();
	}

	@Override
	public String getHeader(String name)
	{
		String value = super.getHeader(name);
		if (!Func.isNotEmpty(name))
		{
			value = requestEntiyface.getHeads().get(name);
		}
		return value;
	}

	@Override
	public String getPathInfo()
	{
		return requestEntiyface.getURI();
	}

	@Override
	public String getRequestURI()
	{
		return requestEntiyface.getURI();
	}

	@Override
	public StringBuffer getRequestURL()
	{
		return super.getRequestURL().append(requestEntiyface.getURI());
	}

	@Override
	public String getServletPath()
	{
		return requestEntiyface.getURI();
	}

	@Override
	public String getQueryString()
	{
		return queryString(requestEntiyface.getGetParam());
	}

	@Override
	public String getParameter(String name)
	{
		String param = null;
		if (requestEntiyface.getGetParam() != null)
		{
			String[] params = requestEntiyface.getGetParam().get(name);
			if (params != null)
				param = params[0];
		}
		return param;
	}

	@Override
	public String getContentType()
	{
		return "application/json";
	}

	@Override
	public Map<String, String[]> getParameterMap()
	{
		return requestEntiyface.getGetParam();
	}

	/**
	 * requestparam注解会调用的方法 
	 * @description:
	 * @param name
	 * @return
	 * @author:xuxiepeg@banksteel
	 * @createTime:2016年6月30日 下午1:48:34
	 */

	@Override
	public String[] getParameterValues(String name)
	{
		String[] params = null;
		if (requestEntiyface.getGetParam() != null)
		{
			 params = requestEntiyface.getGetParam().get(name);
		}
		return params;
	}

	@Override
	public ServletInputStream getInputStream() throws IOException
	{
		final ByteArrayInputStream bais = new ByteArrayInputStream(requestEntiyface.getBodyData().getBytes("UTF-8"));
		ServletInputStream inputStream = new ServletInputStream(){
			@Override
			public boolean isFinished() {
				return false;
			}

			@Override
			public boolean isReady() {
				return false;
			}

			@Override
			public void setReadListener(ReadListener readListener) {
				throw new UnsupportedOperationException();
			}

			public int read() throws IOException
			{
				return bais.read();
			}
		};
		return inputStream;
	}
    /**
     *
     * @description:组合查询字符串
     * @param map
     * @return
     * @author:商家进销存项目组 xuxp
     * @createTime:2017年1月11日 上午11:08:36
     */
	private String queryString(Map<String, String[]> map)
	{
		String value = "?";
		if (map != null && !map.isEmpty())
		{
			for (String key : map.keySet())
			{
				value = value + key + "=" + map.get(key) + "&";
			}
		}
		if (value.endsWith("&"))
		{
			value = value.substring(0, value.length() - 1);
		}
		return value;
	}

}
```
