---
title: Go基础语法与数据类型
date: 2024-06-07 10:00:00
tags:
  - golang
---

# 基础语法与数据类型

Go 语法简洁，没有 class、继承、泛型（Go 1.18 前）等复杂特性。本章介绍变量、常量与基本类型。

## 变量声明

Go 有三种常见声明方式：

```go
// 完整声明
var name string = "Go"

// 类型推断
var age = 18

// 短变量声明（函数内）
city := "Beijing"
```

**短变量声明 `:=` 只能在函数内使用**，且左侧至少有一个新变量。

```go
a, b := 1, 2
b, c := 3, 4  // b 已存在则赋值，c 为新变量
```

多变量声明：

```go
var (
    host string = "localhost"
    port int    = 8080
)
```

## 零值

未显式赋值的变量会有**零值**，不会出现"未初始化"的随机值：

| 类型 | 零值 |
| ---- | ---- |
| 数值 | `0` |
| 布尔 | `false` |
| 字符串 | `""` |
| 指针、切片、map、channel、函数、interface | `nil` |

```go
var n int
var s string
var p *int
// n=0, s="", p=nil
```

## 常量

```go
const Pi = 3.14159
const (
    StatusOK    = 200
    StatusError = 500
)

// iota 枚举
const (
    Sunday = iota  // 0
    Monday         // 1
    Tuesday        // 2
)
```

## 基本数据类型

### 整数

```go
var a int = 42        // 平台相关，32 或 64 位
var b int64 = 1 << 32
var c uint8 = 255     // byte 的别名
```

常用：`int`、`int64`、`uint`、`byte`（uint8）、`rune`（int32，表示 Unicode 码点）。

### 浮点

```go
var f1 float64 = 3.14
var f2 float32 = 1.5
```

默认浮点字面量为 `float64`，计算精度要求高时用 `float64`。

### 布尔

```go
var ok bool = true
if ok {
    // ...
}
```

### 字符串

字符串是**只读**的字节序列，UTF-8 编码：

```go
s := "Hello, 世界"
len(s)              // 字节数，不是字符数
rune(s[0])           // 第一个字节对应的 rune

// 遍历字符（rune）
for i, ch := range s {
    fmt.Printf("%d: %c\n", i, ch)
}
```

字符串不可变，拼接用 `+` 或 `strings.Builder`（高效）：

```go
import "strings"

var b strings.Builder
b.WriteString("Hello")
b.WriteString(", Go")
result := b.String()
```

### 类型转换

Go **没有隐式类型转换**，必须显式转换：

```go
var i int = 42
var f float64 = float64(i)
var u uint = uint(f)

// 错误：cannot use i (type int) as float64
// var x float64 = i
```

## 指针

```go
x := 10
p := &x     // 取地址
fmt.Println(*p)  // 解引用，输出 10
*p = 20
fmt.Println(x)   // 20
```

Go 有指针但没有指针运算（不能 `p++`），比 C 更安全。

## 类型别名与自定义类型

```go
type UserID int64
type Meters float64

var id UserID = 1001
var dist Meters = 3.5

// UserID 与 int64 是不同类型，不能直接赋值
// var n int64 = id  // 编译错误
var n int64 = int64(id)
```

## 小结

- 用 `var` 或 `:=` 声明变量，注意零值规则
- 基本类型包括整型、浮点、布尔、字符串
- 字符串是 UTF-8 字节序列，用 `range` 遍历字符
- 类型转换必须显式，自定义类型需强转
