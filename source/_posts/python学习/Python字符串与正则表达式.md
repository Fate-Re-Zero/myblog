---
title: Python字符串与正则表达式
date: 2023-04-14 13:00:00
tags:
  - python
---

# 字符串与正则表达式

## 字符串不可变

字符串是 immutable，任何"修改"都会创建新对象：

```python
s = "hello"
s.upper()    # 返回 "HELLO"，s 不变
s = s.upper()  # 重新绑定
```

## 常用操作

```python
text = "  Hello, World!  "

text.strip()
text.lstrip()
text.rstrip()
text.lower()
text.upper()
text.title()
text.replace("World", "Python")
text.startswith("Hello")
text.endswith("!")
"World" in text

# 查找
text.find("World")      # 索引，找不到返回 -1
text.index("World")     # 找不到抛 ValueError
text.count("l")

# 分割与拼接
"a,b,c".split(",")
"\n".join(["line1", "line2"])
```

## 格式化

```python
name, score = "Alice", 95

# f-string（推荐）
f"{name} scored {score:.1f}"

# format
"{} scored {:.1f}".format(name, score)

# 对齐与填充
f"{name:>10}"    # 右对齐
f"{score:05d}"   # 00095
```

## 编码与解码

```python
s = "中文"
b = s.encode("utf-8")       # bytes
s2 = b.decode("utf-8")      # str

# 读写文件时注意 encoding="utf-8"
```

## bytes 与 bytearray

```python
data = b"hello"
data = bytes([72, 101, 108, 108, 111])
ba = bytearray(b"hello")    # 可变字节序列
```

## 正则表达式 re

```python
import re

pattern = r"\d{3}-\d{4}"
text = "Call 010-1234 or 020-5678"

# 查找
re.search(pattern, text)           # 第一个匹配
re.findall(pattern, text)          # 所有匹配 ['010-1234', '020-5678']

# 替换
re.sub(r"\d+", "X", "a1b22c")      # aXbXc

# 编译（重复使用时更高效）
pat = re.compile(r"(\w+)@(\w+\.\w+)")
m = pat.search("email: user@example.com")
if m:
    m.group(0)   # 完整匹配
    m.group(1)   # user
    m.group(2)   # example.com
```

### 常用元字符

| 模式 | 含义 |
| ---- | ---- |
| `.` | 任意字符（除换行） |
| `\d` | 数字 |
| `\w` | 字母数字下划线 |
| `\s` | 空白 |
| `*` | 0 次或多次 |
| `+` | 1 次或多次 |
| `?` | 0 次或 1 次 |
| `{n,m}` | n 到 m 次 |
| `^` | 行首 |
| `$` | 行尾 |
| `[]` | 字符集 |
| `()` | 分组 |

### 原始字符串

正则模式前加 `r`，避免 `\` 被转义：

```python
re.match(r"\d+", "123abc")
```

## 小结

- 字符串不可变，频繁拼接用 `"".join()` 或 `io.StringIO`
- f-string 是首选格式化方式
- 文本处理复杂时用 `re`，简单场景用字符串方法即可
