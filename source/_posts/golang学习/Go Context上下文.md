---
title: Go Context上下文
date: 2024-06-14 18:00:00
tags:
  - golang
---

# Context 上下文

`context` 包用于在 goroutine 树中传递**取消信号、超时、截止时间**以及请求范围的值，是 Go 微服务和 HTTP 服务的标配。

## 核心接口

```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}
    Err() error
    Value(key any) any
}
```

## 创建 Context

```go
import "context"

// 根 context，永不取消
ctx := context.Background()

// 用于不确定父 context 时（如测试）
ctx = context.TODO()

// 带取消
ctx, cancel := context.WithCancel(parent)
defer cancel()  // 调用 cancel() 通知所有子 goroutine 退出

// 带超时
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()

// 带截止时间
deadline := time.Now().Add(10 * time.Second)
ctx, cancel := context.WithDeadline(parent, deadline)
defer cancel()
```

## 取消传播

```go
func doWork(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()  // context.Canceled 或 context.DeadlineExceeded
        default:
            // 执行业务逻辑
            time.Sleep(100 * time.Millisecond)
        }
    }
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    go doWork(ctx)

    time.Sleep(time.Second)
    cancel()  // 通知 doWork 退出
}
```

## HTTP 请求中的 Context

`http.Request` 自带 Context，应在调用链中传递：

```go
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    result, err := queryDB(ctx, "SELECT ...")
    if err != nil {
        if errors.Is(err, context.DeadlineExceeded) {
            http.Error(w, "timeout", http.StatusGatewayTimeout)
            return
        }
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    json.NewEncoder(w).Encode(result)
}

func queryDB(ctx context.Context, sql string) (Result, error) {
    // 将 ctx 传给 database/sql
    row := db.QueryRowContext(ctx, sql)
    // ...
}
```

## 传递请求范围值

```go
type ctxKey string

const traceIDKey ctxKey = "traceID"

func withTraceID(ctx context.Context, id string) context.Context {
    return context.WithValue(ctx, traceIDKey, id)
}

func getTraceID(ctx context.Context) string {
    v, _ := ctx.Value(traceIDKey).(string)
    return v
}
```

**注意**：`WithValue` 仅用于请求链路追踪等场景，不要用来传可选参数，key 应使用自定义类型避免冲突。

## 最佳实践

1. **Context 作为函数第一个参数**：`func Foo(ctx context.Context, ...)`
2. **不要存储 Context 到 struct**，每次调用传入
3. **不要传 nil Context**，不确定时用 `context.TODO()`
4. **Value 不要滥用**，只放请求元数据（traceId、userId）
5. **父 Context 取消时，子 Context 自动取消**

## 小结

- `context` 统一管理 goroutine 生命周期
- `WithCancel` / `WithTimeout` / `WithDeadline` 三种常用变体
- HTTP、数据库、RPC 调用都应传递 Context，支持超时与优雅退出
