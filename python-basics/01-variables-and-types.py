'''
CHAPTER 1: VARIABLES, DATA TYPES & OPERATORS — THE COMPLETE DEEP DIVE
======================================================================

"Before you can write logic, you need to store and manipulate data.
Variables are labeled boxes. Data types are what goes inside the boxes.
This chapter teaches you the fundamental building blocks of ALL Python code."

---

PART 1: WHAT IS A VARIABLE? — DYNAMIC TYPING IN PYTHON
=======================================================

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

HOW PYTHON VARIABLES WORK UNDER THE HOOD:
    Python is DYNAMICALLY TYPED. This means:

    1. You don't declare types. Python figures them out automatically.
       age = 25        → Python knows this is an int
       name = "Manav"  → Python knows this is a str

    2. Variables can change type at runtime.
       x = 10          → x is an int
       x = "hello"     → now x is a str (perfectly valid in Python!)
       x = [1, 2, 3]   → now x is a list

    3. Variables are REFERENCES (labels), not the objects themselves.
       Think of a variable as a NAMETAG pointing to an object in memory.

       age = 25    → "age" is a nametag pointing to the integer object 25
       new_age = age  → "new_age" is ANOTHER nametag pointing to the SAME 25

       age = 26    → "age" now points to a NEW object 26
                     "new_age" still points to 25 (unchanged!)

    ┌─────────┐         ┌─────────┐
    │  age ───────────> │   26    │  (age reassigned to new object)
    └─────────┘         └─────────┘
    ┌─────────┐         ┌─────────┐
    │ new_age ─────────>│   25    │  (still points to original 25)
    └─────────┘         └─────────┘

    This distinction is CRITICAL for understanding mutable vs immutable
    types (covered in Part 3).
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

# --- CHECKING THE TYPE ---
print(type(age))         # <class 'int'>
print(type(name))        # <class 'str'>
print(type(is_student))  # <class 'bool'>

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

# How it works under the hood:
# Python creates a temporary tuple (20, 10), then unpacks it into a and b.

# --- AUGMENTED ASSIGNMENT ---
count = 10
count += 5    # same as count = count + 5 → 15
count -= 3    # same as count = count - 3 → 12
count *= 2    # same as count = count * 2 → 24
count //= 5   # same as count = count // 5 → 4
count **= 3   # same as count = count ** 3 → 64
count %= 10   # same as count = count % 10 → 4


'''
NAMING RULES AND CONVENTIONS
=============================
RULES (Python enforces these — violations cause SyntaxError):
    1. Must start with a letter or underscore:  _name ✓   2name ✗
    2. Can contain letters, digits, underscores:  my_var_2 ✓
    3. Cannot start with a digit:                2var ✗
    4. Case-sensitive:  name ≠ Name ≠ NAME
    5. Cannot use reserved words:  for, if, class, def, import, etc.

CONVENTIONS (PEP 8 — Python Style Guide):
    - Variables: snake_case      → first_name, total_count, is_valid
    - Constants: UPPER_CASE      → MAX_RETRIES, PI, DEFAULT_TIMEOUT
    - Private:   _leading_underscore → _internal_data, _cache
    - "Dunder":  __double_underscore → __init__, __str__, __name__
    - Functions: snake_case      → calculate_total, process_payment
    - Classes:   PascalCase      → CustomerOrder, PaymentGateway

NAMING BEST PRACTICES:
    ✓ Good: student_count, is_logged_in, calculate_area()
    ✗ Bad:  x, y, n, sc, flag, data, temp (too vague)

    Be DESCRIPTIVE. Code is read 10× more than it's written.
    The variable name should tell the reader WHAT it holds.

    ✓ Good: elapsed_seconds, max_connections, error_message
    ✗ Bad:  t, maxc, err
'''

# Examples of good and bad naming
# BAD:
x = 25          # What is x?
l = [1, 2, 3]   # Is that a 1 or an l? Never use lowercase L as a variable!
o = 0           # Is that a 0 or an O? Never use uppercase O!

# GOOD:
student_age = 25
numbers_list = [1, 2, 3]
total_count = 0


'''
PART 2: DATA TYPES — THE FIVE PRIMITIVES
==========================================

Python has 5 fundamental data types. Everything else is built from these.

1. INTEGER (int)    — whole numbers          → 42, -7, 0, 1000000
2. FLOAT (float)    — decimal numbers        → 3.14, -0.5, 2.0
3. STRING (str)     — text                   → "hello", 'world', """multi-line"""
4. BOOLEAN (bool)   — True or False          → True, False
5. NONE (NoneType)  — "nothing" / no value   → None

Each type behaves differently. Let's explore each in depth.
'''

# ============================================================
# TYPE 1: INTEGER (int) — THE WHOLE NUMBER
# ============================================================

count = 42
temperature = -10
zero = 0
big_number = 1_000_000  # Underscores for readability (Python 3.6+). Same as 1000000.

print(type(count))          # <class 'int'>

# --- INTEGER OPERATIONS ---
print(10 + 3)               # 13   Addition
print(10 - 3)               # 7    Subtraction
print(10 * 3)               # 30   Multiplication
print(10 / 3)               # 3.333...  TRUE division (always returns float!)
print(10 // 3)              # 3    Floor division (drops the decimal)
print(10 % 3)               # 1    Modulo (remainder after division)
print(10 ** 3)              # 1000 Exponent (10 to the power of 3)

# --- CRITICAL: DIVISION VS FLOOR DIVISION ---
# / always returns a FLOAT, even for integers:
print(type(10 / 2))         # <class 'float'>  (result is 5.0, not 5)
# // returns an INT for integer inputs:
print(type(10 // 2))        # <class 'int'>    (result is 5)

# --- NEGATIVE FLOOR DIVISION (Common Trap!) ---
# Floor division ROUNDS DOWN (toward negative infinity), not toward zero:
print(7 // 2)               # 3   (3.5 rounds down to 3)
print(-7 // 2)              # -4  (-3.5 rounds down to -4, NOT -3!)

# --- MODULO WITH NEGATIVES ---
print(-7 % 3)               # 2  (Python's modulo always returns non-negative
                                  # when the divisor is positive)
print(7 % -3)               # -2 (sign follows the divisor)

# --- PYTHON INTEGERS HAVE NO SIZE LIMIT ---
big = 10 ** 100             # googol — 1 followed by 100 zeros
print(len(str(big)))        # 101 digits. Python handles it fine.
# In languages like C/Java, integers overflow at 2^31 or 2^63.
# Python automatically uses arbitrary precision for large numbers.


# ============================================================
# TYPE 2: FLOAT (float) — THE DECIMAL NUMBER
# ============================================================

pi = 3.14159
gravity = 9.8
price = 19.99
negative_float = -0.001

print(type(pi))             # <class 'float'>

# Scientific notation:
avogadro = 6.022e23        # 6.022 × 10^23
print(avogadro)             # 6.022e+23

# Float operations
print(pi * 2)               # 6.28318
print(pi / 2)               # 1.570795
print(pi + 1)               # 4.14159 (int + float = float)
print(2.5 * 4)              # 10.0 (float × int = float)

# --- FLOATING POINT IMPRECISION (CRITICAL!) ---
# Computers store floats in binary, which can't represent some decimals exactly.
# This is NOT a Python bug — it's a universal problem in ALL programming languages.
print(0.1 + 0.2)            # 0.30000000000000004  ← NOT exactly 0.3!
print(0.1 + 0.2 == 0.3)     # False! (The famous floating point gotcha)

# VISUALIZATION:
# 0.1 in binary is an infinite repeating fraction:
# 0.0001100110011001100110011001100110011...
# Python truncates it, causing tiny errors.

# HOW TO COMPARE FLOATS:
import math
print(math.isclose(0.1 + 0.2, 0.3))    # True (use math.isclose, not ==)

# HOW TO HANDLE MONEY/CURRENCY:
# NEVER use floats for money. Use the decimal module:
from decimal import Decimal
print(Decimal('0.1') + Decimal('0.2'))  # 0.3 (exact!)


# ============================================================
# TYPE 3: STRING (str) — THE TEXT TYPE
# ============================================================

single = 'Hello'
double = "World"
multi = """This is
a multi-line
string"""
raw = r"C:\Users\name\file.txt"   # Raw string: backslashes are literal

print(type(single))         # <class 'str'>

# CONCATENATION (joining strings)
greeting = single + " " + double
print(greeting)             # Hello World

# REPETITION
print("Ha" * 3)             # HaHaHa

# INDEXING (access individual characters — covered in detail in Chapter 5)
word = "Hello"
print(word[0])              # 'H'   (first character, index 0)
print(word[-1])             # 'o'   (last character)

# SLICING (extract a substring)
print(word[0:3])            # "Hel"   (indices 0, 1, 2)
print(word[::-1])           # "olleH" (REVERSE — common trick!)

# STRING LENGTH
print(len("Hello"))         # 5

# --- STRINGS ARE IMMUTABLE ---
# You CANNOT change individual characters:
# word[0] = "J"  # ← TypeError! Strings are immutable.
word = "J" + word[1:]       # Creates a NEW string "Jello"
print(word)


# ============================================================
# TYPE 4: BOOLEAN (bool) — TRUE OR FALSE
# ============================================================

is_raining = True
has_license = False
can_vote = age >= 18        # Booleans are often the RESULT of comparisons

print(type(is_raining))     # <class 'bool'>

# Booleans are actually INTEGERS in disguise!
# True = 1, False = 0
print(True + True)          # 2
print(True + False)         # 1
print(int(True))            # 1
print(int(False))           # 0
print(sum([True, False, True, True]))  # 3 (counting True values)

# BOOLEAN OPERATIONS
print(True and False)       # False  (BOTH must be True)
print(True or False)        # True   (at least ONE must be True)
print(not True)             # False  (reverses)
print(True and not False)   # True   (not binds tighter than and)

def expensive_function():
    """Placeholder for an expensive operation."""
    return True

# Short-circuit evaluation (important!)
# 'and' stops at the first False. 'or' stops at the first True.
result = False and expensive_function()  # expensive_function() never runs!
result = True or expensive_function()    # expensive_function() never runs!


# ============================================================
# TYPE 5: NONE (NoneType) — THE ABSENCE OF VALUE
# ============================================================

result = None
print(type(result))         # <class 'NoneType'>
print(result)               # None
print(result is None)       # True  (use 'is' to check for None, NEVER ==)

# None is used for:
# 1. Variables that haven't been assigned yet:
data = None
# ... later in the code ...
# data = load_data()  # Would assign real data

# 2. Functions that don't explicitly return anything:
def greet(name):
    print(f"Hello, {name}")

result = greet("Manav")     # Prints "Hello, Manav"
print(result)               # None (functions without 'return' return None)

# 3. Default parameter values:
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

# 4. Sentinels ("no result found"):
# user = find_user("nonexistent_id")
# if user is None:
#     print("User not found!")


'''
TRUTHY AND FALSY VALUES — THE COMPLETE GUIDE
=============================================
Python has a concept of "truthy" and "falsy" values.
Every value in Python can be evaluated as True or False in a boolean context.

FALSY VALUES (these evaluate to False):
    False        ← The boolean False
    0            ← The integer zero
    0.0          ← The float zero
    0j           ← Complex zero
    ""           ← Empty string
    []           ← Empty list
    {}           ← Empty dict
    ()           ← Empty tuple
    set()        ← Empty set
    None         ← The None value
    range(0)     ← Empty range

TRUTHY VALUES (everything else):
    True         ← The boolean True
    42           ← Non-zero number
    -1           ← Negative numbers (truthy!)
    "hello"      ← Non-empty string
    [0]          ← List with elements (even if elements are 0/False)
    {"a": 1}     ← Non-empty dict
    [False]      ← List containing False is still truthy (non-empty list)
'''

# --- USING TRUTHY/FALSY IN PRACTICE ---
name = ""
if name:                                # Empty string is falsy → skips
    print(f"Hello, {name}")
else:
    print("Name is empty!")             # ← This runs

numbers = [1, 2, 3]
if numbers:                             # Non-empty list is truthy → runs
    print(f"Found {len(numbers)} items")

# Common pattern: check if list is not empty
items = []
if items:                               # Falsy (empty list)
    pass  # process(items)
else:
    print("No items to process")

# Boolean conversion
print(bool(0))              # False
print(bool(42))             # True
print(bool(""))             # False
print(bool("hello"))        # True
print(bool([]))             # False
print(bool([0]))            # True (non-empty list, even though element is 0)


'''
PART 3: IMMUTABLE vs MUTABLE TYPES — THE MOST IMPORTANT DISTINCTION
=====================================================================

This is THE most important concept in Python data types.
Understanding this prevents 90% of Python bugs.

IMMUTABLE (cannot be changed after creation):
    int, float, str, bool, tuple, frozenset

MUTABLE (can be changed after creation):
    list, dict, set

WHY IT MATTERS: When you "modify" an immutable type, Python creates a
NEW object. When you modify a mutable type, Python changes the SAME object
in place. This has HUGE implications for how variables behave.
'''

# --- IMMUTABLE TYPE BEHAVIOR ---
a = 10
b = a        # b points to the SAME integer object 10
print(a, b)  # 10 10
a = 20       # a now points to a NEW object 20. b is UNAFFECTED.
print(a, b)  # 20 10  ← b still points to the original 10!

# VISUALIZATION:
#   Before: a ──> [10] <── b    (both point to same 10)
#   After:  a ──> [20]          (a points to new 20)
#           b ──> [10]          (b still points to original 10)

# With strings:
s1 = "hello"
s2 = s1
s1 = s1 + " world"   # Creates a NEW string "hello world"
print(s1)             # hello world
print(s2)             # hello ← unchanged!

# --- MUTABLE TYPE BEHAVIOR ---
list1 = [1, 2, 3]
list2 = list1         # list2 points to the SAME list object!
list1.append(4)       # Modify the list IN PLACE
print(list1)          # [1, 2, 3, 4]
print(list2)          # [1, 2, 3, 4] ← ALSO CHANGED!

# VISUALIZATION:
#   list1 ──> [1, 2, 3] <── list2   (both point to same list)
#   After append(4):
#   list1 ──> [1, 2, 3, 4] <── list2  (same list, modified in place)

# THIS IS THE #1 SOURCE OF PYTHON BUGS!
# If you don't want list2 to change when list1 changes, make a COPY:
list1 = [1, 2, 3]
list2 = list1.copy()   # Shallow copy — creates a NEW list with same elements
list1.append(4)
print(list1)            # [1, 2, 3, 4]
print(list2)            # [1, 2, 3] ← unchanged!

# --- THE FUNCTION ARGUMENT GOTCHA ---
def add_item(lst, item):
    """This function MODIFIES the original list (surprising to beginners!)"""
    lst.append(item)

my_list = [1, 2, 3]
add_item(my_list, 99)
print(my_list)          # [1, 2, 3, 99] ← The original list was modified!

# HOW TO AVOID: Pass a copy if you don't want the original modified
add_item(my_list.copy(), 100)
print(my_list)          # [1, 2, 3, 99] ← unchanged (we passed a copy)

# --- id() FUNCTION: SEEING MEMORY ADDRESSES ---
# id() returns the memory address of an object. Useful for debugging.
a = 10
b = 10
print(id(a) == id(b))   # True (Python caches small integers — same object!)

c = [1, 2]
d = [1, 2]
print(id(c) == id(d))   # False (two different list objects in memory!)

e = c
print(id(c) == id(e))   # True (same object — assignment copies reference)


'''
PART 4: TYPE CONVERSION (CASTING) — THE COMPLETE GUIDE
=======================================================

Sometimes you need to convert between types. Python provides built-in
functions for this.
'''

# --- STRING TO NUMBER ---
num_str = "42"
num_int = int(num_str)
print(num_int + 8)          # 50

price_str = "19.99"
price_float = float(price_str)
print(price_float)          # 19.99

# Invalid conversion raises ValueError:
# int("hello")    # ValueError!
# int("3.14")     # ValueError! (must use float() first, then int())

# --- NUMBER TO STRING ---
age = 25
age_str = str(age)
print("I am " + age_str + " years old")    # I am 25 years old

# With f-strings (cleaner — covered in Part 6):
print(f"I am {age} years old")             # I am 25 years old

# --- FLOAT TO INTEGER ---
print(int(3.9))             # 3   (truncates toward zero — NOT rounding!)
print(int(-3.9))            # -3  (truncates toward zero)

# If you want to ROUND:
print(round(3.9))           # 4   (rounds to nearest)
print(round(3.5))           # 4   (rounds to even on .5 — banker's rounding!)
print(round(2.5))           # 2   (rounds to even — 2, not 3!)

# --- INTEGER TO FLOAT ---
print(float(5))             # 5.0
print(float(0))             # 0.0

# --- ANYTHING TO BOOLEAN ---
print(bool(0))              # False
print(bool(42))             # True
print(bool(""))             # False  (empty string)
print(bool("hello"))        # True
print(bool([]))             # False  (empty list)
print(bool([1]))            # True
print(bool(None))           # False

# --- STRING TO LIST ---
print(list("hello"))        # ['h', 'e', 'l', 'l', 'o']

# --- LIST TO STRING ---
chars = ['h', 'e', 'l', 'l', 'o']
print("".join(chars))       # hello

# --- TUPLE AND LIST CONVERSION ---
my_list = [1, 2, 3]
my_tuple = tuple(my_list)
print(my_tuple)             # (1, 2, 3)
print(list(my_tuple))       # [1, 2, 3] (convert back)

# --- SET CONVERSION (removes duplicates!) ---
nums = [1, 2, 2, 3, 3, 3]
unique = list(set(nums))
print(unique)               # [1, 2, 3] (order not guaranteed!)


'''
PART 5: OPERATORS — THE COMPLETE REFERENCE
===========================================
'''

# --- ARITHMETIC OPERATORS ---
print("\n--- Arithmetic ---")
print(10 + 3)     # 13    Addition
print(10 - 3)     # 7     Subtraction
print(10 * 3)     # 30    Multiplication
print(10 / 3)     # 3.333 True division (always returns float)
print(10 // 3)    # 3     Floor division (drops decimal)
print(10 % 3)     # 1     Modulo (remainder)
print(2 ** 10)    # 1024  Exponent (2 to the power of 10)

# --- DIVMOD (quotient and remainder together) ---
q, r = divmod(17, 5)
print(f"17 ÷ 5 = {q} remainder {r}")   # 17 ÷ 5 = 3 remainder 2

# --- COMPARISON OPERATORS (return True or False) ---
print("\n--- Comparison ---")
print(5 == 5)     # True   Equal to (note: TWO equals signs)
print(5 != 3)     # True   Not equal to
print(5 > 3)      # True   Greater than
print(5 < 3)      # False  Less than
print(5 >= 5)     # True   Greater than or equal
print(5 <= 4)     # False  Less than or equal

# CHAINED COMPARISONS (Python exclusive feature!)
x = 5
print(1 < x < 10)     # True (same as 1 < x and x < 10)
print(1 < x < 3)      # False

# --- LOGICAL OPERATORS ---
print("\n--- Logical ---")
print(True and False)    # False (both must be True)
print(True and True)     # True
print(True or False)     # True  (at least one must be True)
print(False or False)    # False
print(not True)          # False (reverses)

# COMBINING LOGIC (use parentheses for clarity)
age = 25
has_license = True
can_drive = (age >= 18) and has_license
print(f"Can drive? {can_drive}")    # True

# --- IDENTITY OPERATORS ---
# 'is' checks if two variables point to the SAME OBJECT (same memory address)
# '==' checks if the VALUES are equal
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)     # True  (same values)
print(a is b)     # False (different objects in memory)

# Rule: use == for comparing VALUES. Use 'is' ONLY for None, True, False.
print(a is not None)    # True (proper way to check not-None)

# None comparison — ALWAYS use 'is', never '==':
result = None
if result is None:       # ✓ Correct
    pass
# if result == None:     # ✗ Works but bad style (PEP 8 violation)

# --- MEMBERSHIP OPERATORS ---
# 'in' checks if something exists inside a collection
print(3 in [1, 2, 3])          # True
print(5 in [1, 2, 3])          # False
print("a" in "apple")          # True
print("x" not in "apple")      # True
print("name" in {"name": "Manav"})  # True (checks dict keys)

# --- BITWISE OPERATORS (less common, but good to know) ---
print(5 & 3)      # 1   (AND: 101 & 011 = 001)
print(5 | 3)      # 7   (OR:  101 | 011 = 111)
print(5 ^ 3)      # 6   (XOR: 101 ^ 011 = 110)
print(~5)         # -6  (NOT: inverts all bits)
print(5 << 1)     # 10  (left shift: multiply by 2)
print(5 >> 1)     # 2   (right shift: divide by 2)


'''
PART 6: F-STRINGS — MODERN STRING FORMATTING (COMPLETE GUIDE)
==============================================================

f-strings (formatted string literals) are the Pythonic way to embed
variables and expressions inside strings. Available since Python 3.6.

WHY f-STRINGS ARE BEST:
    - Faster than .format() and % formatting
    - More readable (variables inline)
    - Support expressions, function calls, and formatting
'''

name = "Manav"
age = 25
height = 5.9
score = 95.6789

# --- BASIC USAGE ---
print(f"Hello, my name is {name}")              # Hello, my name is Manav
print(f"I am {age} years old")                  # I am 25 years old

# --- EXPRESSIONS INSIDE F-STRINGS ---
print(f"In 5 years, I'll be {age + 5}")         # In 5 years, I'll be 30
print(f"2 + 2 = {2 + 2}")                       # 2 + 2 = 4
print(f"Name length: {len(name)}")              # Name length: 5
print(f"{'hello'.upper()}")                     # HELLO

# --- NUMBER FORMATTING ---
print(f"Score: {score:.2f}")                   # Score: 95.68 (2 decimal places)
print(f"Score: {score:.0f}")                   # Score: 96 (0 decimals, rounded)
print(f"Score: {score:>+10.2f}")               # Score:     +95.68 (right-aligned, show sign)
print(f"Score: {score:<10.2f}")                # Score: 95.68     (left-aligned)
print(f"Score: {score:^10.2f}")                # Score:   95.68   (centered)

# --- THOUSANDS SEPARATOR ---
big_number = 1234567.89
print(f"Population: {big_number:,.2f}")         # Population: 1,234,567.89
print(f"Revenue: ${1234567:,}")                 # Revenue: $1,234,567

# --- PERCENTAGE ---
ratio = 0.875
print(f"Pass rate: {ratio:.1%}")               # Pass rate: 87.5%

# --- BINARY, HEX, OCTAL ---
print(f"Binary: {42:b}")                       # Binary: 101010
print(f"Binary: {42:#b}")                      # Binary: 0b101010 (with prefix)
print(f"Hex: {255:x}")                         # Hex: ff
print(f"Hex: {255:#x}")                        # Hex: 0xff
print(f"Octal: {64:o}")                        # Octal: 100

# --- DATE FORMATTING ---
from datetime import datetime
now = datetime.now()
print(f"Date: {now:%Y-%m-%d}")                 # Date: 2024-07-24
print(f"Time: {now:%H:%M:%S}")                 # Time: 10:30:45
print(f"Full: {now:%B %d, %Y at %I:%M %p}")    # Full: July 24, 2024 at 10:30 AM

# --- MULTI-LINE F-STRINGS ---
report = f"""
Student Report
==============
Name:   {name}
Age:    {age}
Height: {height:.1f} feet
Score:  {score:.1f}/100
Pass:   {'Yes' if score >= 60 else 'No'}
"""
print(report)

# --- F-STRING WITH DICTIONARY ---
person = {"name": "Alice", "age": 30, "city": "NYC"}
print(f"{person['name']} is {person['age']} from {person['city']}")

# --- F-STRING DEBUGGING (Python 3.8+) ---
x = 42
y = "hello"
print(f"{x=}")              # x=42 (shows variable name AND value!)
print(f"{x = }")            # x = 42 (with spaces)
print(f"{y.upper() = }")    # y.upper() = 'HELLO'


'''
PART 7: COMMON PITFALLS AND HOW TO AVOID THEM
=============================================

PITFALL 1: INTEGER DIVISION SURPRISES
'''
# / always returns float:
result = 10 / 2    # 5.0 (not 5!)
# If you need an int result, use //:
result = 10 // 2   # 5

'''
PITFALL 2: FLOATING POINT COMPARISON
'''
# Never compare floats with ==:
# print(0.1 + 0.2 == 0.3)  # False! (it's 0.30000000000000004)
# Use math.isclose() instead:
import math
print(math.isclose(0.1 + 0.2, 0.3, abs_tol=1e-9))   # True

'''
PITFALL 3: MODIFYING A LIST WHILE ITERATING
'''
# BAD: Removing items shifts indices
nums = [1, 2, 3, 4, 5]
# for i in range(len(nums)):
#     if nums[i] % 2 == 0:
#         del nums[i]  # IndexError! List shrinks during iteration.

# GOOD: Create a new filtered list
filtered = [x for x in nums if x % 2 != 0]

'''
PITFALL 4: MUTABLE DEFAULT ARGUMENTS
'''
# BAD: Default list is shared across all calls!
def add_item_bad(item, lst=[]):
    lst.append(item)
    return lst
# print(add_item_bad(1))  # [1]
# print(add_item_bad(2))  # [1, 2] — NOT [2]!

# GOOD: Use None as default
def add_item_good(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

'''
PITFALL 5: CONFUSING = AND ==
'''
# = is ASSIGNMENT (stores a value)
x = 5   # x now holds 5

# == is COMPARISON (checks equality)
if x == 5:   # True
    print("x is 5")

# Common typo in if statements:
# if x = 5:  # SyntaxError! (Python catches this, unlike C/Java)
# if x == 5: # Correct

'''
PITFALL 6: SHALLOW vs DEEP COPY
'''
import copy

original = [[1, 2], [3, 4]]

# Shallow copy (only copies the outer structure):
shallow = original[:]        # or: list(original) or original.copy()
shallow[0][0] = 99
print(original)              # [[99, 2], [3, 4]] — inner lists are shared!

# Deep copy (copies everything, recursively):
original2 = [[1, 2], [3, 4]]
deep = copy.deepcopy(original2)
deep[0][0] = 99
print(original2)             # [[1, 2], [3, 4]] — original is safe!

'''
PITFALL 7: is vs ==
'''
# For None, True, False: ALWAYS use 'is' (identity check)
if result is None:    # ✓
    pass

# For values: use == (equality check)
if score == 100:      # ✓
    pass

# For small integers (-5 to 256), Python caches them:
a = 100
b = 100
print(a is b)   # True (cached!)

# But for larger integers:
c = 1000
d = 1000
print(c is d)   # May be False! (not cached)
print(c == d)   # True (values are equal)
# LESSON: Always use == for value comparison. Use 'is' only for None/True/False.

# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 1 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Variables are labels pointing to objects. Python is dynamically typed.
2. Five primitive types: int, float, str, bool, None.
3. Integer division // drops decimals. True division / returns float.
4. Modulo % gives the remainder. Exponent ** raises to power.
5. Floating point is IMPRECISE. Use decimal module for money.
6. IMMUTABLE types (int, str): modifications create NEW objects.
   MUTABLE types (list, dict): modifications change the SAME object.
7. Truthy: non-zero, non-empty. Falsy: 0, "", [], {}, None, False.
8. Use == for value comparison. Use 'is' only for None/True/False.
9. f-strings: f"Hello {name}" — the cleanest way to format strings.
10. Beware: mutable default arguments, shallow copies, float comparison.

Next: Chapter 2 — Control Flow (if/else, loops, comprehensions)
""")
