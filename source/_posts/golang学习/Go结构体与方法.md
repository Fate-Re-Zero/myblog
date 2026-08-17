---
title: Go结构体与方法
date: 2024-06-05 13:00:00
tags:
  - golang
---

# 结构体与方法

Go 没有 class，用**结构体（struct）**组织数据，用**方法（method）**绑定行为。

## 结构体定义

```go
type User struct {
    ID   int64
    Name string
    Age  int
}

u := User{ID: 1, Name: "Alice", Age: 25}
u2 := User{1, "Bob", 30}  // 按字段顺序，不推荐

// 部分初始化，其余为零值
u3 := User{Name: "Carol"}
```

## 字段标签

常用于 JSON、数据库 ORM 等序列化场景：

```go
type Product struct {
    ID    int64  `json:"id"`
    Name  string `json:"name"`
    Price float64 `json:"price,omitempty"`
}
```

## 指针与结构体

```go
u := User{Name: "Alice"}
p := &User{Name: "Bob"}  // 结构体指针

// Go 自动解引用，p.Name 等价于 (*p).Name
fmt.Println(p.Name)

// 取地址
p2 := &u
p2.Age = 26  // 修改 u.Age
```

## 嵌入（组合）

Go 用**嵌入**实现组合，而非继承：

```go
type Animal struct {
    Name string
}

func (a Animal) Speak() {
    fmt.Println(a.Name, "makes a sound")
}

type Dog struct {
    Animal       // 嵌入，Dog 拥有 Animal 的字段和方法
    Breed string
}

d := Dog{
    Animal: Animal{Name: "Buddy"},
    Breed:  "Labrador",
}
d.Speak()       // Buddy makes a sound
fmt.Println(d.Name)  // 可直接访问嵌入字段
```

## 方法

方法是带**接收者（receiver）**的函数：

```go
// 值接收者
func (u User) Greet() string {
    return "Hello, " + u.Name
}

// 指针接收者
func (u *User) Birthday() {
    u.Age++
}
```

### 值接收者 vs 指针接收者

| 场景 | 推荐 |
| ---- | ---- |
| 需要修改接收者 | 指针接收者 |
| 结构体较大，避免拷贝 | 指针接收者 |
| 小结构体、只读操作 | 值接收者可 |

```go
u := User{Name: "Alice", Age: 25}
u.Birthday()   // Go 自动取地址 (&u).Birthday()
```

**一致性原则**：同一类型的方法，接收者类型应统一（都用指针或都用值），避免混用。

## 构造函数惯例

Go 没有构造函数，常用 `NewXxx` 工厂函数：

```go
func NewUser(name string, age int) (*User, error) {
    if name == "" {
        return nil, fmt.Errorf("name is required")
    }
    return &User{Name: name, Age: age}, nil
}
```

## 结构体比较

结构体可比较（所有字段可比较时）：

```go
u1 := User{ID: 1, Name: "A"}
u2 := User{ID: 1, Name: "A"}
u1 == u2  // true

// 含 slice、map、func 的 struct 不可比较
```

## 小结

- 用 struct 组织数据，用嵌入实现组合
- 方法通过接收者绑定到类型，修改状态用指针接收者
- 工厂函数 `NewXxx` 是常见初始化模式
