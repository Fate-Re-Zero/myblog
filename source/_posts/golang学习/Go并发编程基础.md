---
title: Go并发编程基础
date: 2024-06-11 16:00:00
tags:
  - golang
---

# 并发编程基础

Go 的并发模型基于 **CSP（Communicating Sequential Processes）**：**不要通过共享内存来通信，而要通过通信来共享内存**。

## goroutine

goroutine 是 Go 的轻量级线程，由 Go runtime 调度，创建成本极低：

```go
func say(s string) {
    for i := 0; i < 3; i++ {
        fmt.Println(s)
        time.Sleep(100 * time.Millisecond)
    }
}

func main() {
    go say("world")   // 启动 goroutine
    say("hello")      // 主 goroutine 继续执行
    time.Sleep(time.Second)
}
```

启动 goroutine 只需在函数调用前加 `go` 关键字。

## sync.WaitGroup

等待一组 goroutine 完成：

```go
import "sync"

func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    fmt.Printf("worker %d done\n", id)
}

func main() {
    var wg sync.WaitGroup
    for i := 1; i <= 5; i++ {
        wg.Add(1)
        go worker(i, &wg)
    }
    wg.Wait()
    fmt.Println("all done")
}
```

## sync.Mutex

保护共享数据：

```go
type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}
```

`sync.RWMutex` 支持读写分离：读多写少时性能更好。

## sync.Once

保证函数只执行一次，常用于单例初始化：

```go
var (
    instance *Config
    once     sync.Once
)

func GetConfig() *Config {
    once.Do(func() {
        instance = loadConfig()
    })
    return instance
}
```

## 竞态检测

编译或测试时开启竞态检测器：

```bash
go run -race main.go
go test -race ./...
```

## 常见并发问题

| 问题 | 原因 | 解决 |
| ---- | ---- | ---- |
| 数据竞态 | 多 goroutine 无保护写同一变量 | Mutex / channel |
| goroutine 泄漏 | 阻塞在 channel 上无人接收 | context 取消、超时 |
| 死锁 | 互相等待锁或 channel | 固定加锁顺序、避免循环等待 |

## 小结

- goroutine 是 Go 并发的基础，开销小、数量可多
- `WaitGroup` 等待任务完成，`Mutex` 保护共享状态
- 生产代码务必用 `-race` 检测数据竞态
- 下一章介绍 channel，Go 更推荐的通信方式
