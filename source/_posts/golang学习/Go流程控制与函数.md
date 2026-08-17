---
title: Go流程控制与函数
date: 2024-06-04 11:00:00
tags:
  - golang
---

# 流程控制与函数

## 条件语句

Go 的 `if` **不需要括号**，但**必须有大括号**：

```go
if x > 0 {
    fmt.Println("positive")
} else if x < 0 {
    fmt.Println("negative")
} else {
    fmt.Println("zero")
}
```

`if` 可以带初始化语句，变量作用域仅在 if-else 块内：

```go
if err := doSomething(); err != nil {
    return err
}
// err 在此处不可见
```

## switch

比 C 更强大，**自动 break**，无需写 `break`：

```go
switch day {
case "Mon", "Tue", "Wed", "Thu", "Fri":
    fmt.Println("workday")
case "Sat", "Sun":
    fmt.Println("weekend")
default:
    fmt.Println("unknown")
}
```

无表达式的 switch 等价于 if-else 链：

```go
switch {
case score >= 90:
    grade = "A"
case score >= 60:
    grade = "B"
default:
    grade = "C"
}
```

类型 switch（interface 相关，后续接口章节详述）：

```go
switch v := x.(type) {
case int:
    fmt.Println("int", v)
case string:
    fmt.Println("string", v)
}
```

## for 循环

Go **只有 for**，没有 while，但 for 可表达 while：

```go
// 经典三段式
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// 等价 while
sum := 1
for sum < 1000 {
    sum += sum
}

// 无限循环
for {
    // break 退出
}

// range 遍历
nums := []int{1, 2, 3}
for index, value := range nums {
    fmt.Println(index, value)
}
for _, v := range nums {  // 忽略 index
    fmt.Println(v)
}
```

## 函数

### 基本定义

```go
func add(a int, b int) int {
    return a + b
}

// 相同类型参数可简写
func add(a, b int) int {
    return a + b
}
```

### 多返回值

Go 函数可返回多个值，错误处理的核心模式：

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 2)
if err != nil {
    log.Fatal(err)
}
```

### 命名返回值

```go
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return  // 裸 return，返回 x, y
}
```

### 可变参数

```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

sum(1, 2, 3)
sum([]int{1, 2, 3}...)  // 切片展开
```

### 函数是一等公民

函数可以作为参数、返回值、赋值给变量：

```go
func apply(f func(int, int) int, a, b int) int {
    return f(a, b)
}

addFn := func(a, b int) int { return a + b }
apply(addFn, 3, 4)  // 7
```

### defer

函数退出前执行，常用于资源释放，**后进先出**：

```go
func readFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close()  // 函数 return 前执行

    // 读取文件...
    return nil
}
```

多个 defer 按 LIFO 顺序执行：

```go
defer fmt.Println("1")
defer fmt.Println("2")
defer fmt.Println("3")
// 输出: 3 2 1
```

## 小结

- `if`、`switch`、`for` 是主要控制结构，语法比 C/Java 更简洁
- 多返回值 + `error` 是 Go 错误处理的基础
- `defer` 保证资源释放，注意执行顺序
