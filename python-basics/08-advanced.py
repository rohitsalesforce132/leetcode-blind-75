'''
CHAPTER 8: MODULES, ITERATORS, GENERATORS & DECORATORS — THE COMPLETE DEEP DIVE
==================================================================================

"This final chapter covers the 'advanced' features that separate
beginners from professionals. Once you understand these, you can read
and write production-grade Python. These concepts are heavily tested
in interviews — especially generators and decorators."

---

PART 1: MODULES — ORGANIZING CODE INTO REUSABLE FILES
=======================================================

Real-world analogy: A TOOLBOX.

    You don't carry all your tools loose in your pockets.
    You organize them into BOXES: one for screwdrivers, one for wrenches.

A module is a Python file (.py) that contains functions, classes, and
variables you can IMPORT and reuse. This keeps code organized.

WHY MODULES?
    1. REUSABILITY: Write once, import everywhere.
    2. ORGANIZATION: Split large codebases into manageable files.
    3. NAMESPACING: Avoid name collisions (math.sqrt vs numpy.sqrt).
    4. DISTRIBUTION: Share code with others (pip install).
'''

# --- IMPORTING BUILT-IN MODULES ---
import math

print(math.pi)                    # 3.141592653589793
print(math.sqrt(144))             # 12.0
print(math.ceil(3.2))             # 4   (round up)
print(math.floor(3.8))            # 3   (round down)
print(math.factorial(5))          # 120
print(math.gcd(12, 8))            # 4   (greatest common divisor)
print(math.log(100, 10))          # 2.0 (log base 10 of 100)

# --- IMPORT SPECIFIC ITEMS ---
from math import pi, sqrt, ceil   # Import only what you need
print(sqrt(64))                   # 8.0

from math import *                # Import everything (AVOID — pollutes namespace)

# --- IMPORT WITH ALIAS ---
import datetime as dt             # Alias for convenience
import collections as col
now = dt.datetime.now()
print(f"Now: {now}")

# --- THE COLLECTIONS MODULE ---
from collections import Counter, defaultdict, deque, namedtuple, OrderedDict

# Counter: frequency counting
words = "the cat sat on the mat the cat".split()
c = Counter(words)
print(f"\nMost common: {c.most_common(2)}")

# defaultdict: auto-initialize missing keys
dd = defaultdict(list)
dd["fruits"].append("apple")
dd["fruits"].append("banana")
print(f"Defaultdict: {dict(dd)}")

# deque: double-ended queue (O(1) at both ends)
dq = deque([1, 2, 3])
dq.appendleft(0)
dq.append(4)
print(f"Deque: {list(dq)}")

# namedtuple: like a class but simpler
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(f"Point: {p.x}, {p.y}")

# OrderedDict: dict that remembers insertion order
# (Regular dicts also preserve order since Python 3.7)
od = OrderedDict()
od["last"] = 3
od["first"] = 1
od["middle"] = 2

# --- THE DATETIME MODULE ---
from datetime import datetime, timedelta, date

now = datetime.now()
print(f"\nNow: {now}")

formatted = now.strftime("%Y-%m-%d %H:%M:%S")
print(f"Formatted: {formatted}")

tomorrow = now + timedelta(days=1)
print(f"Tomorrow: {tomorrow.strftime('%Y-%m-%d')}")

# Parse a date string
parsed = datetime.strptime("2024-12-25", "%Y-%m-%d")
print(f"Christmas: {parsed}")

# --- THE OS MODULE ---
import os

print(f"\nCurrent dir: {os.getcwd()}")
print(f"Home: {os.path.expanduser('~')}")

# --- THE SYS MODULE ---
import sys

print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Args: {sys.argv}")

# --- THE RANDOM MODULE ---
import random

print(f"\nRandom int: {random.randint(1, 100)}")
print(f"Choice: {random.choice(['apple', 'banana', 'cherry'])}")
print(f"Sample: {random.sample(range(1, 50), 6)}")


'''
CREATING YOUR OWN MODULE
-------------------------
Any .py file is a module. If you have utils.py:

    # utils.py
    def greet(name):
        return f"Hello, {name}"

    PI = 3.14159

Then in another file in the same directory:
    # main.py
    import utils
    print(utils.greet("Manav"))

    from utils import greet, PI
    print(greet("Manav"))

PACKAGE: A directory with __init__.py
    my_package/
        __init__.py
        module_a.py
        module_b.py

    from my_package import module_a
'''


'''
PART 2: ITERATORS AND GENERATORS — MEMORY EFFICIENCY
======================================================

THE PROBLEM:
    Reading a 10 GB file. If you load it all into memory:
    → program crashes. Not enough RAM.

THE SOLUTION: ITERATORS / GENERATORS
    Instead of loading everything, produce ONE ITEM AT A TIME.
    Process it, get the next, repeat. Memory: O(1), not O(n).

Analogy:
    List = SWIMMING POOL. All water is there. Takes space.
    Generator = FAUCET. Water comes one cup at a time. Minimal space.
'''

# --- WHAT IS AN ITERATOR? ---
# An iterator is any object that can produce the "next" item.
# It remembers WHERE it is. You call next() to get the next item.

my_list = [10, 20, 30]
iterator = iter(my_list)        # Create an iterator

print(next(iterator))           # 10
print(next(iterator))           # 20
print(next(iterator))           # 30
# print(next(iterator))         # StopIteration! Iterator is exhausted.

# HOW FOR LOOPS ACTUALLY WORK:
# for item in my_list:
#     ...
#
# Python translates to:
# iterator = iter(my_list)
# while True:
#     try:
#         item = next(iterator)
#         ... your loop body ...
#     except StopIteration:
#         break

# --- GENERATOR FUNCTION (uses yield) ---
def count_up_to(n):
    """Generate numbers from 1 to n, one at a time."""
    current = 1
    while current <= n:
        yield current           # PAUSE here, return current, resume later
        current += 1            # Resumes from here on next() call

for num in count_up_to(5):
    print(f"  Generated: {num}", end=" ")
print()
# 1 2 3 4 5

# KEY DIFFERENCE: yield vs return
#   return → function is DONE. One output.
#   yield  → function PAUSES. Can produce MANY outputs.

# --- GENERATOR EXPRESSION (like list comp but lazy) ---
squares_list = [x ** 2 for x in range(5)]       # Creates full list: [0,1,4,9,16]
squares_gen = (x ** 2 for x in range(5))        # Creates generator (lazy)

print(list(squares_gen))                        # [0, 1, 4, 9, 16]

# The generator doesn't compute values until you ask!
gen = (x ** 2 for x in range(1000000000))       # Instant! No computation yet.
print(next(gen))                                # 0 (computes one value)

# --- INFINITE GENERATOR ---
def fibonacci():
    """Generate Fibonacci numbers forever."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Use itertools.islice to take only what you need:
from itertools import islice

print("\n--- Fibonacci ---")
for fib_num in islice(fibonacci(), 10):
    print(f"  {fib_num}", end="")
print()
# 0 1 1 2 3 5 8 13 21 34


'''
GENERATORS vs LISTS — WHEN TO USE WHICH:
    Use list when:
    - You need to access elements multiple times
    - You need len() or indexing
    - The data is small enough to fit in memory

    Use generator when:
    - Processing large files or streams
    - You only iterate once
    - Memory efficiency matters
    - Infinite sequences
'''


'''
PART 3: DECORATORS — MODIFYING FUNCTIONS
=========================================

A decorator WRAPS a function to extend its behavior without changing
the original code.

Analogy: GIFT WRAPPING. The gift (function) is unchanged.
The wrapping (decorator) adds features.

STEP 1: Functions are first-class objects (can be passed as arguments)
STEP 2: A decorator is a function that takes a function and returns a new one
STEP 3: Apply with @syntax
'''

import time
import functools

# --- A SIMPLE DECORATOR ---
def timer(func):
    """Measure execution time of a function."""
    @functools.wraps(func)  # Preserves original function's metadata
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)       # Call original function
        elapsed = time.time() - start
        print(f"  [timer] {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.1)
    return "Done!"

print("\n--- Decorator ---")
print(slow_function())

# @timer is shorthand for:
# def slow_function(): ...
# slow_function = timer(slow_function)

# --- DECORATOR WITH ARGUMENTS ---
def repeat(n):
    """Run the decorated function n times."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(n):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def say_hi(name):
    return f"Hi, {name}!"

print(say_hi("Manav"))    # ['Hi, Manav!', 'Hi, Manav!', 'Hi, Manav!']

# --- PRACTICAL DECORATOR: MEMOIZATION ---
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_fast(n):
    """Cached Fibonacci — O(n) instead of O(2^n)!"""
    if n <= 1:
        return n
    return fibonacci_fast(n - 1) + fibonacci_fast(n - 2)

print(f"\nMemoized fib(100) = {fibonacci_fast(100)}")


'''
PART 4: CONTEXT MANAGERS (THE 'with' STATEMENT)
=================================================

'with open(...) as f:' is a context manager. You can create your own.
'''

from contextlib import contextmanager

@contextmanager
def timer_context(label="Block"):
    """Measure time in a code block."""
    start = time.time()
    try:
        yield                    # Code inside 'with' runs here
    finally:
        elapsed = time.time() - start
        print(f"  {label} took {elapsed:.4f}s")

print("\n--- Context Manager ---")
with timer_context("My operation"):
    total = sum(x ** 2 for x in range(100000))
    print(f"  Sum of squares: {total}")


'''
PART 5: TYPE HINTS (PYTHON 3.5+)
==================================

Type hints make code self-documenting and catch bugs with tools like mypy.
They DON'T enforce types at runtime — they're just HINTS.
'''

from typing import List, Dict, Optional, Tuple, Union, Any

# --- BASIC TYPE HINTS ---
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> str:
    return f"Hello, {name}"

# --- COLLECTION TYPE HINTS ---
def process_items(items: List[int]) -> List[str]:
    return [str(x) for x in items]

def get_config(key: str) -> Optional[str]:
    """Return config value or None if not found."""
    config = {"port": "8080"}
    return config.get(key)

# Union type (can be one of several types):
def parse_value(value: Union[int, str]) -> int:
    if isinstance(value, str):
        return int(value)
    return value

# Python 3.9+ allows lowercase (no import needed):
def double_all(nums: list[int]) -> list[int]:
    return [n * 2 for n in nums]

# --- TYPE HINTS IN CLASSES ---
class User:
    def __init__(self, name: str, age: int):
        self.name: str = name
        self.age: int = age

    def is_adult(self) -> bool:
        return self.age >= 18


'''
PART 6: FUNCTOOLS — UTILITY FUNCTIONS
=======================================
'''

from functools import reduce

# --- REDUCE: Combine all elements into one ---
numbers = [1, 2, 3, 4, 5]

# Product of all elements:
product = reduce(lambda a, b: a * b, numbers)
print(f"\nProduct of {numbers}: {product}")    # 120

# Maximum element:
maximum = reduce(lambda a, b: a if a > b else b, numbers)
print(f"Maximum: {maximum}")                    # 5

# reduce step by step:
# Step 1: 1 * 2 = 2
# Step 2: 2 * 3 = 6
# Step 3: 6 * 4 = 24
# Step 4: 24 * 5 = 120

# --- PARTIAL: Fix some arguments of a function ---
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(f"square(5): {square(5)}")    # 25
print(f"cube(3): {cube(3)}")        # 27


# === FINAL VERIFICATION ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎓 CHAPTER 8 COMPLETE — YOU'VE FINISHED PYTHON BASICS!")
    print("=" * 60)
    print("""
Congratulations! You now know:
    Ch 1: Variables, types, operators, f-strings, immutability
    Ch 2: if/else, for/while loops, comprehensions, any/all
    Ch 3: Functions, scope (LEGB), lambda, recursion, closures, decorators
    Ch 4: List, dict, set, tuple, deque, Counter, defaultdict
    Ch 5: Strings, slicing, methods, regex, Unicode
    Ch 6: Classes, inheritance, polymorphism, dunder methods
    Ch 7: try/except, file I/O, JSON, CSV, pathlib, context managers
    Ch 8: Modules, iterators, generators, decorators, type hints, functools

YOUR LEARNING PATH FROM HERE:
    1. Read fundamentals/ (Big-O, DS basics)
    2. Read python-basics/ (this guide)
    3. Start solving Blind 75 problems (they'll make sense now!)
    4. Practice on leetcode.com or neetcode.io

    The pattern is: learn → practice → recognize → solve.
    You've done the learning. Now go practice! 🔥
""")
