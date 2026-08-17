---
title: Go错误处理
date: 2024-06-08 15:00:00
tags:
  - golang
---

# 错误处理

Go **没有异常机制**（try-catch），错误通过返回值 `error` 显式传递，强调"错误也是值"。

## error 接口

```go
type error interface {
    Error() string
}
```

任何实现了 `Error() string` 的类型都是 error。

## 基本用法

```go
func readConfig(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("read config: %w", err)
    }
    return data, nil
}

data, err := readConfig("app.yaml")
if err != nil {
    log.Fatal(err)
}
```

## 创建错误

```go
// 简单错误
err := errors.New("something went wrong")

// 格式化错误
err = fmt.Errorf("user %d not found", userID)

// Go 1.13+ 包装错误，保留错误链
err = fmt.Errorf("load user: %w", originalErr)
```

## errors.Is 与 errors.As

```go
import "errors"

var ErrNotFound = errors.New("not found")

func find(id int) error {
    return fmt.Errorf("query db: %w", ErrNotFound)
}

err := find(1)

// 判断是否为特定错误
if errors.Is(err, ErrNotFound) {
    // 处理未找到
}

// 提取特定类型的错误
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    fmt.Println(pathErr.Path)
}
```

## 自定义错误类型

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

func validate(u User) error {
    if u.Name == "" {
        return &ValidationError{Field: "name", Message: "required"}
    }
    return nil
}
```

## panic 与 recover

`panic` 引发运行时恐慌，一般用于**不可恢复**的程序错误；`recover` 可在 defer 中捕获 panic：

```go
func safeDivide(a, b int) (result int, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic recovered: %v", r)
        }
    }()
    return a / b, nil
}
```

**最佳实践**：

- 业务逻辑错误 → 返回 `error`
- 编程错误、不可恢复状态 → `panic`（如 init 失败）
- 库代码避免 panic，除非文档明确说明

## 错误处理风格

```go
// 推荐：早返回
func process() error {
    if err := step1(); err != nil {
        return err
    }
    if err := step2(); err != nil {
        return err
    }
    return step3()
}

// 避免：深层嵌套
func processBad() error {
    if err := step1(); err == nil {
        if err := step2(); err == nil {
            return step3()
        } else {
            return err
        }
    } else {
        return err
    }
}
```

## 小结

- 用 `error` 返回值处理可预期错误，不要滥用 panic
- `fmt.Errorf("...: %w", err)` 包装错误，保留上下文
- `errors.Is` / `errors.As` 判断和提取错误
- 自定义错误类型携带更多业务信息
