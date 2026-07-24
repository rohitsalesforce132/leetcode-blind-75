'''
CHAPTER 3: FUNCTIONS, SCOPE & LAMBDA — THE COMPLETE DEEP DIVE
===============================================================

"Functions are the #1 tool for writing reusable code. Instead of writing
the same 10 lines 5 times, you write them ONCE in a function and call it 5 times.
This chapter teaches you everything about functions — from basics to advanced
concepts like closures, decorators, and recursion."

---

PART 1: WHAT IS A FUNCTION?
============================

Real-world analogy: A VENDING MACHINE.

    1. You put in INPUT (money + button number)
    2. The machine does something INSIDE (you don't care how)
    3. You get OUTPUT (a snack)

A function is the same:
    1. You give it INPUT (called "parameters" or "arguments")
    2. It runs some code
    3. It gives you OUTPUT (called the "return value")

    ┌───────────────────────────┐
    │   def add(a, b):          │
    │       return a + b        │
    └───────────────────────────┘
         ↑ input        ↑ output

WHY USE FUNCTIONS?
    1. REUSABILITY: Write once, use many times.
    2. ORGANIZATION: Break complex code into named, manageable chunks.
    3. TESTING: Test one function in isolation.
    4. ABSTRACTION: Hide complexity behind a simple interface.
'''

# --- DEFINING AND CALLING A FUNCTION ---
def greet(name):
    """Say hello to someone."""       # Docstring (documentation)
    message = f"Hello, {name}!"
    return message                    # Output

# CALL the function with an argument
result = greet("Manav")
print(result)                          # Hello, Manav!

# Call it again with different input
print(greet("World"))                  # Hello, World!

# A function with NO return value returns None:
def say_hello(name):
    print(f"Hi, {name}")              # No return → returns None

result = say_hello("Alice")           # Prints "Hi, Alice"
print(result)                          # None


'''
PART 2: FUNCTION ANATOMY — PARAMETERS AND ARGUMENTS
====================================================

    def  function_name  (parameters):    ← definition
    ↑        ↑              ↑
  keyword   name      inputs (optional)

         """Documentation string"""     ← optional but recommended

         # Function body (indented)
         result = do_something()

         return result                  ← output (optional)

TERMINOLOGY:
    PARAMETER: The variable in the function definition (what it EXPECTS)
    ARGUMENT: The actual value you pass when calling (what you GIVE)

    def greet(name):   ← 'name' is a PARAMETER
        ...

    greet("Manav")     ← "Manav" is an ARGUMENT
'''

# --- PARAMETERS WITH DEFAULT VALUES ---
def greet_with_time(name, greeting="Hello"):
    """Greet with a custom or default greeting."""
    return f"{greeting}, {name}!"

print(greet_with_time("Manav"))                  # Hello, Manav! (uses default)
print(greet_with_time("Manav", greeting="Hi"))   # Hi, Manav! (custom keyword)
print(greet_with_time("Manav", "Hey"))           # Hey, Manav! (positional)

# Default values are evaluated ONCE at definition time!
# This is why mutable defaults (like lst=[]) are dangerous — covered in pitfalls.

# --- KEYWORD ARGUMENTS ---
# Specify arguments by NAME (order doesn't matter)
def create_profile(name, age, city):
    return f"{name}, {age}, from {city}"

print(create_profile(name="Manav", city="Pune", age=25))
print(create_profile("Manav", 25, "Pune"))       # Positional also works

# --- POSITIONAL-ONLY AND KEYWORD-ONLY ARGUMENTS ---
# Python 3.8+ allows you to restrict how arguments are passed:

def strict_function(a, b, /, c, *, d):  # / before c, * before d
    """a, b: positional-only. c: either. d: keyword-only."""
    return a + b + c + d

print(strict_function(1, 2, 3, d=4))              # 10
# strict_function(1, 2, c=3, d=4)                # Also works
# strict_function(a=1, b=2, c=3, d=4)            # Error! a, b are positional-only

# --- *ARGS: VARIABLE NUMBER OF POSITIONAL ARGUMENTS ---
def sum_all(*args):
    """Sum any number of arguments. *args becomes a tuple."""
    print(f"  Type: {type(args)}, Values: {args}")
    return sum(args)

print(sum_all(1, 2, 3))               # Type: <class 'tuple'>, Values: (1, 2, 3) → 6
print(sum_all(1, 2, 3, 4, 5))         # → 15
print(sum_all())                       # → 0

# --- **KWARGS: VARIABLE KEYWORD ARGUMENTS ---
def print_info(**kwargs):
    """Accept any keyword arguments. **kwargs becomes a dict."""
    print(f"  Type: {type(kwargs)}, Values: {kwargs}")
    for key, value in kwargs.items():
        print(f"    {key}: {value}")

print_info(name="Manav", age=25, role="Engineer")

# --- COMBINING ALL PARAMETER TYPES ---
def complex_function(a, b, *args, **kwargs):
    """Standard + *args + **kwargs."""
    print(f"  a={a}, b={b}, args={args}, kwargs={kwargs}")

complex_function(1, 2, 3, 4, 5, name="test", debug=True)
# a=1, b=2, args=(3, 4, 5), kwargs={'name': 'test', 'debug': True}

# --- UNPACKING ARGUMENTS WITH * AND ** ---
def add_three(a, b, c):
    return a + b + c

numbers = [10, 20, 30]
print(add_three(*numbers))            # 60 (unpacks list into 3 args)

config = {"a": 1, "b": 2, "c": 3}
print(add_three(**config))            # 6 (unpacks dict into kwargs)


'''
PART 3: RETURN VALUES
=====================

    - A function can return ONE value:      return x
    - Or MULTIPLE values (as a tuple):      return x, y, z
    - If no return statement: returns None
    - 'return' alone (no value): returns None (exits function)
    - A function STOPS at the first return statement.
'''

# --- MULTIPLE RETURN VALUES ---
def min_max(numbers):
    """Return both the min and max of a list."""
    return min(numbers), max(numbers)      # Returns a tuple

lowest, highest = min_max([3, 7, 1, 9, 4])  # Tuple unpacking
print(f"Min: {lowest}, Max: {highest}")     # Min: 1, Max: 9

# --- EARLY RETURN (GUARD CLAUSE) ---
def is_adult(age):
    """Use early returns for cleaner code."""
    if age < 0:
        return None              # Invalid input → exit immediately
    if age >= 150:
        return None              # Unrealistic → exit
    return age >= 18             # Main logic

print(is_adult(25))              # True
print(is_adult(-5))              # None

# --- RETURNING DIFFERENT TYPES ---
def classify(number):
    """Return different types based on input."""
    if number < 0:
        return "negative"        # Returns str
    elif number == 0:
        return 0                 # Returns int
    elif number < 10:
        return [number]          # Returns list
    else:
        return True              # Returns bool

# This is VALID Python but BAD practice — inconsistent return types
# make code harder to use. Prefer consistent return types.


'''
PART 4: SCOPE — WHERE CAN YOU SEE A VARIABLE?
==============================================

Real-world analogy: OFFICE BUILDING.

    Top floor  (global scope)   → Everyone in the building can see
    Your desk  (local scope)     → Only you can see

LEGB Rule (Python's scope resolution order):
    L → Local        (inside the current function)
    E → Enclosing    (inside the outer function, for nested functions)
    G → Global       (at the top level of the script)
    B → Built-in     (print, len, range, etc.)

Python searches L → E → G → B. Uses the FIRST match it finds.
'''

# --- GLOBAL SCOPE ---
global_var = "I'm global"

def test_scope():
    local_var = "I'm local"
    print(global_var)     # ✓ Can READ global from inside function
    print(local_var)      # ✓ Can read local

test_scope()
# print(local_var)        # ✗ NameError! local_var doesn't exist outside

# --- LOCAL SCOPE ---
def calculate():
    result = 42           # result is LOCAL to calculate()
    return result

# print(result)           # ✗ NameError! result only exists inside calculate()

# --- MODIFYING GLOBAL FROM INSIDE ---
counter = 0

def increment_wrong():
    # counter += 1       # ✗ UnboundLocalError! Python thinks 'counter' is local
    pass

def increment_correct():
    global counter       # Tell Python: "I want to modify the GLOBAL counter"
    counter += 1

increment_correct()
print(f"Counter: {counter}")    # 1

# BEST PRACTICE: Avoid 'global' — pass values as parameters and return results.

# --- NONLOCAL (for nested functions) ---
def outer():
    x = "outer value"

    def inner():
        nonlocal x        # Modify the ENCLOSING function's variable
        x = "inner value"

    inner()
    print(f"x is now: {x}")    # inner value (modified by inner())

outer()

# --- CLOSURES (functions that remember their environment) ---
def make_multiplier(factor):
    """Return a function that multiplies by 'factor'."""
    def multiply(x):
        return x * factor    # 'factor' is remembered from the enclosing scope
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))             # 10
print(triple(5))             # 15
# 'double' remembers factor=2. 'triple' remembers factor=3.
# This is a CLOSURE — the inner function "closes over" the enclosing variable.


'''
PART 5: LAMBDA FUNCTIONS (ANONYMOUS FUNCTIONS)
================================================

A lambda is a tiny one-line function with NO NAME.
Use it when you need a quick function and don't want to write a full def.

    Regular function:   def square(x): return x ** 2
    Lambda equivalent:  lambda x: x ** 2

ANATOMY:
    lambda parameters: expression
          ↑              ↑
       inputs         single expression (NO statements, just one expression)

WHY USE LAMBDA?
    - Short, throwaway functions
    - Passing as arguments to sorted(), filter(), map()
    - When the function is too simple to warrant a name
'''

# --- LAMBDA BASICS ---
square = lambda x: x ** 2
print(square(5))               # 25

add = lambda a, b: a + b
print(add(3, 7))               # 10

# Lambda with default argument
greet_lambda = lambda name="World": f"Hello, {name}!"
print(greet_lambda())          # Hello, World!

# --- WHERE LAMBDAS SHINE ---

# 1. SORTING with a custom key
students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]

# Sort by grade (second element):
sorted_by_grade = sorted(students, key=lambda s: s[1], reverse=True)
print(f"By grade: {sorted_by_grade}")

# Sort by name length:
sorted_by_name_len = sorted(students, key=lambda s: len(s[0]))
print(f"By name length: {sorted_by_name_len}")

# Sort dict by value:
prices = {"apple": 1.5, "banana": 0.5, "cherry": 3.0}
sorted_prices = sorted(prices.items(), key=lambda item: item[1])
print(f"Sorted by price: {sorted_prices}")

# 2. FILTERING with lambda
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Evens: {evens}")

# 3. MAPPING (transform each element)
squared = list(map(lambda x: x ** 2, numbers))
print(f"Squared: {squared}")

# 4. REDUCE (combine all elements into one)
from functools import reduce
product = reduce(lambda a, b: a * b, [1, 2, 3, 4, 5])
print(f"Product: {product}")    # 120

# LAMBDA vs DEF — WHEN TO USE WHICH?
# Use lambda when:
#   - It's a simple one-line expression
#   - You're passing it as an argument (sorted, filter, map)
#   - You won't reuse it elsewhere
#
# Use def when:
#   - The logic is more than one line
#   - You need to reuse the function
#   - You need documentation (docstring)
#   - You need complex logic (if/else, loops)


'''
PART 6: RECURSION — FUNCTIONS THAT CALL THEMSELVES
===================================================

A recursive function calls ITSELF to solve a smaller version of the same problem.

Real-world analogy: Russian nesting dolls.
    You open a doll, find another doll inside, open that, repeat,
    until you find the smallest solid doll (base case).

EVERY RECURSIVE FUNCTION NEEDS:
    1. BASE CASE: When to stop (prevents infinite recursion)
    2. RECURSIVE CASE: Call itself with a smaller input
'''

# --- FACTORIAL ---
# 5! = 5 × 4 × 3 × 2 × 1 = 120
def factorial(n):
    if n <= 1:
        return 1                    # BASE CASE: 0! = 1, 1! = 1
    return n * factorial(n - 1)     # RECURSIVE: n! = n × (n-1)!

print(f"5! = {factorial(5)}")      # 120

# CALL STACK VISUALIZATION:
# factorial(5) = 5 * factorial(4)
#                      4 * factorial(3)
#                           3 * factorial(2)
#                                2 * factorial(1)
#                                     1          ← base case, start returning
#                                2 * 1 = 2
#                           3 * 2 = 6
#                      4 * 6 = 24
#               5 * 24 = 120  ← final answer

# --- FIBONACCI ---
def fib(n):
    if n <= 1:
        return n                    # Base: fib(0)=0, fib(1)=1
    return fib(n - 1) + fib(n - 2)  # Sum of previous two

print(f"fib(10) = {fib(10)}")      # 55

# WARNING: Naive Fibonacci is O(2^n) — exponential! Very slow for n > 35.
# Use memoization (lru_cache) to fix this:
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_fast(n):
    if n <= 1:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)

print(f"fib_fast(100) = {fib_fast(100)}")   # Instant! (memoization)

# --- RECURSION vs ITERATION ---
# Any recursive function can be written iteratively (with a loop).
# Recursive approach: elegant, matches problem structure (trees, graphs).
# Iterative approach: no stack overflow risk, often faster.
# Python limit: ~1000 recursive calls (sys.getrecursionlimit()).


'''
PART 7: FIRST-CLASS FUNCTIONS — FUNCTIONS AS DATA
===================================================

In Python, functions are FIRST-CLASS OBJECTS. This means:
    - Functions can be assigned to variables
    - Functions can be passed as arguments
    - Functions can be returned from other functions
    - Functions can be stored in data structures
'''

# --- ASSIGNING FUNCTIONS TO VARIABLES ---
def shout(text):
    return text.upper()

def whisper(text):
    return text.lower()

yell = shout    # Assign function to variable (no parentheses!)
print(yell("Hello"))    # HELLO

# --- FUNCTIONS IN A LIST ---
operations = [shout, whisper, str.title]
for op in operations:
    print(op("hello world"))

# --- FUNCTIONS IN A DICTIONARY (command pattern) ---
commands = {
    "uppercase": shout,
    "lowercase": whisper,
    "capitalize": str.title,
}

action = "uppercase"
result = commands[action]("hello world")
print(result)   # HELLO WORLD

# --- FUNCTIONS AS ARGUMENTS (higher-order functions) ---
def apply_twice(func, value):
    """Apply a function twice to a value."""
    return func(func(value))

print(apply_twice(lambda x: x + 3, 5))   # 11  ((5+3)+3)
print(apply_twice(lambda x: x * 2, 3))   # 12  ((3*2)*2)


'''
PART 8: DECORATORS — MODIFYING FUNCTIONS
=========================================

A decorator is a function that TAKES another function and EXTENDS its
behavior WITHOUT modifying the original function's code.

Analogy: GIFT WRAPPING. The gift (original function) is unchanged,
but the wrapping (decorator) adds features.
'''

import time

def timing_decorator(func):
    """Measure how long a function takes."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)       # Call original
        elapsed = time.time() - start
        print(f"  [timer] {func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper

# --- APPLYING A DECORATOR WITH @ ---
@timing_decorator
def slow_function():
    """Simulate a slow operation."""
    time.sleep(0.1)
    return "Done!"

print(slow_function())
# [timer] slow_function took 0.100123s
# Done!

# @timing_decorator is shorthand for:
# slow_function = timing_decorator(slow_function)

# --- PRACTICAL DECORATOR: MEMOIZATION (CACHING) ---
def memoize(func):
    """Cache results to avoid recomputation."""
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def expensive_square(n):
    """Simulate an expensive computation."""
    time.sleep(0.01)
    return n * n

print(expensive_square(5))    # Slow (~0.01s)
print(expensive_square(5))    # Instant! (cached)
print(expensive_square(5))    # Instant! (cached)

# Python has this built-in:
# from functools import lru_cache
# @lru_cache(maxsize=None)


'''
PART 9: COMMON PITFALLS
========================
'''

# --- PITFALL 1: MUTABLE DEFAULT ARGUMENTS ---
# BAD: Default list is shared across ALL calls!
def add_item_bad(item, lst=[]):
    lst.append(item)
    return lst
print(add_item_bad(1))     # [1]
print(add_item_bad(2))     # [1, 2] — NOT [2]!

# WHY: The default [] is created ONCE when the function is defined.
# Every call that doesn't pass lst uses the SAME list object.

# GOOD: Use None as default
def add_item_good(item, lst=None):
    if lst is None:
        lst = []            # Create a NEW list each time
    lst.append(item)
    return lst

print(add_item_good(1))    # [1]
print(add_item_good(2))    # [2] ← correct!

# --- PITFALL 2: LATE BINDING IN CLOSURES ---
# Creating functions in a loop:
funcs = []
for i in range(3):
    funcs.append(lambda: i)    # All capture the SAME variable i

print([f() for f in funcs])   # [2, 2, 2] — NOT [0, 1, 2]!

# FIX: Use default argument to capture the current value:
funcs = []
for i in range(3):
    funcs.append(lambda i=i: i)    # i=i captures current value

print([f() for f in funcs])   # [0, 1, 2] ← correct!

# --- PITFALL 3: FORGETTING return ---
def add_wrong(a, b):
    a + b            # No return → returns None!

def add_right(a, b):
    return a + b     # Correct

print(add_wrong(3, 4))   # None (forgot return!)
print(add_right(3, 4))   # 7

# --- PITFALL 4: MODIFYING MUTABLE ARGUMENTS ---
def add_item(lst, item):
    """This modifies the ORIGINAL list (surprising!)."""
    lst.append(item)

my_list = [1, 2, 3]
add_item(my_list, 99)
print(my_list)  # [1, 2, 3, 99] — original modified!

# If you don't want this, return a NEW list:
def add_item_safe(lst, item):
    return lst + [item]    # Creates new list, original unchanged


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 3 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Functions take input (params), do work, return output.
2. Default params, *args (tuple), **kwargs (dict) for flexibility.
3. Multiple return values: return a, b → unpack as x, y = func().
4. Scope (LEGB): Local → Enclosing → Global → Built-in.
5. 'global' modifies globals (avoid). 'nonlocal' modifies enclosing.
6. Closures: inner functions remember enclosing variables.
7. Lambda: one-line anonymous function. Use with sorted/filter/map.
8. Recursion: base case + call self. Mind the call stack limit.
9. Functions are first-class: assign, pass, return, store.
10. Decorators: @decorator wraps a function to extend behavior.
11. NEVER use mutable default arguments (lst=[]) → use None.

Next: Chapter 4 — Data Structures Deep Dive
""")
