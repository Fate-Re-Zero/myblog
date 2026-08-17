---
title: Python列表字典与集合
date: 2023-04-06 12:00:00
tags:
  - python
---

# 列表、字典与集合

Python 内置多种容器类型，是日常开发最常用的数据结构。

## 列表 list

有序、可变、允许重复：

```python
nums = [1, 2, 3]
mixed = [1, "hello", True, [1, 2]]

# 索引与切片
nums[0]       # 1
nums[-1]      # 最后一个
nums[1:3]     # [2, 3]
nums[:2]       # [1, 2]
nums[::2]      # 步长 2

# 修改
nums.append(4)
nums.extend([5, 6])
nums.insert(0, 0)
nums.pop()           # 删除并返回最后一个
nums.remove(2)       # 删除第一个值为 2 的元素
del nums[0]

# 常用操作
len(nums)
3 in nums
nums.index(3)
nums.count(3)
nums.sort()
sorted(nums)         # 返回新列表，不修改原列表
nums.reverse()
```

### 浅拷贝与深拷贝

```python
import copy

a = [[1, 2], [3, 4]]
b = a.copy()           # 浅拷贝
c = copy.deepcopy(a)   # 深拷贝

a[0][0] = 99
# b[0][0] 也变为 99，c 不受影响
```

## 元组 tuple

有序、**不可变**：

```python
point = (3, 4)
single = (42,)       # 单元素元组需逗号

x, y = point         # 解包
name, age, *_ = ("Alice", 25, "Beijing", "CN")
```

元组适合固定结构的数据，如坐标、数据库行、函数多返回值。

## 字典 dict

键值对，键必须可哈希（不可变类型）：

```python
user = {"name": "Alice", "age": 25}
user["email"] = "a@example.com"

# 访问
user.get("phone")           # None
user.get("phone", "N/A")    # 默认值

# 遍历
for key in user:
    print(key, user[key])

for key, value in user.items():
    print(key, value)

# 合并（Python 3.9+）
defaults = {"role": "user"}
profile = defaults | user

# 字典推导
{x: x ** 2 for x in range(5)}
```

### OrderedDict 与 defaultdict

```python
from collections import defaultdict, Counter

# 自动创建默认值
dd = defaultdict(list)
dd["a"].append(1)

# 计数
counter = Counter("hello")
# Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})
```

## 集合 set

无序、不重复：

```python
s = {1, 2, 3}
s = set([1, 2, 2, 3])   # {1, 2, 3}

s.add(4)
s.remove(2)
s.discard(99)           # 不存在不报错

# 集合运算
a = {1, 2, 3}
b = {2, 3, 4}
a | b    # 并集 {1, 2, 3, 4}
a & b    # 交集 {2, 3}
a - b    # 差集 {1}
a ^ b    # 对称差 {1, 4}
```

去重：

```python
unique = list(set([1, 2, 2, 3, 3]))
```

## 类型对比

| 类型 | 有序 | 可变 | 重复 | 典型用途 |
| ---- | ---- | ---- | ---- | -------- |
| list | 是 | 是 | 是 | 序列数据 |
| tuple | 是 | 否 | 是 | 固定记录 |
| dict | 3.7+ 保序 | 是 | 键唯一 | 映射、配置 |
| set | 否 | 是 | 否 | 去重、集合运算 |

## 小结

- list 最常用，注意切片与浅拷贝
- dict 是 Python 核心数据结构，`.get()` 比直接 `[]` 更安全
- set 适合去重和集合运算
- 复杂场景优先考虑 `collections` 模块
