'''
CHAPTER 1: VARIABLES, DATA TYPES & OPERATORS
=============================================

"Before you can write logic, you need to store and manipulate data.
Variables are labeled boxes. Data types are what goes inside the boxes."

---

PART 1: WHAT IS A VARIABLE?
============================

Real-world analogy: A VARIABLE IS A LABELED BOX.

    ┌─────────┐
    │  42     │   ← The VALUE (what's inside)
    │         │   ← The NAME on the label ("age")
    └─────────┘
       "age"

    When you write:  age = 42
    Python creates a box, puts 42 inside, and slaps the label "age" on it.

    Later, you can look inside the box:  print(age)  →  42
    Or put something new inside:         age = 43    →  box now holds 43
'''

# --- CREATING VARIABLES (ASSIGNMENT) ---
name = "Manav"           # String (text)
age = 25                 # Integer (whole number)
height = 5.9             # Float (decimal)
is_student = True        # Boolean (True/False)

print(name)              # Manav
print(age)               # 25
print(height)            # 5.9
print(is_student)        # True

# --- MULTIPLE ASSIGNMENT ---
# Assign multiple variables at once:
x, y, z = 1, 2, 3
print(x, y, z)           # 1 2 3

# Assign same value to multiple:
a = b = c = 0
print(a, b, c)           # 0 0 0

# --- SWAPPING VARIABLES (Python trick) ---
# In most languages you need a temp variable. Python lets you swap in one line:
a, b = 10, 20
print(f"Before: a={a}, b={b}")    # Before: a=10, b=20
a, b = b, a
print(f"After:  a={a}, b={b}")    # After:  a=20, b=10


'''
NAMING RULES:
    - Must start with a letter or underscore:  my_var ✗   _private ✓
    - Can contain letters, digits, underscores:  my_var_2 ✓
    - Cannot start with a digit:                2var ✗
    - Case-sensitive:  name ≠ Name ≠ NAME
    - Cannot use reserved words:  for, if, class, def, import, etc.

CONVENTIONS (PEP 8 — Python Style Guide):
    - Use snake_case:  my_variable_name  (NOT camelCase or PascalCase)
    - Constants in UPPER_CASE:  MAX_RETRIES = 3
    - "Private" variables start with underscore:  _internal_data

---

PART 2: DATA TYPES — THE FIVE PRIMITIVES
=========================================

Python has 5 fundamental data types. Everything else is built from these.

1. INTEGER (int)    — whole numbers          → 42, -7, 0, 1000000
2. FLOAT (float)    — decimal numbers        → 3.14, -0.5, 2.0
3. STRING (str)     — text                   → "hello", 'world', """multi-line"""
4. BOOLEAN (bool)   — True or False          → True, False
5. NONE (NoneType)  — "nothing" / no value   → None

Each type behaves differently. Let's explore each.
'''

# ==========================================
# TYPE 1: INTEGER (int)
# ==========================================
# Whole numbers — positive, negative, or zero.

count = 42
temperature = -10
zero = 0

print(type(count))          # <class 'int'>
print(count + 8)            # 50  (addition)
print(count - 2)            # 40  (subtraction)
print(count * 2)            # 84  (multiplication)
print(count // 5)           # 8   (integer division — drops the decimal!)
print(count % 5)            # 2   (modulo — remainder after division)
print(count ** 2)           # 1764 (exponent — 42 squared)

# PYTHON INTEGERS HAVE NO SIZE LIMIT!
big = 10 ** 100             # googol — 1 followed by 100 zeros
print(len(str(big)))        # 101 digits. Python handles it fine.


# ==========================================
# TYPE 2: FLOAT (float)
# ==========================================
# Numbers with decimal points.

pi = 3.14159
gravity = 9.8
price = 19.99

print(type(pi))             # <class 'float'>
print(pi * 2)               # 6.28318
print(pi / 2)               # 1.570795
print(10 / 3)               # 3.3333333333333335 (float division)

# WARNING: FLOATING POINT IMPRECISION
# Computers store floats in binary, which can't represent some decimals exactly.
print(0.1 + 0.2)            # 0.30000000000000004  ← NOT exactly 0.3!
# This is a universal problem in ALL programming languages, not just Python.
# For money/currency, use the decimal module:
from decimal import Decimal
print(Decimal('0.1') + Decimal('0.2'))    # 0.3 (exact!)


# ==========================================
# TYPE 3: STRING (str)
# ==========================================
# Text — a sequence of characters enclosed in quotes.

single = 'Hello'
double = "World"
multi = """This is
a multi-line
string"""

print(type(single))         # <class 'str'>

# CONCATENATION (joining strings)
greeting = single + " " + double
print(greeting)             # Hello World

# REPETITION
print("Ha" * 3)             # HaHaHa

# INDEXING (access individual characters)
#    H  e  l  l  o
#    0  1  2  3  4    ← positive indices (from left)
#   -5 -4 -3 -2 -1    ← negative indices (from right)
word = "Hello"
print(word[0])              # H   (first character)
print(word[-1])             # o   (last character)

# SLICING (extract a substring)
#    Syntax: string[start:stop:step]
#    start is INCLUSIVE, stop is EXCLUSIVE
print(word[0:3])            # "Hel"   (indices 0,1,2)
print(word[1:])             # "ello"  (from index 1 to end)
print(word[:3])             # "Hel"   (from start to index 2)
print(word[::2])            # "Hlo"   (every 2nd character)
print(word[::-1])           # "olleH" (REVERSE a string!)


# ==========================================
# TYPE 4: BOOLEAN (bool)
# ==========================================
# Can only be True or False. Used for logic and decisions.

is_raining = True
has_license = False

print(type(is_raining))     # <class 'bool'>

# Booleans are actually integers in disguise!
# True = 1, False = 0
print(True + True)          # 2
print(True + False)         # 1
print(int(True))            # 1
print(int(False))           # 0


# ==========================================
# TYPE 5: NONE (NoneType)
# ==========================================
# Represents "nothing" or "no value." Like null in other languages.

result = None
print(type(result))         # <class 'NoneType'>
print(result)               # None

# Used when a function doesn't return anything meaningful,
# or as a placeholder before assigning a real value.


'''
PART 3: TYPE CONVERSION (CASTING)
==================================
Sometimes you need to convert between types.
'''

# String → Integer
num_str = "42"
num_int = int(num_str)
print(num_int + 8)          # 50

# Integer → String
age = 25
age_str = str(age)
print("I am " + age_str + " years old")   # I am 25 years old

# String → Float
price = float("19.99")
print(price)                # 19.99

# Float → Integer (truncates the decimal, does NOT round)
print(int(3.9))             # 3  (not 4!)

# Integer → Float
print(float(5))             # 5.0

# Any value → Boolean
# "Falsy" values: 0, 0.0, "", [], {}, None, False
# Everything else is "Truthy"
print(bool(0))              # False
print(bool(42))             # True
print(bool(""))             # False  (empty string)
print(bool("Hello"))        # True
print(bool([]))             # False  (empty list)
print(bool([1, 2]))         # True


'''
PART 4: OPERATORS — THE COMPLETE GUIDE
=======================================
'''

# --- ARITHMETIC OPERATORS ---
print("\n--- Arithmetic ---")
print(10 + 3)     # 13   Addition
print(10 - 3)     # 7    Subtraction
print(10 * 3)     # 30   Multiplication
print(10 / 3)     # 3.333...  True division (always returns float)
print(10 // 3)    # 3    Floor division (drops decimal)
print(10 % 3)     # 1    Modulo (remainder)
print(2 ** 10)    # 1024 Exponent (2 to the power of 10)

# --- COMPARISON OPERATORS (return True or False) ---
print("\n--- Comparison ---")
print(5 == 5)     # True   Equal to
print(5 != 3)     # True   Not equal to
print(5 > 3)      # True   Greater than
print(5 < 3)      # False  Less than
print(5 >= 5)     # True   Greater than or equal
print(5 <= 4)     # False  Less than or equal

# --- LOGICAL OPERATORS ---
print("\n--- Logical ---")
# AND: Both must be True
print(True and False)    # False
print(True and True)     # True
# OR: At least one must be True
print(True or False)     # True
print(False or False)    # False
# NOT: Reverses the boolean
print(not True)          # False
print(not False)         # True

# COMBINING LOGIC (real example)
age = 25
has_license = True
can_drive = (age >= 18) and has_license
print(f"\nCan drive? {can_drive}")    # True

# --- IDENTITY OPERATORS ---
# 'is' checks if two variables point to the SAME OBJECT (same memory location)
# '==' checks if the VALUES are equal
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)     # True  (same values)
print(a is b)     # False (different objects in memory)

# Rule: use '==' for comparing values. Use 'is' only for None, True, False.
print(a is not None)    # True  (proper way to check not-None)

# --- MEMBERSHIP OPERATORS ---
# 'in' checks if something exists inside a collection
print(3 in [1, 2, 3])          # True
print(5 in [1, 2, 3])          # False
print("a" in "apple")          # True
print("x" not in "apple")      # True


'''
PART 5: F-STRINGS — MODERN STRING FORMATTING
=============================================
f-strings are the Pythonic way to embed variables inside strings.
'''
name = "Manav"
age = 25
height = 5.9

# Basic usage: put variables inside { }
print(f"Hello, my name is {name}")
# → Hello, my name is Manav

# Expressions inside { }
print(f"In 5 years, I'll be {age + 5}")
# → In 5 years, I'll be 30

# Formatting numbers
print(f"Height: {height:.1f} feet")      # 1 decimal place → Height: 5.9 feet
print(f"Price: ${19.99:.2f}")            # 2 decimal places → Price: $19.99
print(f"Binary of 42: {42:#010b}")       # Binary → Binary of 42: 0b00101010
print(f"Big number: {1000000:,}")        # Thousands separator → Big number: 1,000,000

# Padding/alignment
print(f"[{'CENTER':^20}]")               # [      CENTER      ]
print(f"[{'LEFT':<20}]")                 # [LEFT                ]
print(f"[{'RIGHT':>20}]")                # [               RIGHT]


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 1 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Variables are labeled boxes. Use snake_case naming.
2. Five primitive types: int, float, str, bool, None.
3. Integer division // drops decimals. Regular division / returns float.
4. Modulo % gives the remainder. Exponent ** raises to power.
5. String slicing: [start:stop:step]. [::-1] reverses.
6. "Falsy" values: 0, "", [], {}, None. Everything else is truthy.
7. Use == for value comparison. Use 'is' only for None/True/False.
8. f-strings: f"Hello {name}" — cleanest way to format strings.

Next: Chapter 2 — Control Flow (if/else, loops, comprehensions)
""")
