'''
CHAPTER 4: DATA STRUCTURES DEEP DIVE
=====================================

"Python has 4 built-in data structures that solve 90% of problems.
Master these and you can solve almost anything."

---

THE FOUR PILLARS:
    1. LIST  → ordered, mutable, allows duplicates
    2. DICT  → key-value pairs, fast lookup
    3. SET   → unordered, unique elements only
    4. TUPLE → ordered, IMMUTABLE (cannot change)

┌─────────────────────────────────────────────────────────────────┐
│           COMPARISON TABLE                                       │
├──────────┬──────────┬──────────┬──────────┬─────────────────────┤
│ Feature  │ List     │ Dict     │ Set      │ Tuple               │
├──────────┼──────────┼──────────┼──────────┼─────────────────────┤
│ Ordered? │ Yes      │ Yes (3.7)│ No       │ Yes                 │
│ Mutable? │ Yes      │ Yes      │ Yes      │ NO (immutable)      │
│ Dups OK? │ Yes      │ No (key) │ No       │ Yes                 │
│ Syntax   │ [1, 2]   │ {k: v}   │ {1, 2}   │ (1, 2)              │
│ Lookup   │ O(n)     │ O(1)     │ O(1)     │ O(n)                │
│ Use when │ Sequence │ Mapping  │ Unique   │ Fixed/immutable     │
└──────────┴──────────┴──────────┴──────────┴─────────────────────┘
'''

# ============================================================
# PART 1: LISTS — THE WORKHORSE
# ============================================================

# --- CREATION ---
empty = []
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]           # Can mix types (but don't usually)
nested = [[1, 2], [3, 4], [5, 6]]          # List of lists (2D grid)

# --- ADDING ELEMENTS ---
fruits = ["apple", "banana"]

fruits.append("cherry")                     # Add to END → O(1)
print(fruits)                               # ['apple', 'banana', 'cherry']

fruits.insert(0, "avocado")                 # Insert at INDEX → O(n)
print(fruits)                               # ['avocado', 'apple', 'banana', 'cherry']

fruits.extend(["date", "elderberry"])       # Add all from another list → O(k)
print(fruits)

# --- REMOVING ELEMENTS ---
fruits.remove("banana")                     # Remove by VALUE → O(n)
print(fruits)

popped = fruits.pop()                       # Remove from END → O(1)
print(f"Popped: {popped}, List: {fruits}")

popped_front = fruits.pop(0)                # Remove at INDEX → O(n)
print(f"Popped front: {popped_front}, List: {fruits}")

# --- ACCESSING & SLICING ---
nums = [10, 20, 30, 40, 50, 60, 70]

print(nums[0])           # 10   First element
print(nums[-1])          # 70   Last element
print(nums[1:4])         # [20, 30, 40]   Slice from index 1 to 3
print(nums[:3])          # [10, 20, 30]   First 3 elements
print(nums[-3:])         # [50, 60, 70]   Last 3 elements
print(nums[::2])         # [10, 30, 50, 70]  Every 2nd element
print(nums[::-1])        # [70, 60, 50, 40, 30, 20, 10]  REVERSE

# --- SEARCHING ---
print(30 in nums)        # True   Check if exists → O(n)
print(nums.index(30))    # 2      Find index of value → O(n)
print(nums.count(30))    # 1      Count occurrences → O(n)

# --- SORTING ---
# .sort() sorts IN-PLACE (modifies original). Returns None.
nums2 = [3, 1, 4, 1, 5, 9, 2, 6]
nums2.sort()                             # Ascending
print(f"Sorted ascending: {nums2}")

nums2.sort(reverse=True)                 # Descending
print(f"Sorted descending: {nums2}")

# sorted() returns a NEW list (original unchanged)
original = [3, 1, 4, 1, 5]
new_sorted = sorted(original)
print(f"Original: {original}, Sorted: {new_sorted}")

# --- USEFUL LIST METHODS ---
# reverse(), copy(), clear(), min(), max(), sum()
data = [5, 2, 8, 1, 9]
print(f"Min: {min(data)}, Max: {max(data)}, Sum: {sum(data)}")
print(f"Length: {len(data)}")


# ============================================================
# PART 2: DICTIONARIES — THE POWERHOUSE
# ============================================================

# --- CREATION ---
empty_dict = {}
person = {"name": "Manav", "age": 25, "city": "Pune"}
person2 = dict(name="Alice", age=30)      # Alternative constructor

# --- ACCESSING ---
print(person["name"])                     # Manav → O(1) lookup!
# print(person["email"])                  # ✗ KeyError if key doesn't exist

# Safe access with .get():
print(person.get("email"))                # None (no error)
print(person.get("email", "Not found"))   # "Not found" (default value)

# --- ADD/UPDATE ---
person["email"] = "manav@example.com"     # Add new key → O(1)
person["age"] = 26                        # Update existing → O(1)
print(person)

# --- DELETE ---
del person["city"]                        # Delete by key → O(1)
person.pop("email")                       # Delete and return value → O(1)
print(person)

# --- ITERATING ---
capitals = {"India": "New Delhi", "France": "Paris", "Japan": "Tokyo"}

# Keys only
for country in capitals:
    print(f"  {country}")

# Key-value pairs
for country, capital in capitals.items():
    print(f"  Capital of {country} is {capital}")

# Values only
for capital in capitals.values():
    print(f"  City: {capital}")

# --- CHECK IF KEY EXISTS ---
print("India" in capitals)                # True → O(1)
print("USA" in capitals)                  # False

# --- USEFUL DICT METHODS ---
print(capitals.keys())                    # dict_keys(['India', 'France', 'Japan'])
print(capitals.values())                  # dict_values(['New Delhi', 'Paris', 'Tokyo'])
print(capitals.items())                   # dict_items([('India', 'New Delhi'), ...])

# --- DEFAULTDICT (auto-creates missing keys) ---
from collections import defaultdict

# Problem: counting word frequencies
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]

# Old way (must check if key exists):
count_old = {}
for word in words:
    if word in count_old:
        count_old[word] += 1
    else:
        count_old[word] = 1
print(f"Count (old way): {count_old}")

# defaultdict way (auto-initializes missing keys to 0):
count_new = defaultdict(int)              # int() → 0
for word in words:
    count_new[word] += 1                  # No need to check!
print(f"Count (defaultdict): {dict(count_new)}")

# --- COUNTER (frequency counting in one line) ---
from collections import Counter
word_counts = Counter(words)
print(f"Counter: {word_counts}")          # Counter({'apple': 3, 'banana': 2, 'cherry': 1})
print(f"Top 2: {word_counts.most_common(2)}")  # [('apple', 3), ('banana', 2)]


# ============================================================
# PART 3: SETS — THE DEDUPLICATOR
# ============================================================

# A set is like a mathematical set: unique elements only, no order.

# --- CREATION ---
empty_set = set()                         # NOT {} (that's a dict!)
fruits_set = {"apple", "banana", "cherry"}
from_list = set([1, 2, 2, 3, 3, 3])      # Removes duplicates!
print(f"From list with dups: {from_list}")  # {1, 2, 3}

# --- ADD/REMOVE ---
fruits_set.add("date")                    # Add → O(1)
fruits_set.discard("banana")              # Remove (no error if missing)
print(fruits_set)

# --- SET OPERATIONS (like math class!) ---
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7, 8}

print(f"Union: {A | B}")                  # {1, 2, 3, 4, 5, 6, 7, 8}
print(f"Intersection: {A & B}")           # {4, 5}
print(f"Difference: {A - B}")             # {1, 2, 3}
print(f"Symmetric diff: {A ^ B}")         # {1, 2, 3, 6, 7, 8} (in one but not both)

# --- WHEN TO USE A SET ---
# 1. Remove duplicates from a list
names = ["Alice", "Bob", "Alice", "Charlie", "Bob"]
unique = list(set(names))
print(f"Unique: {unique}")

# 2. Fast membership test (O(1) vs list's O(n))
big_list = list(range(1000000))
big_set = set(big_list)

import time
start = time.time()
_ = 999999 in big_list                    # O(n) — slow
print(f"List lookup: {time.time() - start:.6f}s")

start = time.time()
_ = 999999 in big_set                     # O(1) — instant!
print(f"Set lookup:  {time.time() - start:.6f}s")


# ============================================================
# PART 4: TUPLES — THE IMMUTABLE LIST
# ============================================================

# A tuple is like a list but CANNOT BE CHANGED after creation.
# Use for: coordinates, fixed configurations, return multiple values.

# --- CREATION ---
point = (3, 5)                            # 2D coordinate
rgb = (255, 128, 0)                       # Color values
single = (42,)                            # Single-element tuple (NOTE the comma!)
not_tuple = (42)                          # Just integer 42 (no comma = not a tuple!)

print(type(point))                        # <class 'tuple'>
print(type(single))                       # <class 'tuple'>
print(type(not_tuple))                    # <class 'int'>

# --- ACCESSING (same as list) ---
print(point[0])                           # 3
print(rgb[-1])                            # 0

# --- IMMUTABILITY ---
# point[0] = 10                           # ✗ ERROR! Cannot modify a tuple

# --- TUPLE UNPACKING ---
# Assign tuple elements to separate variables
x, y = point
print(f"x={x}, y={y}")                    # x=3, y=5

# Swap variables (this works because Python creates a tuple!)
a, b = 10, 20
a, b = b, a

# --- WHY USE TUPLES INSTEAD OF LISTS? ---
# 1. Safety: can't be accidentally modified
# 2. Can be used as DICT KEYS (lists cannot!)
locations = {(40.7, -74.0): "New York", (34.0, -118.2): "Los Angeles"}
print(locations[(40.7, -74.0)])           # New York

# 3. Slightly faster and less memory than lists
# 4. Signal intent: "this data shouldn't change"


# ============================================================
# PART 5: DEQUE — FAST QUEUE
# ============================================================

from collections import deque

# A deque (double-ended queue) is like a list but O(1) for both ends.
# Use when you need to add/remove from BOTH front and back frequently.

# LIST:  append()=O(1), pop()=O(1), but insert(0)=O(n), pop(0)=O(n)
# DEQUE: append()=O(1), pop()=O(1), appendleft()=O(1), popleft()=O(1)

dq = deque([1, 2, 3])
dq.append(4)                              # Add to right → [1, 2, 3, 4]
dq.appendleft(0)                          # Add to left → [0, 1, 2, 3, 4]
print(f"Deque: {dq}")

dq.pop()                                  # Remove from right → [0, 1, 2, 3]
dq.popleft()                              # Remove from left → [1, 2, 3]
print(f"After pops: {dq}")

# For BFS / queue usage: always use deque, not list!
queue = deque()
queue.append("task1")
queue.append("task2")
while queue:
    task = queue.popleft()                # FIFO — first in, first out
    print(f"  Processing: {task}")


# ============================================================
# PART 6: PRACTICAL PATTERNS
# ============================================================

# --- ZIP: Combine two lists element-by-element ---
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]

for name, score in zip(names, scores):
    print(f"  {name}: {score}")

# Create a dict from two lists:
score_dict = dict(zip(names, scores))
print(f"Score dict: {score_dict}")

# --- UNPACKING WITH * ---
first, *rest = [1, 2, 3, 4, 5]
print(f"First: {first}, Rest: {rest}")    # First: 1, Rest: [2, 3, 4, 5]

*init, last = [1, 2, 3, 4, 5]
print(f"Init: {init}, Last: {last}")      # Init: [1, 2, 3, 4], Last: 5

# --- ANY() AND ALL() ---
print(any([False, False, True]))          # True (at least one is True)
print(all([True, True, False]))           # False (not all are True)
print(any([]))                            # False (empty = nothing True)
print(all([]))                            # True (vacuously true — edge case!)


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 4 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. List: ordered, mutable. append/pop=O(1). insert/pop(0)=O(n).
2. Dict: key→value. O(1) lookup. Use defaultdict/Counter for counting.
3. Set: unique elements. O(1) membership test. Union/intersection/diff.
4. Tuple: immutable list. Use for coordinates, dict keys, unpacking.
5. Deque: O(1) at both ends. Use for queues/BFS.
6. Patterns: zip(), enumerate(), unpacking with *, any()/all().

Next: Chapter 5 — Strings Deep Guide
""")
