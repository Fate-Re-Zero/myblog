---
title: Python异常处理
date: 2023-04-11 15:00:00
tags:
  - python
---

# 异常处理

Python 用异常（Exception）处理错误，遵循 **EAFP**（Easier to Ask Forgiveness than Permission）风格：先尝试，出错再处理。

## 基本语法

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"除零错误: {e}")
except (TypeError, ValueError) as e:
    print(f"类型或值错误: {e}")
else:
    print("没有异常时执行")
finally:
    print("无论是否异常都执行")
```

## 抛出异常

```python
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

raise RuntimeError("something went wrong")
```

## 异常链

保留原始异常上下文：

```python
try:
    int("abc")
except ValueError as e:
    raise RuntimeError("解析失败") from e
```

## 常见内置异常

| 异常 | 触发场景 |
| ---- | -------- |
| `ValueError` | 值合法但语义不对 |
| `TypeError` | 类型不匹配 |
| `KeyError` | dict 键不存在 |
| `IndexError` | 序列索引越界 |
| `FileNotFoundError` | 文件不存在 |
| `AttributeError` | 对象无该属性 |
| `StopIteration` | 迭代器结束 |

## 自定义异常

```python
class AppError(Exception):
    """应用基础异常。"""

class NotFoundError(AppError):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} {id} not found")

def get_user(user_id: int) -> dict:
    user = db.find(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return user
```

## 断言 assert

开发阶段检查不变量，生产环境可用 `-O` 禁用：

```python
assert len(items) > 0, "items must not be empty"
```

**不要**用 assert 做业务逻辑校验或用户输入验证，应显式 raise。

## 上下文管理器

自动释放资源（详见装饰器章节）：

```python
with open("data.txt", encoding="utf-8") as f:
    content = f.read()
# 文件自动关闭
```

## 最佳实践

```python
# 好：捕获具体异常
try:
    value = int(user_input)
except ValueError:
    value = 0

# 差：裸 except 或 except Exception 吞掉所有错误
try:
    risky()
except:
    pass

# 好：使用 else 分离正常逻辑
try:
    data = load_config()
except FileNotFoundError:
    data = default_config()
else:
    validate(data)
```

## 小结

- 捕获具体异常类型，避免裸 `except`
- 自定义异常继承自 `Exception`，按业务分层
- `raise ... from ...` 保留异常链便于调试
- 资源管理优先用 `with` 语句
