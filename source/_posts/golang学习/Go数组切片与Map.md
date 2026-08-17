---
title: Go数组切片与Map
date: 2024-06-03 12:00:00
tags:
  - golang
---

# 数组、切片与 Map

Go 中数组、切片、Map 是最常用的复合类型。日常开发中**几乎只用切片，很少直接用数组**。

## 数组

长度是类型的一部分，`[3]int` 与 `[5]int` 是不同类型：

```go
var a [3]int           // [0 0 0]
b := [3]int{1, 2, 3}
c := [...]int{1, 2, 3} // 编译器推断长度

// 数组是值类型，赋值会复制整个数组
d := b
d[0] = 100
// b[0] 仍为 1
```

## 切片（Slice）

切片是对数组的**动态视图**，包含指针、长度 len、容量 cap 三个属性。

### 创建

```go
// 字面量
s1 := []int{1, 2, 3}

// make 创建
s2 := make([]int, 5)       // len=5, cap=5, 全 0
s3 := make([]int, 3, 10)   // len=3, cap=10

// 从数组切片
arr := [5]int{1, 2, 3, 4, 5}
s4 := arr[1:4]  // [2 3 4]，左闭右开
```

### 常用操作

```go
s := []int{1, 2, 3}

len(s)   // 3
cap(s)   // 3

s = append(s, 4)           // [1 2 3 4]
s = append(s, 5, 6, 7)     // 追加多个

// 切片截取
sub := s[1:3]   // [2 3]
sub = s[:3]     // [1 2 3]
sub = s[2:]     // [3 4 5 6 7]
```

### append 与扩容

`append` 可能触发底层数组扩容，返回新切片（可能指向新数组）：

```go
s1 := []int{1, 2, 3}
s2 := append(s1, 4)

// 若 cap 足够，s1 与 s2 共享底层数组
// 若扩容，s2 指向新数组，修改 s2 不影响 s1
```

**注意**：循环中向切片追加元素时，不要对 range 的变量直接 append 到同一切片，容易踩坑。

### 拷贝

```go
src := []int{1, 2, 3}
dst := make([]int, len(src))
copy(dst, src)
```

### nil 切片

```go
var s []int   // nil，len=0, cap=0
s == nil      // true

// nil 切片可以 append
s = append(s, 1)  // OK
```

## Map

Map 是键值对集合，**引用类型**，必须 make 或字面量初始化后才能写入：

```go
// 字面量
m1 := map[string]int{
    "apple":  5,
    "banana": 3,
}

// make
m2 := make(map[string]int)

// 读写
m2["key"] = 42
v, ok := m2["key"]   // v=42, ok=true
v, ok = m2["none"]   // v=0, ok=false（key 不存在）

// 删除
delete(m2, "key")

// 遍历（顺序随机）
for k, v := range m2 {
    fmt.Println(k, v)
}
```

### 零值与并发

```go
var m map[string]int  // nil map
m["a"] = 1            // panic: assignment to entry in nil map
```

**Map 不是并发安全的**，并发读写需用 `sync.Map` 或加锁。

## 切片 vs 数组 vs Map 选型

| 场景 | 推荐 |
| ---- | ---- |
| 固定长度、值语义 | 数组（极少） |
| 动态列表、队列 | 切片 |
| 键值查找、计数 | Map |
| 并发 Map | sync.Map 或 map + Mutex |

## 小结

- 数组是值类型、定长；切片是引用类型、动态，日常首选
- `append` 可能扩容，注意共享底层数组的副作用
- Map 需初始化后使用，用 `v, ok := m[key]` 判断 key 是否存在
