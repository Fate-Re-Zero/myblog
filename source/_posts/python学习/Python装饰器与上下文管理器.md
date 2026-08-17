---
title: Python装饰器与上下文管理器
date: 2023-04-13 19:00:00
tags:
  - python
---

# 装饰器与上下文管理器

## 装饰器原理

装饰器是接受函数、返回函数的高阶函数，语法糖 `@decorator`：

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(2, 3)
# calling add
# add returned 5
```

### functools.wraps

保留原函数元信息：

```python
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### 带参数的装饰器

```python
def repeat(times: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}")
```

### 类装饰器

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    print("Hi")
```

## 内置装饰器

```python
class MyClass:
    @staticmethod
    def util():
        ...

    @classmethod
    def create(cls):
        return cls()

    @property
    def name(self):
        ...
```

## 常见装饰器应用

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator
```

Flask/FastAPI 的路由注册 `@app.route`、`@app.get` 也是装饰器。

## 上下文管理器

`with` 语句保证资源正确释放，实现 `__enter__` 和 `__exit__`：

```python
class FileManager:
    def __init__(self, path: str, mode: str):
        self.path = path
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.path, self.mode, encoding="utf-8")
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False   # 不吞异常

with FileManager("data.txt", "r") as f:
    print(f.read())
```

### contextlib.contextmanager

用生成器简化：

```python
from contextlib import contextmanager

@contextmanager
def timer(label: str = ""):
    start = time.perf_counter()
    yield
    print(f"{label}: {time.perf_counter() - start:.4f}s")

with timer("task"):
    do_work()
```

### 常用内置上下文

```python
from contextlib import suppress, redirect_stdout
import io

with suppress(FileNotFoundError):
    os.remove("maybe_missing.txt")

buf = io.StringIO()
with redirect_stdout(buf):
    print("captured")
print(buf.getvalue())
```

## 小结

- 装饰器用于横切关注点：日志、计时、重试、权限
- 始终用 `@wraps` 保留函数签名
- 上下文管理器配合 `with` 管理资源生命周期
- `@contextmanager` 是用 yield 写上下文管理器的简便方式
