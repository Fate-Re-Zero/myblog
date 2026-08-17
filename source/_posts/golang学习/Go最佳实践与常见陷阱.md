---
title: Go最佳实践与常见陷阱
date: 2024-06-02 22:00:00
tags:
  - golang
---

# 最佳实践与常见陷阱

本章汇总 Go 工程实践中的经验与常见坑，帮助写出更健壮、可维护的代码。

## 代码风格

### go fmt / go vet

提交前必跑：

```bash
go fmt ./...
go vet ./...
```

Go 只有一种官方格式，团队无需争论缩进风格。

### 命名规范

| 类型 | 规范 | 示例 |
| ---- | ---- | ---- |
| 包名 | 小写、简短、单数 | `user`、`httputil` |
| 导出 | 大写开头 | `UserService` |
| 接口 | 单方法接口以 er 结尾 | `Reader`、`Writer` |
| 缩写 | 全大写或全小写 | `HTTPClient`、`userID` |

## 错误处理

```go
// 好：包装上下文
return fmt.Errorf("save user %d: %w", id, err)

// 差：丢失原始错误
return fmt.Errorf("save failed")

// 好：早返回
if err != nil {
    return err
}

// 差：忽略 error
data, _ := os.ReadFile(path)
```

## 并发陷阱

### 1. 循环变量捕获

```go
// 错误：所有 goroutine 可能共享同一个 i
for i := 0; i < 10; i++ {
    go func() {
        fmt.Println(i)  // 可能全部打印 10
    }()
}

// 正确
for i := 0; i < 10; i++ {
    go func(n int) {
        fmt.Println(n)
    }(i)
}
```

### 2. 向已关闭 channel 发送

```go
close(ch)
ch <- 1  // panic
```

### 3. goroutine 泄漏

无接收者的 channel 发送、无 cancel 的阻塞会导致 goroutine 永久阻塞，务必传递 Context。

### 4. Map 并发读写

```go
// panic: concurrent map read and map write
go func() { m["a"] = 1 }()
go func() { _ = m["a"] }()
```

## 内存与性能

### 切片预分配

```go
// 好：已知大小时预分配
s := make([]int, 0, 1000)
for i := 0; i < 1000; i++ {
    s = append(s, i)
}

// 差：频繁扩容
var s []int
for i := 0; i < 1000; i++ {
    s = append(s, i)
}
```

### 字符串拼接

大量拼接用 `strings.Builder`，避免 `+` 产生大量临时对象。

### 避免不必要的指针

小 struct 传值可能比传指针更高效（减少 GC 压力）。

## JSON 与零值

```go
type Config struct {
    Port int `json:"port"`  // 0 无法与"未设置"区分
}

// 用指针表示可选
type Config struct {
    Port *int `json:"port,omitempty"`
}
```

## 项目工程化

```bash
# Makefile 或脚本
go fmt ./...
go vet ./...
go test -race -cover ./...
go build -o bin/app ./cmd/server
```

推荐工具：

| 工具 | 用途 |
| ---- | ---- |
| golangci-lint | 聚合多种 linter |
| air | 热重载开发 |
| delve | 调试 |

## 学习路线建议

```
入门 → 语法 / 数据类型 / 函数
     → 切片 / Map / 结构体 / 接口
     → 错误处理
     → goroutine / channel / context
     → Modules / 标准库 / 测试
     → 微服务框架（Gin、Echo）/ gRPC
     → 源码阅读（net/http、sync、runtime）
```

## 系列目录

| 章节 | 主题 |
| ---- | ---- |
| 1 | Go语言入门与环境搭建 |
| 2 | Go基础语法与数据类型 |
| 3 | Go流程控制与函数 |
| 4 | Go数组切片与Map |
| 5 | Go结构体与方法 |
| 6 | Go接口 |
| 7 | Go错误处理 |
| 8 | Go并发编程基础 |
| 9 | Go Channel与并发模式 |
| 10 | Go Context上下文 |
| 11 | Go包管理与Modules |
| 12 | Go标准库实战 |
| 13 | Go测试与性能分析 |
| 14 | Go最佳实践与常见陷阱（本文） |

## 小结

Go 强调简单、显式、实用。掌握错误处理、并发模型和接口设计，配合良好的测试与工程习惯，即可胜任大多数后端开发任务。持续阅读标准库与优秀开源项目（Kubernetes、Docker、Prometheus）是进阶的最佳路径。
