---
title: Go接口
date: 2024-06-06 14:00:00
tags:
  - golang
---

# 接口

Go 的接口是**隐式实现**的：只要类型实现了接口的所有方法，就自动满足该接口，无需 `implements` 关键字。

## 接口定义

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}
```

## 隐式实现

```go
type File struct {
    path string
}

func (f *File) Read(p []byte) (int, error) {
    // 实现读取逻辑
    return 0, nil
}

// *File 自动实现 Reader 接口
var r Reader = &File{path: "data.txt"}
```

## 空接口

`interface{}`（Go 1.18+ 可写 `any`）不包含任何方法，**所有类型**都实现空接口：

```go
func printAny(v any) {
    fmt.Println(v)
}

printAny(42)
printAny("hello")
printAny([]int{1, 2})
```

## 类型断言

从 interface 取出具体类型：

```go
var i any = "hello"

s, ok := i.(string)  // s="hello", ok=true
n, ok := i.(int)    // n=0, ok=false

// 失败时 panic 的写法（确定类型时使用）
s = i.(string)
```

类型 switch：

```go
switch v := i.(type) {
case string:
    fmt.Println("string:", v)
case int:
    fmt.Println("int:", v)
default:
    fmt.Println("unknown")
}
```

## 接口组合

```go
type ReadWriter interface {
    Reader
    Writer
}
```

## 常用标准接口

| 接口 | 包 | 典型用途 |
| ---- | --- | -------- |
| `io.Reader` / `io.Writer` | io | 读写抽象 |
| `fmt.Stringer` | fmt | 自定义 `String()` 输出 |
| `error` | builtin | 错误类型 |
| `sort.Interface` | sort | 自定义排序 |

```go
type Point struct{ X, Y int }

func (p Point) String() string {
    return fmt.Sprintf("(%d,%d)", p.X, p.Y)
}
// Point 实现 fmt.Stringer
```

## 面向接口编程

依赖接口而非具体类型，便于测试和扩展：

```go
type UserStore interface {
    Get(id int64) (*User, error)
    Save(u *User) error
}

type Service struct {
    store UserStore
}

// 生产环境用数据库实现，测试用 mock 实现
func NewService(store UserStore) *Service {
    return &Service{store: store}
}
```

## nil 接口陷阱

```go
var err error
var p *MyError = nil
err = p

if err != nil {
    // 会进入！接口 nil 需要类型和值都为 nil
    fmt.Println("not nil")
}
```

接口变量为 nil 当且仅当**动态类型和动态值都为 nil**。

## 小结

- 接口隐式实现，是 Go 多态的核心
- 小接口 + 组合，优于大而全的接口
- 面向接口编程提升可测试性与扩展性
- 注意 nil 接口的判断陷阱
