---
title: Go Channel与并发模式
date: 2024-06-15 17:00:00
tags:
  - golang
---

# Channel 与并发模式

Channel 是 goroutine 之间通信的管道，类型化、线程安全。

## 基本用法

```go
// 创建
ch := make(chan int)        // 无缓冲
ch := make(chan int, 10)    // 缓冲容量 10

// 发送与接收（阻塞）
ch <- 42       // 发送
v := <-ch      // 接收

// 关闭
close(ch)

// 接收时判断 channel 是否已关闭
v, ok := <-ch
if !ok {
    // channel 已关闭且无数据
}
```

## 无缓冲 vs 有缓冲

| 类型 | 行为 |
| ---- | ---- |
| 无缓冲 | 发送方阻塞直到接收方就绪（同步握手） |
| 有缓冲 | 缓冲区未满时发送不阻塞，满则阻塞 |

```go
ch := make(chan int, 2)
ch <- 1
ch <- 2
// ch <- 3  // 阻塞，缓冲区满
```

## range 遍历 channel

```go
func producer(ch chan<- int) {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    close(ch)  // 生产者负责关闭
}

func consumer(ch <-chan int) {
    for v := range ch {
        fmt.Println(v)
    }
}
```

## 单向 channel

限制 channel 只能发送或接收，编译期约束：

```go
func sendOnly(ch chan<- int) {
    ch <- 1
}

func receiveOnly(ch <-chan int) {
    v := <-ch
    _ = v
}
```

## select 多路复用

同时等待多个 channel 操作：

```go
select {
case msg := <-ch1:
    fmt.Println("from ch1:", msg)
case msg := <-ch2:
    fmt.Println("from ch2:", msg)
case <-time.After(time.Second):
    fmt.Println("timeout")
default:
    fmt.Println("no channel ready")
}
```

## 常见并发模式

### Worker Pool

```go
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }

    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)

    for r := 1; r <= 5; r++ {
        fmt.Println(<-results)
    }
}
```

### Pipeline

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// 使用
for n := range square(gen(1, 2, 3, 4)) {
    fmt.Println(n)
}
```

### Fan-out / Fan-in

多个 goroutine 消费同一 channel（fan-out），多个 channel 合并到一个（fan-in），适合并行处理与结果聚合。

## context 取消

配合 `context` 实现超时与取消（详见 context 使用）：

```go
ctx, cancel := context.WithTimeout(context.Background(), time.Second)
defer cancel()

select {
case <-ctx.Done():
    return ctx.Err()
case result := <-resultCh:
    return result
}
```

## 小结

- channel 用于 goroutine 间安全通信，遵循"谁发送谁关闭"原则
- `select` 处理多 channel 场景
- Worker Pool、Pipeline 是生产环境常见模式
- 避免向已关闭的 channel 发送数据（会 panic）
