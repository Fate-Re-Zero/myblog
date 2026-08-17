---
title: Python面向对象编程
date: 2023-04-08 14:00:00
tags:
  - python
---

# 面向对象编程

Python 支持完整的 OOP：类、继承、多态、封装，同时保留函数式风格。

## 定义类

```python
class User:
    species = "Homo sapiens"   # 类变量

    def __init__(self, name: str, age: int):
        self.name = name       # 实例变量
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"

    def __repr__(self) -> str:
        return f"User(name={self.name!r}, age={self.age})"

user = User("Alice", 25)
user.greet()
print(user)   # User(name='Alice', age=25)
```

## 封装

Python 无 private 关键字，用命名约定：

```python
class Account:
    def __init__(self, balance: float):
        self._balance = balance      # 受保护（约定）
        self.__secret = "key"        # 名称改写，避免子类冲突

    def deposit(self, amount: float) -> None:
        if amount > 0:
            self._balance += amount
```

## 属性与 property

```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError("radius must be positive")
        self._radius = value

    @property
    def area(self) -> float:
        return 3.14159 * self._radius ** 2

c = Circle(5)
c.radius = 10
print(c.area)
```

## 继承

```python
class Animal:
    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"

def make_sound(animal: Animal) -> None:
    print(animal.speak())   # 多态
```

### super()

```python
class Employee(User):
    def __init__(self, name: str, age: int, dept: str):
        super().__init__(name, age)
        self.dept = dept
```

### 多重继承

Python 支持多继承，按 MRO（Method Resolution Order）查找方法：

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    pass

class D(B, C):
    pass

D().method()           # "B"
D.__mro__              # 查看解析顺序
```

实际项目中多重继承宜谨慎，Mixin 模式更常见。

## 特殊方法（魔术方法）

```python
class Vector:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __len__(self) -> int:
        return 2

    def __getitem__(self, index: int) -> float:
        return (self.x, self.y)[index]
```

常用：`__str__`、`__repr__`、`__eq__`、`__hash__`、`__len__`、`__getitem__`、`__enter__`/`__exit__`。

## dataclass（Python 3.7+）

简化数据类定义：

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float
    label: str = "origin"

@dataclass(frozen=True)   # 不可变
class Config:
    host: str
    port: int = 8080

@dataclass
class Node:
    value: int
    children: list["Node"] = field(default_factory=list)
```

## 抽象基类

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def get(self, id: int) -> dict:
        ...

    @abstractmethod
    def save(self, entity: dict) -> None:
        ...
```

## 小结

- `__init__` 初始化，`self` 代表实例
- `@property` 实现 getter/setter
- 继承 + 多态，配合 ABC 定义接口
- 数据类优先用 `@dataclass`，减少样板代码
