'''
CHAPTER 2: CONTROL FLOW — IF/ELSE, LOOPS & COMPREHENSIONS
==========================================================

"Your code needs to make DECISIONS and REPEAT actions.
Control flow is how you tell Python: 'Do this if X, otherwise do Y.
Do this 10 times. Do this for each item.'"

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

# IMPORTANT: Only the FIRST matching branch runs.
# Once a condition is True, Python skips all remaining elif/else.

# --- NESTED CONDITIONALS ---
score = 85
if score >= 60:
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"                       # ← This runs
    else:
        grade = "C"
    print(f"You passed with grade {grade}!")
else:
    print("You failed.")


# --- CONDITIONAL EXPRESSION (TERNARY OPERATOR) ---
# One-line if/else for simple assignments
age = 20
status = "adult" if age >= 18 else "minor"
print(f"Status: {status}")                # adult

# Read as: "value_if_true if condition else value_if_false"


'''
INDENTATION IS CRITICAL IN PYTHON!
    In other languages, you use { } to mark code blocks.
    In Python, you use INDENTATION (4 spaces).
    Everything indented under an 'if' belongs to that if.

    if True:
        print("This is inside the if")      ← 4 spaces = inside if
        print("This too")                   ← 4 spaces = inside if
    print("This is OUTSIDE the if")         ← 0 spaces = outside if

    Mixing tabs and spaces causes errors. Always use 4 spaces.

---

PART 2: LOOPS — REPEATING ACTIONS
===================================

There are two types of loops in Python: FOR and WHILE.


LOOP 1: FOR LOOP — "FOR each item in a collection"
---------------------------------------------------
Real-world analogy: Going through each item in a shopping list.
    "For each item on my list: put it in the cart."
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
    print(f"Count: {i}")
# Output: 0, 1, 2, 3, 4

# range(start, stop) → from start to stop-1
for i in range(2, 6):
    print(f"  From 2: {i}")
# Output: 2, 3, 4, 5

# range(start, stop, step)
for i in range(0, 10, 2):
    print(f"    Even: {i}")
# Output: 0, 2, 4, 6, 8

# --- FOR LOOP WITH ENUMERATE ---
# When you need BOTH the index AND the value:
colors = ["red", "green", "blue"]

for index, color in enumerate(colors):
    print(f"  Position {index}: {color}")
# Position 0: red
# Position 1: green
# Position 2: blue

# --- FOR LOOP OVER A STRING ---
for char in "Hello":
    print(char, end=" ")
# H e l l o
print()

# --- FOR LOOP OVER A DICTIONARY ---
person = {"name": "Manav", "age": 25, "city": "Pune"}

# Iterate over keys
for key in person:
    print(f"  {key}: {person[key]}")

# Iterate over key-value pairs (better)
for key, value in person.items():
    print(f"  {key} = {value}")


# --- LOOP 2: WHILE LOOP — "WHILE this condition is True, keep going" ---
# Real-world analogy: "Keep eating WHILE there's food on the plate."

count = 5
while count > 0:
    print(f"  Countdown: {count}")
    count -= 1                # CRITICAL: change the condition variable!
print("  🚀 Liftoff!")

# WARNING: If you forget to change the condition variable,
# the loop runs FOREVER (infinite loop). Always ensure the loop progresses.


'''
BREAK AND CONTINUE
------------------
Sometimes you need to exit a loop early or skip an iteration.

    break    → EXIT the loop immediately (stop looping)
    continue → SKIP this iteration (jump to next item)
'''

# --- BREAK: Stop the loop when you find what you need ---
numbers = [3, 7, 2, 8, 1, 9, 4]

for num in numbers:
    if num == 8:
        print(f"Found 8 at index {numbers.index(num)}!")
        break                    # Stop searching — we found it
    print(f"  Checking {num}...")

# --- CONTINUE: Skip certain items ---
# Print only odd numbers
for num in range(10):
    if num % 2 == 0:             # If even
        continue                 # Skip to next iteration
    print(f"  Odd: {num}")
# Output: 1, 3, 5, 7, 9


# --- NESTED LOOPS ---
# A loop inside a loop. Useful for 2D structures (grids, matrices).
print("\n--- Multiplication Table ---")
for i in range(1, 4):            # Outer loop: rows
    for j in range(1, 4):        # Inner loop: columns
        product = i * j
        print(f"  {i}×{j}={product}", end="  ")
    print()                      # New line after each row

# WARNING: Nested loops multiply. 3×3 = 9 iterations. 100×100 = 10,000.
# This is why nested loops are O(n²) — see Big-O chapter!


'''
LOOP ELSE CLAUSE (Python special)
----------------------------------
Python has a unique feature: for/while loops can have an 'else' that runs
ONLY if the loop completed WITHOUT hitting a break.
'''

# Example: Search for an item. If not found, print a message.
for num in [1, 3, 5, 7]:
    if num == 4:
        print("Found 4!")
        break
else:
    print("4 not found in the list!")   # This runs (no break occurred)


'''
PART 3: COMPREHENSIONS — PYTHON'S SUPERPOWER
=============================================

Comprehensions are a one-line way to create lists, sets, or dicts
from an existing collection. They are FASTER and more readable than loops.

Think of it as: "Transform each item and collect the results."
'''

# --- LIST COMPREHENSION ---
# Long way (traditional loop):
squares_old = []
for x in range(5):
    squares_old.append(x ** 2)
print(f"\nSquares (loop): {squares_old}")       # [0, 1, 4, 9, 16]

# Python way (list comprehension):
squares_new = [x ** 2 for x in range(5)]
print(f"Squares (comprehension): {squares_new}")  # [0, 1, 4, 9, 16]

# ANATOMY OF A COMPREHENSION:
#
#   [ expression  for item in collection  if condition ]
#      ↑              ↑                      ↑
#   what to do    loop through it     (optional) filter
#
# Read as: "For each item in collection, if condition is true,
#           apply expression and collect results"

# --- COMPREHENSION WITH CONDITION (FILTER) ---
# Get only even numbers, squared
evens_squared = [x ** 2 for x in range(10) if x % 2 == 0]
print(f"Even squares: {evens_squared}")          # [0, 4, 16, 36, 64]

# --- COMPREHENSION WITH IF/ELSE ---
# Label numbers as even or odd
labels = ["even" if x % 2 == 0 else "odd" for x in range(5)]
print(f"Labels: {labels}")                       # ['even', 'odd', 'even', 'odd', 'even']

# --- NESTED COMPREHENSION (2D grid) ---
matrix = [[0 for _ in range(3)] for _ in range(3)]
print(f"3×3 matrix: {matrix}")
# [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

# --- SET COMPREHENSION ---
# Remove duplicates while transforming
unique_lengths = {len(word) for word in ["hi", "ok", "hey", "no"]}
print(f"Unique word lengths: {unique_lengths}")  # {2, 3}

# --- DICTIONARY COMPREHENSION ---
# Create a dict from two lists
names = ["Alice", "Bob", "Charlie"]
ages = [30, 25, 35]
age_dict = {name: age for name, age in zip(names, ages)}
print(f"Name→age: {age_dict}")                   # {'Alice': 30, 'Bob': 25, 'Charlie': 35}


'''
COMPREHENSIONS SUMMARY:
    [expr for x in items]                    → basic
    [expr for x in items if cond]            → filter
    ["a" if cond else "b" for x in items]    → if/else transform
    {expr for x in items}                    → set
    {key: val for ...}                       → dict

    Read right-to-left: "for x in items, if cond, compute expr"
'''

# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 2 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. if/elif/else: decisions. Only first matching branch runs.
2. Indentation (4 spaces) defines code blocks — no curly braces.
3. for loop: iterate over collections (lists, strings, dicts, range).
4. while loop: repeat while condition is True. Must update condition!
5. break: exit loop. continue: skip iteration.
6. enumerate(): get both index and value.
7. Comprehensions: [expr for x in items if cond] — one-line transform+filter.
8. Nested loops are O(n²). Be careful with large inputs.

Next: Chapter 3 — Functions, Scope & Lambda
""")
