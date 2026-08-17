---
title: MySQL索引优化
date: 2022-09-27 14:30:38
tags:
---

### MySQL添加索引的语句
1.添加PRIMARY KEY（主键索引）
mysql>ALTER TABLE table_name ADD PRIMARY KEY (column )

2.添加UNIQUE(唯一索引)
mysql>ALTER TABLE table_name ADD UNIQUE (column)

3.添加INDEX(普通索引)
mysql>ALTER TABLE table_name ADD INDEX index_name (column )

4.添加FULLTEXT(全文索引)
mysql>ALTER TABLE table_name ADD FULLTEXT (column)

5.添加联合索引
mysql>ALTER TABLE table_name ADD INDEX index_name (column1, column2, column3)

6.其他语法
CREATE INDEX index_name ON table_name (column1, column2, column3);


### 高性能索引创建策略
1. 索引列的类型要尽量小
更小的数据类型，也就意味着节省更多的存储空间和更高效的I/0。

2. 索引的选择性
创建索引应该选择选择性/离散性高的列。重复的数据越多,查询时需要扫描的列就越多;

3. 前缀索引
创建前缀索引(主要针对text,很长的varchar类型)
mysql>ALTER TABLE table_name ADD INDEX index_name (column(前缀长度))
缺点：无法适用与order by和group by,也无法做覆盖索引;

4. 后缀索引
MySQL原生并不支持后缀索引。
可以通过在表中添加一个新列，用于保存要被建立后缀索引的字段倒排值，然后建立前缀索引。
查询邮箱后缀。

5. 多列索引
将离散性高的列尽量放在前面;
将使用频率高的列尽量放在前面;


### 高性能索引使用策略
1. 不要在查询条件索引列上做任何操作：比如：计算,sql函数等；
2. 覆盖索引尽量用上：尽量不要使用*
3. 最佳左前缀法则：(由于联合索引在B+树中前面列的顺序对后面列的顺序是有影响的)
	当我们项目有大量的查询同时用到name和age来进行查询,此时可以创建name和age的组合索引,
	select * from emp where name = ? AND age = ?  //走的上索引 --- 这里查询优化器会自动优化查询顺序,name和age更换位置也可以
	select * from emp where age = ?  // 走不上索引
	select * from emp where name = ?  // 走的上索引
4. 不等于要慎用：使用不等于(!= 或者&lt;&gt;)的时候无法使用索引会导致全表扫描
5. 字符类型加引号：隐式类型转换导致索引失效;
6. like条件尽量右模糊：一般模糊查询的话都是字符串类型，右模糊的话还可以利用上索引的前缀,左模糊则用不上;
7. 尽可能按主键顺序插入行：插入已存在数据的中间值,导致页内数据移动导致页分裂;
8. count(※)和count(列)效率几乎一样,但是统计结果会有差别,count(※)会统计含null值的列,count(列)不会统计当前列值为null的列,所以统计结果会有差别;





