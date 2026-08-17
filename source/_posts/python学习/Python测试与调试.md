---
title: Python测试与调试
date: 2023-04-03 21:00:00
tags:
  - python
---

# 测试与调试

## unittest

标准库内置测试框架：

```python
# test_mathutil.py
import unittest
from mathutil import add

class TestAdd(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(add(2, 3), 5)

    def test_zero(self):
        self.assertEqual(add(0, 0), 0)

    def test_negative(self):
        self.assertEqual(add(-1, 1), 0)

    def test_type_error(self):
        with self.assertRaises(TypeError):
            add("a", 1)

if __name__ == "__main__":
    unittest.main()
```

```bash
python -m unittest discover -s tests -v
```

## pytest（推荐）

语法简洁，生态丰富：

```python
# test_mathutil.py
import pytest
from mathutil import add

def test_add_positive():
    assert add(2, 3) == 5

def test_add_zero():
    assert add(0, 0) == 0

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add_parametrize(a, b, expected):
    assert add(a, b) == expected
```

```bash
pip install pytest
pytest
pytest tests/test_mathutil.py -v
pytest --cov=myapp --cov-report=html
```

### fixture

```python
@pytest.fixture
def sample_user():
    return {"name": "Alice", "age": 25}

def test_user_name(sample_user):
    assert sample_user["name"] == "Alice"
```

### mock

```python
from unittest.mock import patch, MagicMock

def test_fetch_user(mocker):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 1, "name": "Bob"}
    mocker.patch("requests.get", return_value=mock_resp)

    user = fetch_user(1)
    assert user["name"] == "Bob"
```

## 调试技巧

### print 调试

```python
print(f"{var=}")   # Python 3.8+，print(var=42)
```

### pdb 断点

```python
import pdb; pdb.set_trace()   # 传统方式

def buggy():
    x = 1
    breakpoint()   # Python 3.7+，等价于 pdb.set_trace()
    return x / 0
```

常用命令：`n` 下一步、`s` 步入、`c` 继续、`p var` 打印变量、`q` 退出。

### logging 调试

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("x=%s", x)
```

## 性能分析

```python
import cProfile
cProfile.run("main()", sort="cumulative")

# 命令行
# python -m cProfile -s cumulative script.py
```

```python
import timeit
timeit.timeit("sum(range(1000))", number=10000)
```

## 代码质量工具

```bash
pip install ruff mypy

ruff check .          # lint
ruff format .         # 格式化
mypy src/             # 类型检查
```

## 测试最佳实践

1. 测试文件命名 `test_*.py` 或 `*_test.py`
2. 每个测试只验证一个行为
3. 用 fixture 管理测试数据，避免重复
4. 集成测试与单元测试分离
5. CI 中运行 `pytest --cov` 和 `ruff check`

## 小结

- 新项目优先 pytest，参数化与 fixture 提高效率
- `breakpoint()` 快速断点调试
- ruff + mypy 保证代码风格与类型安全
- 测试覆盖核心逻辑，不必追求 100%
