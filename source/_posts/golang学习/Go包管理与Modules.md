---
title: Go包管理与Modules
date: 2024-06-13 19:00:00
tags:
  - golang
---

# 包管理与 Go Modules

## 包（Package）

每个 Go 文件属于一个 package，同一目录下 package 名相同：

```go
// mathutil/add.go
package mathutil

func Add(a, b int) int {
    return a + b
}
```

导入规则：

```go
import "fmt"                          // 标准库
import "example.com/project/mathutil" // 第三方或自有模块

import (
    "fmt"
    mu "example.com/project/mathutil"  // 别名
)
```

**大写开头**的标识符可导出（public），小写为包内私有。

## 可见性

```go
type User struct {    // 可导出
    ID   int64       // 可导出
    name string      // 包内私有
}

func NewUser() {}     // 可导出
func validate() {}    // 包内私有
```

## Go Modules

Go 1.11+ 官方依赖管理方案，以模块（module）为单位。

### 初始化

```bash
go mod init github.com/yourname/myproject
```

生成 `go.mod`：

```
module github.com/yourname/myproject

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
)
```

### 常用命令

```bash
go mod tidy          # 添加缺失依赖、删除未使用依赖
go get pkg@version   # 添加或升级依赖
go get pkg@latest
go mod download      # 下载依赖到本地缓存
go mod vendor        # 将依赖复制到 vendor 目录
go list -m all       # 列出所有依赖
```

### 版本语义

Go Modules 遵循语义化版本（SemVer）：`v1.2.3`

- 主版本 ≥ 2 时，import 路径需带版本后缀：`v2/module/v2`

### replace 与私有仓库

本地开发替换依赖：

```
replace example.com/lib => ../lib
```

私有 Git 仓库需配置 `GOPRIVATE`：

```bash
go env -w GOPRIVATE=git.company.com,github.com/yourname/*
```

## 项目布局参考

```
myproject/
├── go.mod
├── go.sum
├── cmd/
│   └── server/
│       └── main.go       # 可执行入口
├── internal/
│   ├── handler/          # HTTP 处理器
│   ├── service/          # 业务逻辑
│   └── repository/       # 数据访问
├── pkg/
│   └── util/             # 可被外部引用的工具包
├── api/                  # API 定义（OpenAPI 等）
└── configs/
```

- `internal/`：Go 编译器强制，外部模块无法 import
- `cmd/`：多个可执行文件的入口
- `pkg/`：可复用的公共库

## init 函数

包加载时自动执行，用于注册驱动、初始化配置：

```go
func init() {
    // 初始化逻辑，注意避免依赖顺序问题
}
```

一个包可有多个 `init`，同一文件内按定义顺序执行。

## 小结

- 大写导出、小写私有，用 package 组织代码
- Go Modules 管理依赖，`go mod tidy` 保持依赖整洁
- 推荐 `cmd/` + `internal/` 项目结构
- `internal` 包保证实现细节不对外暴露
