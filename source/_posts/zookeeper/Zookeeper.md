---
title: Zookeeper
date: 2022-09-25 22:30:38
tags:
---

### 理解

小岛(Island)——ZK Server Cluster

议员(Senator)——ZK Server

提议(Proposal)——ZNode Change(Create/Delete/SetData…)

提议编号(PID)——Zxid(ZooKeeper Transaction Id)

正式法令——所有ZNode及其数据

总统——ZK Server Leader

### ZAB协议
原子广播协议: 原子,要么成功,要么失败;广播：过半机制;
队列：FIFO,顺序性; 队列能够保证消息的顺序性;

### Zookeeper分布式锁
首先要明确分布式锁要解决的：几个问题; (准确快速和压力)
1. 所有client只能有一个人能够获取到锁;
2. 锁释放问题,(获取锁的client异常了该如何释放锁和执行完毕释放锁);
3. 锁过期了该如何处理;
4. 获取到锁后执行的业务代码是否要加上分布式事务(可能会少卖);
5. 锁释放了该如何通知其他客户端;
	5.1 主动轮询,心跳 --- 弊端：延迟,压力;
	5.2 watch 解决延迟问题 --- 弊端：压力;
	5.3 sequence + watch：watch前一个客户端, 如果锁释放,zk只给前一个客户端发事件回调;