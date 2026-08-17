---
title: Python标准库实战
date: 2023-04-02 20:00:00
tags:
  - python
---

# 标准库实战

Python "内置电池"哲学：标准库覆盖大多数日常需求。本章介绍高频模块。

## datetime — 日期时间

```python
from datetime import datetime, date, timedelta, timezone

now = datetime.now()
today = date.today()
dt = datetime(2026, 6, 30, 14, 30, 0)

# 格式化
now.strftime("%Y-%m-%d %H:%M:%S")
datetime.strptime("2026-06-30", "%Y-%m-%d")

# 运算
tomorrow = today + timedelta(days=1)
delta = datetime(2026, 7, 1) - now

# 时区
utc = datetime.now(timezone.utc)
```

## collections — 增强容器

```python
from collections import deque, Counter, defaultdict, namedtuple

# 双端队列
dq = deque([1, 2, 3])
dq.appendleft(0)
dq.pop()

# 计数
Counter("hello")              # Counter({'l': 2, ...})
Counter([1, 1, 2, 3, 3, 3])

# 命名元组
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
p.x
```

## os 与 shutil

```python
import os
import shutil

os.getcwd()
os.listdir(".")
os.makedirs("logs/app", exist_ok=True)
os.environ.get("HOME")

shutil.copy("src.txt", "dst.txt")
shutil.rmtree("temp_dir")
```

## subprocess — 执行命令

```python
import subprocess

result = subprocess.run(
    ["python", "--version"],
    capture_output=True,
    text=True,
    check=True,
)
print(result.stdout)
```

## urllib / http

简单 HTTP 请求可用标准库，生产环境推荐 `requests`：

```python
from urllib.request import urlopen
import json

with urlopen("https://api.github.com") as resp:
    data = json.loads(resp.read().decode())
```

## logging — 日志

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
logger.info("server started")
logger.error("connection failed", exc_info=True)
```

## random 与 secrets

```python
import random
import secrets

random.randint(1, 100)
random.choice(["a", "b", "c"])
random.shuffle(items)

# 密码、token 用 secrets，不用 random
token = secrets.token_hex(32)
```

## typing — 类型工具

```python
from typing import Optional, Union, Callable, TypeVar, Generic

T = TypeVar("T")

def first(items: list[T]) -> Optional[T]:
    return items[0] if items else None

Handler = Callable[[str], None]
```

Python 3.10+ 可用内置语法：`list[int]`、`X | Y` 替代 `Optional`、`Union`。

## functools

```python
from functools import lru_cache, partial

@lru_cache(maxsize=128)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

# 偏函数
int_from_hex = partial(int, base=16)
int_from_hex("ff")   # 255
```

## 小结

- `datetime` 处理时间，`collections` 扩展容器
- `logging` 替代 print 做生产日志
- 安全随机用 `secrets`，不要用 `random`
- 复杂 HTTP/异步任务可引入 requests、aiohttp 等第三方库
