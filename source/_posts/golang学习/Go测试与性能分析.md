---
title: Go测试与性能分析
date: 2024-06-10 21:00:00
tags:
  - golang
---

# 测试与性能分析

Go 内置测试框架，无需第三方测试库即可完成单元测试、基准测试和示例测试。

## 单元测试

测试文件命名：`*_test.go`，与被测文件同包。

```go
// mathutil/add.go
package mathutil

func Add(a, b int) int {
    return a + b
}

// mathutil/add_test.go
package mathutil

import "testing"

func TestAdd(t *testing.T) {
    got := Add(2, 3)
    want := 5
    if got != want {
        t.Errorf("Add(2, 3) = %d, want %d", got, want)
    }
}
```

运行：

```bash
go test ./...              # 所有包
go test -v ./mathutil      # 详细输出
go test -run TestAdd       # 指定测试
go test -cover ./...       # 覆盖率
```

## 表驱动测试

Go 社区推荐的测试写法：

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 2, 3, 5},
        {"zero", 0, 0, 0},
        {"negative", -1, 1, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("got %d, want %d", got, tt.expected)
            }
        })
    }
}
```

## 子测试与并行

```go
t.Run("subtest", func(t *testing.T) {
    t.Parallel()  // 并行执行
    // ...
})
```

## 基准测试（Benchmark）

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(i, i+1)
    }
}
```

```bash
go test -bench=. -benchmem ./mathutil
# BenchmarkAdd-8   1000000000   0.25 ns/op   0 B/op   0 allocs/op
```

`-benchmem` 显示内存分配次数，优化性能时重点关注 `allocs/op`。

## 示例测试

示例代码会作为文档展示，也可验证输出：

```go
func ExampleAdd() {
    fmt.Println(Add(1, 2))
    // Output: 3
}
```

## Mock 与接口

Go 测试依赖**接口**实现 mock：

```go
type UserRepo interface {
    Get(id int64) (*User, error)
}

type mockRepo struct{}

func (m *mockRepo) Get(id int64) (*User, error) {
    return &User{ID: id, Name: "test"}, nil
}

func TestService(t *testing.T) {
    svc := NewService(&mockRepo{})
    // 测试 svc...
}
```

常用 mock 工具：testify/mock、gomock。

## pprof 性能分析

```go
import _ "net/http/pprof"

func main() {
    go func() {
        log.Println(http.ListenAndServe(":6060", nil))
    }()
    // 业务逻辑...
}
```

```bash
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
go tool pprof -http=:8080 cpu.prof
```

## 测试最佳实践

1. 测试文件与被测代码同包（白盒）或 `_test` 后缀包（黑盒）
2. 用表驱动测试覆盖多种输入
3. CI 中运行 `go test -race -cover ./...`
4. 基准测试对比优化前后结果
5. 集成测试可用 testcontainers 或 docker-compose

## 小结

- `go test` 是 Go 测试核心，表驱动是标准写法
- Benchmark 衡量性能，pprof 定位瓶颈
- 面向接口设计便于 mock 和单元测试
