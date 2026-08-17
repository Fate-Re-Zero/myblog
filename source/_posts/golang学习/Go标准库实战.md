---
title: Go标准库实战
date: 2024-06-12 20:00:00
tags:
  - golang
---

# 标准库实战

Go 标准库功能丰富，日常开发大部分需求无需第三方库。本章介绍最常用的几个包。

## net/http — HTTP 服务与客户端

### 简单 HTTP 服务

```go
package main

import (
    "fmt"
    "net/http"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
}

func main() {
    http.HandleFunc("/hello/", helloHandler)
    http.ListenAndServe(":8080", nil)
}
```

### JSON API

```go
type Response struct {
    Code    int    `json:"code"`
    Message string `json:"message"`
}

func userHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(Response{Code: 0, Message: "ok"})
}
```

### HTTP 客户端

```go
resp, err := http.Get("https://api.example.com/users")
if err != nil {
    return err
}
defer resp.Body.Close()

body, err := io.ReadAll(resp.Body)
```

生产环境建议使用带 Context 和超时的 `http.Client`：

```go
client := &http.Client{Timeout: 10 * time.Second}
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := client.Do(req)
```

## encoding/json

```go
type User struct {
    ID   int64  `json:"id"`
    Name string `json:"name"`
}

// 序列化
data, err := json.Marshal(user)

// 反序列化
var u User
err = json.Unmarshal(data, &u)

// 流式编解码（大 JSON）
decoder := json.NewDecoder(r.Body)
encoder := json.NewEncoder(w)
```

## database/sql

```go
import (
    "database/sql"
    _ "github.com/go-sql-driver/mysql"  // 注册驱动
)

db, err := sql.Open("mysql", "user:pass@tcp(localhost:3306)/dbname")
if err != nil {
    log.Fatal(err)
}
defer db.Close()

db.SetMaxOpenConns(25)
db.SetMaxIdleConns(5)

row := db.QueryRowContext(ctx, "SELECT name FROM users WHERE id = ?", id)
err = row.Scan(&name)
```

## io 与 os

```go
// 读文件
data, err := os.ReadFile("config.yaml")

// 写文件
err = os.WriteFile("output.txt", data, 0644)

// 拷贝
io.Copy(dst, src)

// 限流读取
limited := io.LimitReader(r, 1024)
```

## time

```go
now := time.Now()
t := time.Date(2026, 6, 29, 12, 0, 0, 0, time.Local)

// 解析与格式化
layout := "2006-01-02 15:04:05"  // Go 的参考时间
s := now.Format(layout)
t, err := time.Parse(layout, "2026-06-29 12:00:00")

// 定时器
timer := time.NewTimer(5 * time.Second)
<-timer.C

ticker := time.NewTicker(time.Second)
defer ticker.Stop()
for range ticker.C {
    // 每秒执行
}
```

## strings 与 strconv

```go
strings.Contains(s, "sub")
strings.Split(s, ",")
strings.Join([]string{"a", "b"}, ",")
strings.Builder  // 高效拼接

i, err := strconv.Atoi("42")
s := strconv.Itoa(42)
f, err := strconv.ParseFloat("3.14", 64)
```

## 小结

- `net/http` 足以构建 REST API 和微服务
- `encoding/json` 处理 JSON 序列化
- `database/sql` + 驱动连接数据库，注意连接池配置
- 优先使用标准库，第三方库选型需评估维护活跃度
