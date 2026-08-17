---
title: Go语言入门与环境搭建
date: 2024-06-02 09:00:00
tags:
  - golang
---

# Go 语言入门

Go（又称 Golang）是 Google 于 2009 年发布、2012 年开源的一门静态类型、编译型编程语言。设计目标是：**简单、高效、可靠**，特别适合云原生、微服务、网络编程和高并发场景。

## 为什么选择 Go

| 特点 | 说明 |
| ---- | ---- |
| 编译快 | 大型项目也能在秒级完成编译 |
| 并发原生支持 | goroutine + channel，语法层面支持 |
| 垃圾回收 | 自动内存管理，无需手动 free |
| 静态类型 | 编译期发现类型错误，IDE 友好 |
| 单二进制部署 | 交叉编译后一个可执行文件即可运行 |
| 标准库强大 | HTTP、JSON、加密、测试等开箱即用 |

常见应用场景：Kubernetes、Docker、Prometheus、etcd、微服务 API、CLI 工具等。

## 环境安装

### 1. 下载安装

访问 [https://go.dev/dl/](https://go.dev/dl/) 下载对应平台的安装包。Windows 直接运行 `.msi` 安装，macOS 使用 `.pkg`，Linux 解压到 `/usr/local/go` 并配置 PATH。

验证安装：

```bash
go version
# go version go1.22.0 linux/amd64
```

### 2. 环境变量

| 变量 | 作用 |
| ---- | ---- |
| `GOROOT` | Go 安装目录，一般自动设置 |
| `GOPATH` | 工作区目录（Go 1.11 前常用，现 Modules 模式下较少直接操作） |
| `GOPROXY` | 模块代理，国内建议 `https://goproxy.cn,direct` |
| `GO111MODULE` | 设为 `on` 启用 Go Modules |

```bash
# Linux / macOS 示例
export GOPROXY=https://goproxy.cn,direct
export GO111MODULE=on
```

### 3. 第一个程序

```bash
mkdir hello && cd hello
go mod init example/hello
```

创建 `main.go`：

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Go!")
}
```

运行：

```bash
go run main.go
# Hello, Go!

go build -o hello
./hello
```

## 项目结构初识

Go Modules 模式下，典型项目结构如下：

```
hello/
├── go.mod          # 模块定义与依赖
├── go.sum          # 依赖校验和
├── main.go         # 入口文件
├── internal/       # 私有包，外部不可导入
├── pkg/            # 可被外部引用的公共包
└── cmd/            # 多个可执行入口（可选）
```

`go.mod` 示例：

```
module example/hello

go 1.22
```

## 常用命令

| 命令 | 作用 |
| ---- | ---- |
| `go run` | 编译并运行 |
| `go build` | 编译生成可执行文件 |
| `go test` | 运行测试 |
| `go fmt` | 格式化代码 |
| `go vet` | 静态检查 |
| `go mod tidy` | 整理依赖 |
| `go get pkg@version` | 添加/升级依赖 |

## 开发工具推荐

- **IDE**：GoLand、VS Code + Go 插件
- **调试**：Delve（`dlv debug`）
- **文档**：`go doc fmt.Println` 或 [pkg.go.dev](https://pkg.go.dev)

## 小结

Go 以简洁语法和强大并发模型著称。安装 Go 工具链、初始化 `go mod`、编写 `package main` 是入门第一步。后续章节将从语法基础逐步深入到并发与工程实践。
