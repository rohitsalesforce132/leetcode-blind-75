'''
CHAPTER 2: CONTROL FLOW — IF/ELSE, LOOPS & COMPREHENSIONS
==========================================================

"Your code needs to make DECISIONS and REPEAT actions.
Control flow is how you tell Python: 'Do this if X, otherwise do Y.
Do this 10 times. Do this for each item.' This chapter covers
all the ways to control how your code executes."

---

PART 1: CONDITIONALS (if / elif / else)
========================================

Real-world analogy: CHOOSING WHAT TO WEAR based on weather.

    IF it's raining → take umbrella
    ELSE IF it's sunny → wear sunglasses
    ELSE → wear a jacket

Python uses if / elif (else if) / else:

    if condition:
        # do something
    elif another_condition:
        # do something else
    else:
        # default action

IMPORTANT: Only the FIRST matching branch runs.
Once a condition is True, Python skips all remaining elif/else.
'''

# --- BASIC IF/ELSE ---
temperature = 30

if temperature > 35:
    print("It's scorching hot! 🔥")
elif temperature > 25:
    print("It's warm and nice. 😊")      # ← This runs (30 > 25)
elif temperature > 10:
    print("It's cool. 🧥")
else:
    print("It's cold! 🥶")

# --- COMPARISON OPERATORS IN CONDITIONS ---
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"                           # ← This runs
elif score >= 70:
    grade = "C"
else:
    grade = "F"
print(f"Grade: {grade}")

# --- NESTED CONDITIONALS ---
age = 25
has_license = True

if age >= 18:
    if has_license:
        print("You can drive! 🚗")
    else:
        print("You need a license first.")
else:
    print("You're too young to drive.")

# AVOID deep nesting — use early returns / guard clauses:
def check_access(age, has_id):
    """Guard clauses — check conditions top to bottom, exit early."""
    if age < 18:
        return "Too young"
    if not has_id:
        return "Need ID"
    return "Access granted"

print(check_access(25, True))   # Access granted

# --- CONDITIONAL EXPRESSION (TERNARY OPERATOR) ---
# One-line if/else for simple assignments
age = 20
status = "adult" if age >= 18 else "minor"
print(f"Status: {status}")                # adult

# Read as: "value_if_true if condition else value_if_false"

# Nested ternary (avoid — hard to read):
category = "child" if age < 13 else "teen" if age < 18 else "adult"
# Better written as if/elif/else for clarity.


'''
INDENTATION IS CRITICAL IN PYTHON!
    In other languages, you use { } to mark code blocks.
    In Python, you use INDENTATION (4 spaces).
    Everything indented under an 'if' belongs to that if.

    if True:
        print("Inside the if")       ← 4 spaces = inside if
        print("This too")            ← 4 spaces = inside if
    print("Outside the if")          ← 0 spaces = outside if

    Mixing tabs and spaces causes TabError. ALWAYS use 4 spaces.

    TIP: Configure your editor to insert 4 spaces when you press Tab.
'''


'''
PART 2: FOR LOOPS — ITERATING OVER COLLECTIONS
================================================

Real-world analogy: Going through each item in a shopping list.
    "For each item on my list: put it in the cart."

FOR LOOPS ARE THE MOST COMMON LOOP IN PYTHON.
You'll use them 100× more than while loops.
'''

# --- FOR LOOP OVER A LIST ---
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(f"I like {fruit}")
# Output:
# I like apple
# I like banana
# I like cherry

# --- FOR LOOP WITH RANGE ---
# range(n) → generates 0, 1, 2, ..., n-1
for i in range(5):
    print(f"Count: {i}", end=" ")
# Output: Count: 0 Count: 1 Count: 2 Count: 3 Count: 4
print()

# range(start, stop) → from start to stop-1
for i in range(2, 6):
    print(f"  From 2: {i}", end=" ")
# Output: From 2: 2 From 2: 3 From 2: 4 From 2: 5
print()

# range(start, stop, step)
for i in range(0, 10, 2):
    print(f"  Even: {i}", end=" ")
# Output: Even: 0 Even: 2 Even: 4 Even: 6 Even: 8
print()

# Counting backwards:
for i in range(5, 0, -1):
    print(f"  Countdown: {i}", end=" ")
# Output: Countdown: 5 Countdown: 4 Countdown: 3 Countdown: 2 Countdown: 1
print()

# --- FOR LOOP WITH ENUMERATE ---
# When you need BOTH the index AND the value:
colors = ["red", "green", "blue"]

for index, color in enumerate(colors):
    print(f"  Position {index}: {color}")
# Position 0: red
# Position 1: green
# Position 2: blue

# enumerate with custom start:
for i, color in enumerate(colors, start=1):
    print(f"  #{i}: {color}")

# --- FOR LOOP OVER A STRING ---
for char in "Hello":
    print(char, end=" ")
# H e l l o
print()

# --- FOR LOOP OVER A DICTIONARY ---
person = {"name": "Manav", "age": 25, "city": "Pune"}

# Iterate over key-value pairs (BEST practice):
for key, value in person.items():
    print(f"  {key} = {value}")

# Iterate over keys only:
for key in person:
    print(f"  Key: {key}")

# Iterate over values only:
for value in person.values():
    print(f"  Value: {value}")

# --- FOR LOOP OVER TWO LISTS WITH ZIP ---
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]

for name, score in zip(names, scores):
    print(f"  {name}: {score}")

# zip stops at the shortest list:
for a, b in zip([1, 2, 3], [10, 20]):
    print(f"  {a}, {b}")   # Only 2 pairs (shorter list has 2 items)

# --- NESTED FOR LOOPS ---
# A loop inside a loop. Used for 2D structures (grids, matrices).
print("\n--- Multiplication Table ---")
for i in range(1, 4):              # Outer loop: rows
    for j in range(1, 4):          # Inner loop: columns
        product = i * j
        print(f"  {i}×{j}={product}", end="  ")
    print()                        # New line after each row

# WARNING: Nested loops multiply. O(n²) time complexity.
# 3×3 = 9 iterations. 100×100 = 10,000. 1000×1000 = 1,000,000.


'''
PART 3: WHILE LOOPS — REPEAT UNTIL A CONDITION CHANGES
========================================================

Real-world analogy: "Keep eating WHILE there's food on the plate."

USE WHILE WHEN:
  - You don't know how many iterations you need
  - You're waiting for a condition to change
  - You're processing input until a sentinel value

USE FOR WHEN:
  - You know the number of iterations
  - You're iterating over a collection
'''

# --- BASIC WHILE LOOP ---
count = 5
while count > 0:
    print(f"  Countdown: {count}")
    count -= 1                # CRITICAL: must change the condition variable!
print("  🚀 Liftoff!")

# --- INFINITE LOOP (AND HOW TO BREAK IT) ---
# while True:
#     response = input("Enter 'quit' to stop: ")
#     if response == 'quit':
#         break

# --- WHILE WITH ELSE (Python special) ---
# The else block runs ONLY if the loop completed WITHOUT hitting break
for num in [1, 3, 5, 7]:
    if num == 4:
        print("Found 4!")
        break
else:
    print("4 not found in the list!")   # ← This runs (no break occurred)


'''
BREAK AND CONTINUE
------------------
    break    → EXIT the loop immediately (stop looping)
    continue → SKIP this iteration (jump to next item)

These work in BOTH for and while loops.
'''

# --- BREAK: Stop the loop early ---
numbers = [3, 7, 2, 8, 1, 9, 4]

for num in numbers:
    if num == 8:
        print(f"Found 8! Stopping search.")
        break
    print(f"  Checking {num}...")

# --- CONTINUE: Skip certain items ---
# Print only odd numbers from 0 to 9
for num in range(10):
    if num % 2 == 0:         # If even
        continue             # Skip to next iteration
    print(f"  Odd: {num}", end=" ")
# Output: Odd: 1 Odd: 3 Odd: 5 Odd: 7 Odd: 9
print()

# --- BREAK IN NESTED LOOPS ---
# break only exits the INNERMOST loop:
for i in range(3):
    for j in range(3):
        if i == 1 and j == 1:
            break            # Only breaks inner loop
        print(f"  ({i},{j})", end="")
    print()

# To break out of ALL nested loops, use a flag or exception:
found = False
for i in range(3):
    for j in range(3):
        if i == 1 and j == 1:
            found = True
            break           # Break inner
    if found:
        break               # Break outer


'''
PART 4: COMPREHENSIONS — PYTHON'S SUPERPOWER
=============================================

Comprehensions are a one-line way to create lists, sets, or dicts
from an existing collection. They are FASTER and more PYTHONIC than loops.

Think of it as: "Transform each item and collect the results."

ANATOMY OF A LIST COMPREHENSION:
    [ expression  for item in collection  if condition ]
       ↑              ↑                      ↑
    what to do    loop through it     (optional) filter

Read right-to-left: "For each item in collection, if condition is true,
                     apply expression and collect results"
'''

# --- LIST COMPREHENSION: BASIC ---
# Long way (traditional loop):
squares_old = []
for x in range(5):
    squares_old.append(x ** 2)
print(f"Squares (loop): {squares_old}")           # [0, 1, 4, 9, 16]

# Python way (list comprehension):
squares_new = [x ** 2 for x in range(5)]
print(f"Squares (comprehension): {squares_new}")  # [0, 1, 4, 9, 16]

# --- COMPREHENSION WITH FILTER (if condition) ---
# Get only even numbers, squared
evens_squared = [x ** 2 for x in range(10) if x % 2 == 0]
print(f"Even squares: {evens_squared}")            # [0, 4, 16, 36, 64]

# --- COMPREHENSION WITH IF/ELSE (transform) ---
# Label numbers as even or odd
labels = ["even" if x % 2 == 0 else "odd" for x in range(5)]
print(f"Labels: {labels}")                         # ['even', 'odd', 'even', 'odd', 'even']

# NOTE: if/else goes BEFORE the for (it's the expression).
#       Plain if goes AFTER the for (it's a filter).
#       Don't confuse these two positions!

# --- COMPREHENSION WITH FUNCTION CALLS ---
words = ["hello", "world", "python"]
lengths = [len(word) for word in words]
print(f"Lengths: {lengths}")                       # [5, 5, 6]

upper_words = [word.upper() for word in words]
print(f"Uppercase: {upper_words}")                 # ['HELLO', 'WORLD', 'PYTHON']

# --- NESTED COMPREHENSION (2D grid) ---
matrix = [[0 for _ in range(3)] for _ in range(3)]
print(f"3×3 matrix: {matrix}")
# [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

# Flatten a 2D list:
nested = [[1, 2], [3, 4], [5, 6]]
flat = [num for row in nested for num in row]
print(f"Flattened: {flat}")                        # [1, 2, 3, 4, 5, 6]

# --- SET COMPREHENSION ---
# Removes duplicates automatically
words = ["hi", "ok", "hey", "no", "hi"]
unique_lengths = {len(word) for word in words}
print(f"Unique word lengths: {unique_lengths}")    # {2, 3}

# --- DICTIONARY COMPREHENSION ---
names = ["Alice", "Bob", "Charlie"]
ages = [30, 25, 35]

# Create dict from two lists using zip:
age_dict = {name: age for name, age in zip(names, ages)}
print(f"Name→age: {age_dict}")                     # {'Alice': 30, 'Bob': 25, 'Charlie': 35}

# Reverse a dictionary:
reversed_dict = {v: k for k, v in age_dict.items()}
print(f"Age→name: {reversed_dict}")                # {30: 'Alice', 25: 'Bob', 35: 'Charlie'}

# Filter items in a dict:
long_names = {k: v for k, v in age_dict.items() if len(k) > 3}
print(f"Long names: {long_names}")                 # {'Alice': 30, 'Charlie': 35}

# --- COMPREHENSION vs LOOP: WHEN TO USE WHICH ---
# Use comprehension when:
#   - Simple transformation (one expression)
#   - Filtering with one condition
#   - Creating a new list/set/dict
#
# Use a regular loop when:
#   - Multiple statements per iteration
#   - Complex logic (nested if/else, try/except)
#   - Side effects (printing, modifying external state)
#   - The comprehension would be hard to read


'''
PART 5: ANY() AND ALL() — BOOLEAN AGGREGATION
==============================================

any() returns True if AT LEAST ONE element is truthy.
all() returns True if ALL elements are truthy.

These are shortcuts for common loop patterns.
'''

scores = [85, 92, 78, 65, 88]

# ANY: "Did anyone score above 90?"
print(any(score > 90 for score in scores))    # True (92 > 90)

# ALL: "Did everyone pass (score >= 60)?"
print(all(score >= 60 for score in scores))   # True

# Without any()/all():
has_high_score = False
for score in scores:
    if score > 90:
        has_high_score = True
        break

# EMPTY COLLECTIONS (edge cases):
print(any([]))     # False (nothing is True in an empty list)
print(all([]))     # True! (vacuously true — "all zero elements pass")
print(all([True, True, True]))   # True
print(all([True, False, True]))  # False


'''
PART 6: THE PASS STATEMENT
===========================

'pass' is a placeholder that does NOTHING.
Use it when Python requires a statement but you have nothing to write yet.
'''

# As a placeholder during development:
def calculate_tax(income):
    pass  # TODO: implement this later

class User:
    pass  # Empty class for now

# In an if block where you intentionally do nothing:
for num in range(10):
    if num % 2 == 0:
        pass  # Even numbers — intentionally skip
    else:
        print(f"  Odd: {num}")


'''
PART 7: COMMON MISTAKES
========================
'''

# --- MISTAKE 1: FORGETTING TO UPDATE THE WHILE CONDITION ---
# count = 5
# while count > 0:
#     print(count)
#     # Forgot count -= 1 → INFINITE LOOP!

# --- MISTAKE 2: MODIFYING A LIST WHILE ITERATING ---
# BAD: Removing items while iterating skips elements
# nums = [1, 2, 3, 4, 5]
# for i in range(len(nums)):
#     if nums[i] % 2 == 0:
#         nums.pop(i)  # BUG! After removing, indices shift.

# GOOD: Iterate over a COPY or use list comprehension:
nums = [1, 2, 3, 4, 5]
filtered = [x for x in nums if x % 2 != 0]

# --- MISTAKE 3: CONFUSING = AND == IN CONDITIONS ---
# if x = 5:   # SyntaxError in Python (unlike C/Java)
# if x == 5:  # Correct

# --- MISTAKE 4: OFF-BY-ONE ERRORS WITH RANGE ---
# range(5) generates 0,1,2,3,4 (FIVE numbers, NOT 0-5)
# range(1, 5) generates 1,2,3,4 (NOT including 5)
# range(0, 10, 2) generates 0,2,4,6,8 (NOT including 10)

# --- MISTAKE 5: CONFUSING 'is' AND '==' ---
a = [1, 2]
b = [1, 2]
# if a is b:   # False! Different objects
# if a == b:   # True! Same values


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 2 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. if/elif/else: decisions. Only first matching branch runs.
2. Guard clauses (early return) are cleaner than deep nesting.
3. for loop: iterate over collections (lists, strings, dicts, range).
4. while loop: repeat while condition is True. MUST update condition!
5. break: exit loop. continue: skip iteration.
6. enumerate(): get both index and value.
7. zip(): iterate over two lists simultaneously.
8. Comprehensions: [expr for x in items if cond] — one-line transform.
9. any()/all(): boolean aggregation over collections.
10. Don't modify lists while iterating — use comprehensions instead.

Next: Chapter 3 — Functions, Scope & Lambda
""")
