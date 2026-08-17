---
title: Python文件与IO
date: 2023-04-10 16:00:00
tags:
  - python
---

# 文件与 IO

## 读写文本文件

```python
# 读
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()          # 整个文件
    lines = f.readlines()       # 列表，每行含 \n

# 按行迭代（大文件推荐）
with open("large.log", encoding="utf-8") as f:
    for line in f:
        process(line.strip())

# 写
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("Hello\n")
    f.writelines(["line1\n", "line2\n"])

# 追加
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("new entry\n")
```

### 模式说明

| 模式 | 说明 |
| ---- | ---- |
| `r` | 只读（默认） |
| `w` | 写入，覆盖 |
| `a` | 追加 |
| `x` | 创建新文件，存在则失败 |
| `r+` | 读写 |
| `b` | 二进制，如 `rb`、`wb` |

## 读写二进制

```python
with open("image.png", "rb") as f:
    data = f.read()

with open("copy.png", "wb") as f:
    f.write(data)
```

## pathlib（推荐）

面向对象的路径操作，Python 3.4+：

```python
from pathlib import Path

p = Path("data/config.yaml")
p.exists()
p.is_file()
p.read_text(encoding="utf-8")
p.write_text("content", encoding="utf-8")

# 路径拼接
root = Path("/var/log")
log_file = root / "app" / "error.log"

# 遍历
for py_file in Path(".").glob("**/*.py"):
    print(py_file)

for item in Path("src").iterdir():
    print(item.name)
```

## JSON 文件

```python
import json
from pathlib import Path

data = {"name": "Alice", "scores": [90, 85]}

# 写
Path("user.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

# 读
raw = Path("user.json").read_text(encoding="utf-8")
obj = json.loads(raw)

# 流式
with open("data.json", encoding="utf-8") as f:
    obj = json.load(f)

with open("out.json", "w", encoding="utf-8") as f:
    json.dump(obj, f, ensure_ascii=False, indent=2)
```

## CSV

```python
import csv

with open("users.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["age"])

with open("out.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerow({"name": "Bob", "age": 30})
```

## 临时文件

```python
import tempfile

with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
    f.write("temp data")
    path = f.name
```

## 标准输入输出

```python
import sys

sys.stdin.readline()
print("stdout", file=sys.stdout)
print("stderr", file=sys.stderr)
```

## 小结

- 始终指定 `encoding="utf-8"` 读写文本
- 大文件用逐行迭代，避免一次性 `read()`
- `pathlib.Path` 替代 `os.path`，API 更清晰
- JSON/CSV 分别用 `json` 和 `csv` 标准库
