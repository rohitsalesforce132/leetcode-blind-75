'''
CHAPTER 3: FUNCTIONS, SCOPE & LAMBDA
=====================================

"Functions are the #1 tool for writing reusable code. Instead of writing
the same 10 lines 5 times, you write them ONCE in a function and call it 5 times."

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
'''

# --- DEFINING AND CALLING A FUNCTION ---
def greet(name):
    """Say hello to someone."""       # This is a docstring (documentation)
    message = f"Hello, {name}!"
    return message

# CALL the function with an argument
result = greet("Manav")
print(result)                          # Hello, Manav!

# Call it again with different input
print(greet("World"))                  # Hello, World!


'''
PART 2: FUNCTION ANATOMY
=========================
'''

#   def  function_name  (parameters):    ← definition
#    ↑       ↑              ↑
#  keyword  name      inputs (optional)
#
#        """Documentation string"""     ← optional but recommended
#
#        # Function body (indented)
#        result = do_something()
#
#        return result                  ← output (optional)

# --- PARAMETERS WITH DEFAULT VALUES ---
# If the caller doesn't provide a value, use the default
def greet_with_time(name, greeting="Hello"):
    """Greet with a custom or default greeting."""
    return f"{greeting}, {name}!"

print(greet_with_time("Manav"))                  # Hello, Manav! (default)
print(greet_with_time("Manav", greeting="Hi"))   # Hi, Manav! (custom)
print(greet_with_time("Manav", "Hey"))           # Hey, Manav! (positional)

# --- KEYWORD ARGUMENTS ---
# You can specify arguments by NAME (order doesn't matter then)
def create_profile(name, age, city):
    return f"{name}, {age}, from {city}"

print(create_profile(name="Manav", city="Pune", age=25))   # Order doesn't matter!
print(create_profile("Manav", 25, "Pune"))                  # Positional also works


# --- *ARGS: VARIABLE NUMBER OF ARGUMENTS ---
# When you don't know how many arguments will be passed
def sum_all(*args):
    """Sum any number of arguments. *args is a tuple."""
    print(f"  args type: {type(args)}, values: {args}")
    return sum(args)

print(sum_all(1, 2, 3))                # 6
print(sum_all(1, 2, 3, 4, 5))          # 15
print(sum_all())                        # 0


# --- **KWARGS: VARIABLE KEYWORD ARGUMENTS ---
def print_info(**kwargs):
    """Accept any number of keyword arguments. **kwargs is a dict."""
    print(f"  kwargs type: {type(kwargs)}, values: {kwargs}")
    for key, value in kwargs.items():
        print(f"    {key}: {value}")

print_info(name="Manav", age=25, role="DevOps Engineer")
# kwargs type: <class 'dict'>, values: {'name': 'Manav', 'age': 25, 'role': 'DevOps Engineer'}


# --- COMBINING ALL PARAMETER TYPES ---
def mix(a, b, *args, **kwargs):
    """Standard params + *args + **kwargs."""
    print(f"  a={a}, b={b}, args={args}, kwargs={kwargs}")

mix(1, 2, 3, 4, 5, name="test", debug=True)
# a=1, b=2, args=(3, 4, 5), kwargs={'name': 'test', 'debug': True}


'''
RETURN VALUES
-------------
    - A function can return ONE value:      return x
    - Or MULTIPLE values (as a tuple):      return x, y, z
    - If no return statement: returns None
    - 'return' alone (no value): returns None (exits the function)
'''

# --- MULTIPLE RETURN VALUES ---
def min_max(numbers):
    """Return both the min and max of a list."""
    return min(numbers), max(numbers)      # Returns a tuple

lowest, highest = min_max([3, 7, 1, 9, 4])  # Unpack the tuple
print(f"Min: {lowest}, Max: {highest}")     # Min: 1, Max: 9


# --- EARLY RETURN ---
def is_adult(age):
    """Use 'return' to exit a function early."""
    if age < 0:
        return None              # Exit immediately, return None
    return age >= 18

print(is_adult(25))              # True
print(is_adult(-5))              # None


'''
PART 3: SCOPE — WHERE CAN YOU SEE A VARIABLE?
==============================================

Real-world analogy: OFFICE BUILDING.

    Top floor  (global scope)   → Everyone in the building can see
    Your desk  (local scope)     → Only you can see
    Your drawer (enclosing)      → Only your room can see

LEGB Rule (Python's scope resolution order):
    L → Local        (inside the current function)
    E → Enclosing    (inside the outer function, for nested functions)
    G → Global       (at the top level of the script)
    B → Built-in     (print, len, range, etc.)
'''

# --- GLOBAL SCOPE ---
global_var = "I'm global"

def test_scope():
    # --- LOCAL SCOPE ---
    local_var = "I'm local"

    print(global_var)     # ✓ Can read global from inside function
    print(local_var)      # ✓ Can read local

test_scope()
# print(local_var)        # ✗ ERROR! local_var doesn't exist outside the function


# --- MODIFYING GLOBAL FROM INSIDE A FUNCTION ---
counter = 0

def increment():
    # counter += 1       # ✗ ERROR! Can't modify global without 'global' keyword
    pass

def increment_correct():
    global counter       # Tell Python: "I want to modify the global counter"
    counter += 1

increment_correct()
print(f"Counter: {counter}")    # 1


# --- NONLOCAL (for nested functions) ---
def outer():
    x = "outer"

    def inner():
        nonlocal x        # Tell Python: "I want to modify the enclosing x"
        x = "inner"

    inner()
    print(f"x is now: {x}")    # inner

outer()


'''
PART 4: LAMBDA FUNCTIONS (ANONYMOUS FUNCTIONS)
================================================

A lambda is a tiny one-line function with NO NAME.
Use it when you need a quick function and don't want to write a full def.

    Regular function:   def square(x): return x ** 2
    Lambda equivalent:  lambda x: x ** 2

ANATOMY:
    lambda parameters: expression
          ↑              ↑
       inputs         single expression (NO statements, just one expression)
'''

# --- LAMBDA BASICS ---
square = lambda x: x ** 2
print(square(5))               # 25

add = lambda a, b: a + b
print(add(3, 7))               # 10

# Lambda with default argument
greet_lambda = lambda name="World": f"Hello, {name}!"
print(greet_lambda())          # Hello, World!
print(greet_lambda("Manav"))   # Hello, Manav!


# --- WHERE LAMBDAS SHINE: SORTING AND FILTERING ---

# 1. SORTING with a custom key
students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]

# Sort by grade (second element) using lambda as the key function
sorted_by_grade = sorted(students, key=lambda student: student[1], reverse=True)
print(f"\nSorted by grade: {sorted_by_grade}")
# [('Bob', 92), ('Alice', 85), ('Charlie', 78)]

# Sort by name length
sorted_by_name_len = sorted(students, key=lambda s: len(s[0]))
print(f"Sorted by name length: {sorted_by_name_len}")

# 2. FILTERING with lambda
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Get only even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Even numbers: {evens}")     # [2, 4, 6, 8, 10]

# 3. MAPPING (transform each element)
squared = list(map(lambda x: x ** 2, numbers))
print(f"Squared: {squared}")        # [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]


'''
LAMBDA vs REGULAR FUNCTION — WHEN TO USE WHICH?
    Use lambda when:
    - It's a simple one-line expression
    - You're passing it as an argument (sorted, filter, map)
    - You won't reuse it elsewhere

    Use def when:
    - The logic is more than one line
    - You need to reuse the function
    - You need documentation (docstring)
    - You need complex logic (if/else, loops)

---

PART 5: PASS-BY-REFERENCE GOTCHA (Crucial Interview Topic)
===========================================================

This is the #1 source of bugs in Python. Pay close attention.
'''

# --- IMMUTABLE TYPES: int, float, str, bool, tuple ---
# When you "modify" an immutable, Python creates a NEW object.
def add_ten(num):
    num += 10
    print(f"  Inside function: num = {num}")

x = 5
add_ten(x)
print(f"  Outside function: x = {x}")     # Still 5! Unchanged.

# --- MUTABLE TYPES: list, dict, set ---
# When you modify a mutable, the original changes too!
def add_item(lst):
    lst.append(99)
    print(f"  Inside function: lst = {lst}")

my_list = [1, 2, 3]
add_item(my_list)
print(f"  Outside function: my_list = {my_list}")  # [1, 2, 3, 99]! Changed!

# WHY? Because lists are passed by REFERENCE.
# The function gets a pointer to the SAME list, not a copy.

# HOW TO AVOID THIS: Pass a copy
def safe_add_item(lst):
    lst = lst.copy()     # Work on a COPY
    lst.append(99)
    print(f"  Inside (safe): lst = {lst}")

my_list2 = [1, 2, 3]
safe_add_item(my_list2)
print(f"  Outside (safe): my_list2 = {my_list2}")  # [1, 2, 3] unchanged!


'''
THE GOLDEN RULE:
    - Immutable types (int, str, tuple): Safe. Modifications don't affect the original.
    - Mutable types (list, dict): DANGEROUS. Modifications INSIDE a function
      affect the original. If you don't want that, pass a .copy().

---

PART 6: RECURSION — FUNCTIONS THAT CALL THEMSELVES
===================================================

A recursive function calls ITSELF to solve a smaller version of the same problem.

Real-world analogy: Looking inside a nested set of Russian dolls.
    You open a doll, find another doll inside, open that one, repeat,
    until you find the smallest solid doll (base case).

EVERY RECURSIVE FUNCTION NEEDS:
    1. BASE CASE: When to stop (prevents infinite recursion)
    2. RECURSIVE CASE: Call itself with a smaller input
'''

# --- EXAMPLE 1: FACTORIAL ---
# 5! = 5 × 4 × 3 × 2 × 1 = 120
def factorial(n):
    if n <= 1:
        return 1                    # BASE CASE: 0! = 1, 1! = 1
    return n * factorial(n - 1)     # RECURSIVE CASE: n! = n × (n-1)!

print(f"\n5! = {factorial(5)}")    # 120

# HOW IT WORKS (call stack):
# factorial(5) = 5 * factorial(4)
#                      4 * factorial(3)
#                           3 * factorial(2)
#                                2 * factorial(1)
#                                     1          ← base case, start returning
#                                2 * 1 = 2
#                           3 * 2 = 6
#                      4 * 6 = 24
#               5 * 24 = 120  ← final answer

# --- EXAMPLE 2: FIBONACCI ---
# 0, 1, 1, 2, 3, 5, 8, 13, 21, ...
# Each number = sum of previous two
def fib(n):
    if n <= 1:
        return n                    # Base: fib(0)=0, fib(1)=1
    return fib(n - 1) + fib(n - 2)  # Recursive: sum of previous two

print(f"fib(10) = {fib(10)}")      # 55


'''
RECURSION vs ITERATION:
    Recursion is elegant but uses more memory (call stack).
    Every recursive call adds a frame to the call stack.
    Too many recursive calls → Stack Overflow error.
    Python default limit: ~1000 recursive calls.

    In interviews: recursion is often the most natural approach for
    tree/graph problems. Learn it well.
'''

# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 3 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Functions take input (params), do work, return output.
2. Default params, *args (tuple), **kwargs (dict) for flexibility.
3. Scope (LEGB): Local → Enclosing → Global → Built-in.
4. Lambda: one-line anonymous function. Use with sorted/filter/map.
5. IMMUTABLE types (int, str) are safe. MUTABLE types (list, dict)
   are modified in-place — pass .copy() to protect the original.
6. Recursion: base case + call self with smaller input.
   Every tree/graph problem uses this.

Next: Chapter 4 — Data Structures Deep Dive (list, dict, set, tuple)
""")
