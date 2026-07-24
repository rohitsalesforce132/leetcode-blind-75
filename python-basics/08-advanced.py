'''
CHAPTER 8: MODULES, ITERATORS, GENERATORS & DECORATORS
========================================================

"This final chapter covers the 'advanced' features that separate
beginners from professionals. Once you understand these, you can read
and write production-grade Python."

---

PART 1: MODULES — ORGANIZING CODE
===================================

Real-world analogy: A TOOLBOX.

    You don't carry all your tools loose in your pockets.
    You organize them into BOXES: one for screwdrivers, one for wrenches, etc.

A module is a Python file that contains functions, classes, and variables
you can import and reuse. This keeps code organized.
'''

# --- IMPORTING BUILT-IN MODULES ---
import math

print(math.pi)                    # 3.141592653589793
print(math.sqrt(144))             # 12.0
print(math.ceil(3.2))             # 4   (round up)
print(math.floor(3.8))            # 3   (round down)
print(math.factorial(5))          # 120

# --- IMPORT SPECIFIC ITEMS ---
from math import pi, sqrt         # Import only what you need
print(sqrt(64))                   # 8.0

# --- IMPORT WITH ALIAS ---
# Convention in data science: import numpy as np
# Then use: np.array([1, 2, 3])
# (We don't import numpy here — it's just to show the alias pattern)

# --- COLLECTIONS MODULE ---
from collections import Counter, defaultdict, deque

# Counter: automatic frequency counting
words = "the cat sat on the mat the cat".split()
c = Counter(words)
print(c.most_common(2))           # [('the', 3), ('cat', 2)]

# defaultdict: auto-initialize missing keys
dd = defaultdict(list)            # Missing key → empty list
dd["fruits"].append("apple")
dd["fruits"].append("banana")
print(dict(dd))                   # {'fruits': ['apple', 'banana']}

# deque: fast queue (O(1) at both ends)
dq = deque([1, 2, 3])
dq.appendleft(0)
dq.append(4)
print(list(dq))                   # [0, 1, 2, 3, 4]

# --- DATETIME MODULE ---
from datetime import datetime, timedelta

now = datetime.now()
print(f"Right now: {now}")

formatted = now.strftime("%Y-%m-%d %H:%M:%S")
print(f"Formatted: {formatted}")

# Date arithmetic
tomorrow = now + timedelta(days=1)
print(f"Tomorrow: {tomorrow.strftime('%Y-%m-%d')}")

# Parse a date string
parsed_date = datetime.strptime("2024-12-25", "%Y-%m-%d")
print(f"Parsed: {parsed_date}")

# --- OS MODULE ---
import os

print(f"Current directory: {os.getcwd()}")
print(f"Home directory: {os.path.expanduser('~')}")

# --- SYS MODULE ---
import sys

print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")

# Command line arguments
# sys.argv[0] = script name, sys.argv[1:] = arguments
print(f"Arguments: {sys.argv}")


'''
CREATING YOUR OWN MODULE ---
    Any .py file is a module. If you have a file called utils.py:

    # utils.py
    def greet(name):
        return f"Hello, {name}"

    PI = 3.14159

    Then in another file:
    # main.py
    import utils
    print(utils.greet("Manav"))     # Hello, Manav
    print(utils.PI)                 # 3.14159

    Or:
    from utils import greet, PI
    print(greet("Manav"))
'''

# --- RANDOM MODULE ---
import random

print(random.randint(1, 100))               # Random integer 1-100
print(random.choice(["apple", "banana"]))    # Random element from list
print(random.random())                       # Random float 0.0 to 1.0

# Shuffle a list in place
cards = [1, 2, 3, 4, 5]
random.shuffle(cards)
print(f"Shuffled: {cards}")

# Sample without replacement
print(random.sample(range(1, 50), 6))        # 6 unique random numbers


'''
PART 2: ITERATORS AND GENERATORS — MEMORY EFFICIENCY
======================================================

THE PROBLEM:
    Imagine reading a 10 GB file. If you load all of it into memory:
    → program crashes. Not enough RAM.

THE SOLUTION: ITERATORS / GENERATORS
    Instead of loading everything at once, produce ONE ITEM AT A TIME.
    Process it, then get the next. Memory usage: O(1), not O(n).

Real-world analogy: A WATER FAUCET vs A SWIMMING POOL.

    List = swimming pool. All water is there at once. Takes space.
    Generator = faucet. Water comes one cup at a time. Minimal space.

---

WHAT IS AN ITERATOR?
    An iterator is any object that can produce the "next" item.
    It remembers where it is. You call next() to get the next item.

    Every list, string, dict is ITERABLE (can be looped over).
    But they're not iterators themselves. Use iter() to create one.
'''

# --- ITERATOR BASICS ---
my_list = [10, 20, 30]
iterator = iter(my_list)        # Create an iterator from the list

print(next(iterator))           # 10
print(next(iterator))           # 20
print(next(iterator))           # 30
# print(next(iterator))         # StopIteration! Iterator is exhausted.


'''
HOW FOR LOOPS ACTUALLY WORK:
    for item in my_list:
        ...

    Python translates this to:
    iterator = iter(my_list)
    while True:
        try:
            item = next(iterator)
            # ... your loop body ...
        except StopIteration:
            break
'''

# --- BUILDING A CUSTOM ITERATOR ---
class Countdown:
    """Count down from n to 1. An iterator that yields values."""
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self                # The object IS its own iterator

    def __next__(self):
        if self.current <= 0:
            raise StopIteration     # Signal: no more items
        self.current -= 1
        return self.current + 1

# Using it
for num in Countdown(5):
    print(f"  T-minus {num}...")
print("  🚀 Lift off!")


'''
--- GENERATORS: THE EASY WAY ---

A generator is a function that produces values one at a time using 'yield'.
Instead of 'return' (which ends the function), 'yield' PAUSES the function,
returns the value, and resumes when next() is called again.

    return → function is DONE. One output.
    yield  → function PAUSES. Can produce MANY outputs.
'''

# --- GENERATOR FUNCTION ---
def count_up_to(n):
    """Generate numbers from 1 to n, one at a time."""
    current = 1
    while current <= n:
        yield current           # PAUSE here, return current, resume later
        current += 1            # Resumes from here on next() call

# Using the generator
for num in count_up_to(5):
    print(f"  Generated: {num}")
# Output: 1, 2, 3, 4, 5

# --- GENERATOR SAVES MEMORY ---
# range() is itself a generator-like object!
# range(1000000000) uses almost NO memory (doesn't create the numbers)
# [0, 1, 2, ..., 999999999] as a list would use ~8GB!

# --- INFINITE GENERATOR ---
def fibonacci():
    """Generate Fibonacci numbers forever (until you stop asking)."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Use itertools.islice to take only what you need
from itertools import islice

print("\n--- First 10 Fibonacci ---")
for fib_num in islice(fibonacci(), 10):
    print(f"  {fib_num}", end="")
print()  # 0 1 1 2 3 5 8 13 21 34

# --- GENERATOR EXPRESSIONSION ---
# Like list comprehensions but lazy (uses () instead of [])
squares_list = [x ** 2 for x in range(5)]       # Creates full list → [0, 1, 4, 9, 16]
squares_gen = (x ** 2 for x in range(5))        # Creates generator → lazy

print(list(squares_gen))                        # [0, 1, 4, 9, 16] (consumed when listed)

# Generator doesn't compute values until you ask for them!
gen = (x ** 2 for x in range(1000000000))       # Instant! No computation yet.
print(next(gen))                                # 0 (now it computes one)


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

---

PART 3: DECORATORS — MODIFYING FUNCTIONS
=========================================

Real-world analogy: GIFT WRAPPING.

    You have a gift (your function).
    You wrap it in nice paper (the decorator).
    The gift inside is unchanged, but now it has extra features (wrapping).

A decorator is a function that TAKES another function and EXTENDS its behavior
WITHOUT modifying the original function's code.

STEP 1: FUNCTIONS ARE FIRST-CLASS OBJECTS
    In Python, functions can be:
    - Assigned to variables
    - Passed as arguments to other functions
    - Returned from functions
'''

# --- FUNCTIONS AS ARGUMENTS ---
def shout(text):
    return text.upper()

def whisper(text):
    return text.lower()

# Pass a function as an argument
def greet(func):
    """Call whatever function is passed in."""
    return func("Hello, World!")

print(greet(shout))              # HELLO, WORLD!
print(greet(whisper))            # hello, world!


# --- A SIMPLE DECORATOR ---
def timing_decorator(func):
    """Measure how long a function takes."""
    import time

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)       # Call the original function
        elapsed = time.time() - start
        print(f"  [timer] {func.__name__} took {elapsed:.6f}s")
        return result

    return wrapper

# --- APPLYING A DECORATOR WITH @ ---
@timing_decorator
def slow_function():
    """Simulate a slow operation."""
    import time
    time.sleep(0.5)
    return "Done!"

print(slow_function())
# [timer] slow_function took 0.500123s
# Done!


'''
HOW DECORATORS WORK (step by step):

    @timing_decorator          ← This is syntactic sugar for:
    def slow_function():       #
        ...                    #   def slow_function():
                               #       ...
                               #   slow_function = timing_decorator(slow_function)

    1. Python sees @timing_decorator above the function
    2. It passes slow_function to timing_decorator
    3. timing_decorator returns 'wrapper'
    4. Now 'slow_function' actually points to 'wrapper'
    5. When you call slow_function(), you're actually calling wrapper()
    6. wrapper() runs the timing code, then calls the original function

DECORATOR ANATOMY:
    def decorator_name(func):          # Takes the original function
        def wrapper(*args, **kwargs):  # Defines a replacement
            # BEFORE the original function runs
            result = func(*args, **kwargs)
            # AFTER the original function runs
            return result
        return wrapper                 # Returns the replacement
'''

# --- PRACTICAL DECORATOR: CACHING / MEMOIZATION ---
def memoize(func):
    """Cache results so we don't recompute. Essential for DP!"""
    cache = {}

    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return wrapper

@memoize
def expensive_computation(n):
    """Simulate a slow computation."""
    import time
    time.sleep(0.1)     # Pretend this is slow
    return n * n

print(f"\n--- Memoization ---")
print(expensive_computation(5))    # Slow (~0.1s) — first call
print(expensive_computation(5))    # Instant! — cached result
print(expensive_computation(5))    # Instant! — cached result

# Python has this built-in!
from functools import lru_cache
# @lru_cache(maxsize=None)
# def fib(n):
#     ...


# --- DECORATOR WITH ARGUMENTS ---
def repeat(n):
    """Run the decorated function n times."""
    def decorator(func):
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

print(say_hi("Manav"))            # ['Hi, Manav!', 'Hi, Manav!', 'Hi, Manav!']


'''
COMMON USES FOR DECORATORS (IN REAL PROJECTS):
    1. @app.route("/path")          — Flask/Django URL routing
    2. @property                    — Turn a method into a read-only attribute
    3. @staticmethod / @classmethod — Already covered in Ch 6
    4. @functools.lru_cache         — Built-in memoization
    5. @dataclass                   — Auto-generate __init__, __repr__, etc.
    6. Custom logging/timing/auth decorators

---

PART 4: CONTEXT MANAGERS (THE 'with' STATEMENT)
=================================================

You've seen 'with open(...) as f:'. That's a context manager.
You can create your own with a class or a generator.
'''

# --- CONTEXT MANAGER USING A CLASS ---
class Timer:
    """Measure time spent in a code block."""
    def __enter__(self):
        import time
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.time() - self.start
        print(f"  Block took {self.elapsed:.4f}s")

with Timer():
    # Code to time
    sum(range(1000000))
# Block took 0.0312s

# --- CONTEXT MANAGER USING contextlib ---
from contextlib import contextmanager
import time as _time

@contextmanager
def timer(label="Block"):
    """Simpler way to create a context manager."""
    start = _time.time()
    try:
        yield                    # Code inside 'with' runs here
    finally:
        elapsed = _time.time() - start
        print(f"  {label} took {elapsed:.4f}s")

with timer("My operation"):
    total = sum(x ** 2 for x in range(100000))
    print(f"  Sum of squares: {total}")


'''
PART 5: TYPE HINTS (PYTHON 3.5+)
=================================
Type hints make your code self-documenting and catch bugs with tools
like mypy. They DON'T enforce types at runtime — they're just hints.
'''

# --- BASIC TYPE HINTS ---
def add(a: int, b: int) -> int:
    """The hints say: a and b are ints, return is an int."""
    return a + b

def greet(name: str) -> str:
    return f"Hello, {name}"

# --- TYPE HINTS FOR COLLECTIONS ---
from typing import List, Dict, Optional, Tuple

def process_items(items: List[int]) -> List[str]:
    """Convert list of ints to list of strings."""
    return [str(x) for x in items]

def get_config(key: str) -> Optional[str]:
    """Return config value or None if not found."""
    config = {"port": "8080"}
    return config.get(key)

# --- PYTHON 3.9+ ALLOWS LOWERCASE ---
def double_all(nums: list[int]) -> list[int]:
    return [n * 2 for n in nums]

# --- TYPE HINTS IN CLASSES ---
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def is_adult(self) -> bool:
        return self.age >= 18


'''
PART 6: FUNCTOOLS — UTILITY FUNCTIONS FOR FUNCTIONS
====================================================
'''

from functools import reduce

# --- REDUCE: Combine all elements into one ---
numbers = [1, 2, 3, 4, 5]
product = reduce(lambda a, b: a * b, numbers)
print(f"\nProduct of {numbers}: {product}")    # 120 (1×2×3×4×5)

# reduce step by step:
# Step 1: 1 * 2 = 3
# Step 2: 2 * 3 = 6
# Step 3: 6 * 4 = 24
# Step 4: 24 * 5 = 120


# === FINAL VERIFICATION ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎓 CHAPTER 8 COMPLETE — YOU'VE FINISHED PYTHON BASICS!")
    print("=" * 60)
    print("""
Congratulations! You now know:
    Ch 1: Variables, types, operators, f-strings
    Ch 2: if/else, for/while loops, comprehensions
    Ch 3: Functions, scope, lambda, recursion, pass-by-reference
    Ch 4: List, dict, set, tuple, deque, Counter, defaultdict
    Ch 5: Strings, slicing, methods, regex
    Ch 6: Classes, inheritance, polymorphism, dunder methods
    Ch 7: try/except, file I/O, JSON, CSV, pathlib
    Ch 8: Modules, iterators, generators, decorators, context managers

YOUR LEARNING PATH FROM HERE:
    1. Read fundamentals/ (Big-O, DS basics)
    2. Read python-basics/ (this guide)
    3. Start solving Blind 75 problems (they'll make sense now!)
    4. Practice on leetcode.com or neetcode.io

    The pattern is: learn → practice → recognize → solve.
    You've done the learning. Now go practice! 🔥
""")
