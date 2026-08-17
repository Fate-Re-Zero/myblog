---
title: ElasticSearch学习总结
date: 2021-07-26 13:18:09
tags:
---
ElasticSearch安装：
	1.下载地址：https://www.elastic.co/cn/

ElasticSearch基础操作：
(1).索引的基础操作
	1.新增索引（相当于数据库表）：
		![](/images/ES索引新增操作.jpg)
	2.获取索引：
		![](/images/ES获取索引.jpg)
	3.获取所有索引的详细信息
		![](/images/获取所有索引的详细信息.jpg)
	4.删除索引
		![](/images/ES删除索引.jpg)
(2).文档的基础操作
	1.向索引中添加文档（相当于数据库的行）数据：
		新增文档请求体不能为空（错误示例）：
		![](/images/ES新增文档错误实例.jpg)
		正确示例：
		![](/images/ES新增文档.jpg)
		添加文档时自定义ID
		![](/images/添加文档自定义Id.jpg)
	2.ES根据主键查询文档
		![](/images/ES根据主键查询文档.jpg)
	3.ES获取索引下所有的数据
		![](/images/ES获取索引下所有的数据.jpg)
	4.ES修改所有文档的数据
		![](/images/ES修改所有文档的数据.jpg)
	5.ES修改指定文档的数据
		![](/images/ES文档局部修改.jpg)
	6.ES文档的删除
		![](/images/ES删除文档.jpg)

(3).ES复杂查询操作
	1.请求路径中传输查询条件(不推荐，url中加上查询条件在网络传输中是极其容易出现中文乱码)
		![](/images/ES条件查询(url中带条件).jpg)
	2.文档-全量查找
		![](/images/文档-全量查找.jpg)
	3.文档-分页查询
		![](/images/文档-分页查询.jpg)
	4.文档-排序查询
		![](/images/文档-排序查询.jpg)
	5.文档-多条件查询
		![](/images/文档-多条件查询.jpg)
	6.文档-多个条件满足其中之一
		![](/images/文档-多个条件满足其中之一.jpg)
	7.文档-范围查询
		![](/images/文档-范围查询.jpg)
	8.文档-完全匹配
		![](/images/文档-完全匹配.jpg)
	9.文档-高亮查询
		![](/images/文档-高亮查询.jpg)

