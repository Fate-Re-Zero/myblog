---
title: redis学习总结
date: 2020-03-22 18:49:15
tags:
---

redis String类型的数据结构
set key1 value 设置值

get key1 获取值

keys * 获取所有的key
 
EXISTS key1 判断某一个key是否存在

APPEND key1 'hello'  如果当前key存在则追加字符串，如果当前key不存在则设置一个新值

set views 0

set artic:100:views 0  设置第100号文章的浏览量为 0

incr views  ---- 1  自增长1

incr views  ---- 2

decr view   ---- 1  自减1

decr view   ---- 0

set key1 'hello, lixiang'

GETRANGE key1 0 3  ----'hell'     获取字符串[0,3]

SETRANGE key1 1 xx ----'hxxl0, lixiang' 替换指定位置开始的字符串

setex key1 30 'hello' 设置过期时间,单位为秒

ttl key1  当前key的剩余时间

setnx mykey 'redis' 如果mykey不存在，则创建； 如果mykey存在，则创建失败 (分布式锁中使用较多)

mset k1 v1 k2 v2 k3 v3  批量设置值

mget k1 k2 k3  批量获取值

msetnx k1 v1 k4 v4 是一个原子性的操作，key存在则设置成功，要么一起成功，要么一起失败

get k4  ------ null

设置对象
set user:1 {name:zhangsan,age:23}  设置user对象

get user:1

这里的key是一个巧妙地设计

mset user:1:name zhangsan user:1:age 23

mget user:1:name user:1:age  ---- zhangsan , 23

getset db redis  ---- null  如果不存在则设置值，返回null

get db  ---- redis

getset db mysql  ---- redis 如果存在,获取原来的值，并设置新值（比较并交换）

get db  ---- mysql

String类似的使用类似的使用场景：（value除了是字符串还可以是数字)
1.计数器(比如阅读量)
2.统计多单位数量
3.粉丝数
4.对象缓存存储

List数据类型：（可以存在重复的值）
在redis里面，可以把list设计成栈，队列，阻塞队列

LPUSH list one ---- 将一个值或者多个值，插入到列表头部（左）

LPUSH list two

LRANGE list 0 -1  ---- one, two

RPUSH list rigth ---- 将一个值或者多个值，插入到列表尾部（右）

LPOP list  ---- 移除列表的第一个元素

RPOP list  ----  移除列表的最后一个元素

LINDEX list 1 ---通过下标获取list中的某一个值

LREM list 1 one  ---- 移除list集合中指定个数的value,精确匹配

ltrim mylist 1 2 ---- 通过下标截取指定的长度，这个list已经被改变了，截断了只剩下截取的元素




rpush mylist 'hello'

rpush mylist 'hello1' 

rpush mylist 'hello2'

rpoplpush mylist myotherlist  ---- 移除列表的最后一个元素，将他移动到新的列表中
返回hello2

lrange mylist 0 -1  ---- hello, hello1

lrange myotherlist 0 -1  ---- hello2


lset list 0 hell5 ---- 将列表中指定下标的值替换为另一个值，更新操作

如果列表不存在，则报错， 如果对应的下标的值不存在，则报错

linsert list before 'world' 'other'  ---- 将某个具体的value插入到列表的前面或者后面

linsert list after 'world' 'new'


set数据结构

sadd myset 'hello'



