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

UNDER THE HOOD (CPython):
    List  → resizable array of PyObject* pointers (over-allocates)
    Dict  → open-addressed hash table (sparse index array + entries)
    Set   → hash table (same machinery as dict, values only, no values)
    Tuple → fixed-size array of PyObject* pointers (no over-alloc)

┌─────────────────────────────────────────────────────────────┐
│  MEMORY FOOTPRINT (64-bit CPython, per element, approx)      │
├──────────────┬──────────────────────────────────────────────┤
│ List[int]    │  8 bytes pointer + ~12.5% over-allocation     │
│ Tuple[int]   │  8 bytes pointer (no over-allocation)         │
│ Dict entry   │ 24 bytes (hash + key ptr + value ptr)         │
│ Set entry    │  8 bytes (hash + key ptr, packed)             │
└──────────────┴──────────────────────────────────────────────┘
'''

# ============================================================
# PART 1: LISTS — THE WORKHORSE
# ============================================================
#
# INTERNAL IMPLEMENTATION (CPython):
# A list is a DYNAMIC ARRAY of pointers to PyObject.
#
#   ob_item (pointer to array of PyObject*)       ob_size   allocated
#   ┌─────────────────────────────────┐           ┌──────┐  ┌──────┐
#   │ [ptr0][ptr1][ptr2][..][garbage] │           │  3   │  │  10  │
#   └────┬────┬────┬─────────────────┘           └──────┘  └──────┘
#        │    │    │
#        ▼    ▼    ▼
#       10   20   30        ← the actual integer objects (on the heap)
#
# Key facts:
#   * ob_size   = number of elements you can see (len(list))
#   * allocated = capacity of the underlying C array (>= ob_size)
#   * Over-allocation growth pattern (CPython listobject.c):
#
#       new_allocated = (size >> 3) + (size < 9 ? 3 : 6) + size
#
#     So as the list grows, CPython allocates extra slots to make
#     amortized append() O(1) instead of reallocating every time.
#
#   growth sequence: 0 -> 4 -> 8 -> 16 -> 25 -> 35 -> 46 -> 58 -> 72 ...
#
# WHY append() is O(1) AMORTIZED:
#   Most appends just write into an existing empty slot -> O(1).
#   Only when the array is FULL does Python realloc + copy -> O(n),
#   but that happens rarely (geometric growth), so averaged over
#   many appends it's O(1) per append.

# --- CREATION ---
empty = []
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]           # Can mix types (but don't usually)
nested = [[1, 2], [3, 4], [5, 6]]          # List of lists (2D grid)

# Memory: each list above stores POINTERS; the objects live elsewhere.
# `mixed` has 4 pointers -> 32 bytes on 64-bit, regardless of object sizes.

# --- ADDING ELEMENTS ---
fruits = ["apple", "banana"]

fruits.append("cherry")                     # Add to END -> O(1) amortized
print(fruits)                               # ['apple', 'banana', 'cherry']

fruits.insert(0, "avocado")                 # Insert at INDEX -> O(n)
# Why O(n)? Python must SHIFT every element after index 0 one slot right:
#   Before: [apple][banana][cherry]
#   Step 1: [apple][banana][cherry][..]  (shift cherry right)
#   Step 2: [apple][banana][banana][..]  (shift banana right)
#   Step 3: [apple][apple][banana][..]   (shift apple right)
#   Step 4: [avocado][apple][banana][cherry]
print(fruits)                               # ['avocado', 'apple', 'banana', 'cherry']

fruits.extend(["date", "elderberry"])       # Add all from another list -> O(k)
print(fruits)

# --- REMOVING ELEMENTS ---
fruits.remove("banana")                     # Remove by VALUE -> O(n)
# Must scan to find it (O(n)) then shift remaining left (O(n)).
print(fruits)

popped = fruits.pop()                       # Remove from END -> O(1)
print(f"Popped: {popped}, List: {fruits}")

popped_front = fruits.pop(0)                # Remove at INDEX -> O(n)
# All elements after index 0 must shift LEFT by one.
print(f"Popped front: {popped_front}, List: {fruits}")

# --- ACCESSING & SLICING ---
nums = [10, 20, 30, 40, 50, 60, 70]

print(nums[0])           # 10   First element     -> O(1) pointer arithmetic
print(nums[-1])          # 70   Last element       -> O(1)
print(nums[1:4])         # [20, 30, 40]   Slice from index 1 to 3  -> O(k) copy
print(nums[:3])          # [10, 20, 30]   First 3 elements
print(nums[-3:])         # [50, 60, 70]   Last 3 elements
print(nums[::2])         # [10, 30, 50, 70]  Every 2nd element
print(nums[::-1])        # [70, 60, 50, 40, 30, 20, 10]  REVERSE

# SLICE SYNTAX:  list[start:stop:step]
#   * start inclusive, stop EXCLUSIVE, step can be negative
#   * Any omitted value uses a sensible default
#   * Slicing ALWAYS returns a NEW list (shallow copy)

# --- SEARCHING ---
print(30 in nums)        # True   Check if exists -> O(n) linear scan
print(nums.index(30))    # 2      Find index of value -> O(n)
print(nums.count(30))    # 1      Count occurrences -> O(n)

# --- SORTING ---
# .sort() sorts IN-PLACE (modifies original). Returns None.
# Uses Timsort: a hybrid merge/insertion sort. Worst case O(n log n).
nums2 = [3, 1, 4, 1, 5, 9, 2, 6]
nums2.sort()                             # Ascending
print(f"Sorted ascending: {nums2}")

nums2.sort(reverse=True)                 # Descending
print(f"Sorted descending: {nums2}")

# sorted() returns a NEW list (original unchanged)
original = [3, 1, 4, 1, 5]
new_sorted = sorted(original)
print(f"Original: {original}, Sorted: {new_sorted}")

# Sort with a KEY function (very common in interviews):
people = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
people.sort(key=lambda p: p[1])          # Sort by age (2nd element)
print(f"Sorted by age: {people}")

# --- USEFUL LIST METHODS ---
# reverse(), copy(), clear(), min(), max(), sum()
data = [5, 2, 8, 1, 9]
print(f"Min: {min(data)}, Max: {max(data)}, Sum: {sum(data)}")
print(f"Length: {len(data)}")

# --- LIST COMPREHENSIONS (fast, pythonic creation) ---
squares = [x * x for x in range(6)]       # [0, 1, 4, 9, 16, 25]
evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]
print(f"Squares: {squares}")
print(f"Evens: {evens}")
# Comprehensions are ~2x faster than a for-loop with .append() because
# the loop body runs in C and Python pre-sizes the result list.

# ============================================================
# LIST PERFORMANCE TABLE
# ============================================================
# ┌──────────────────────┬──────────────┬───────────────────────────────┐
# │ Operation            │ Complexity   │ Notes                         │
# ├──────────────────────┼──────────────┼───────────────────────────────┤
# │ len(lst)             │ O(1)         │ stored as ob_size             │
# │ lst[i] / lst[i] = v  │ O(1)         │ pointer arithmetic            │
# │ lst.append(v)        │ O(1) amort.  │ rare realloc = O(n)           │
# │ lst.pop()            │ O(1)         │ remove from end               │
# │ lst.insert(0, v)     │ O(n)         │ shifts all elements right     │
# │ lst.pop(0)           │ O(n)         │ shifts all elements left      │
# │ v in lst             │ O(n)         │ linear scan                   │
# │ lst.index(v)         │ O(n)         │ linear scan                   │
# │ lst.sort()           │ O(n log n)   │ Timsort                       │
# │ lst[a:b] (slice)     │ O(b-a)       │ shallow copy                  │
# │ lst.extend(other)    │ O(k)         │ k = len(other)                │
# └──────────────────────┴──────────────┴───────────────────────────────┘


# ============================================================
# PART 2: DICTIONARIES — THE POWERHOUSE
# ============================================================
#
# INTERNAL IMPLEMENTATION (CPython 3.6+):
# A dict is an OPEN-ADDRESSED HASH TABLE split into two arrays:
#
#   1. INDICES array (sparse): maps hash -> slot
#   2. ENTRIES array (dense):  stores (hash, key_ptr, value_ptr)
#
#   dict = {"name": "Manav", "age": 25}
#
#   INDICES (sparse, hash-bucket lookup):
#   index:   0    1    2    3    4    5    6    7
#         [ -1 |  1 | -1 | -1 | -1 | -1 |  0 | -1 ]   (-1 = empty)
#
#   ENTRIES (dense, insertion-ordered):
#   slot 0: (hash("name"), "name", "Manav")
#   slot 1: (hash("age"),  "age",  25)
#
#   Lookup d["age"]:
#     1. h = hash("age")           -> fast C-level hash
#     2. bucket = h % table_size   -> say bucket 1
#     3. indices[1] == 1           -> entry slot 1
#     4. entries[1].key == "age"?  -> YES -> return entries[1].value (25)
#
# WHY dict is O(1):
#   The hash function turns the key into a number; modular arithmetic
#   jumps directly to the right bucket. No scanning required.
#   (Technically O(1) average; worst case O(n) if every key collides,
#    but Python's random hash seed makes this astronomically unlikely.)
#
#   Load factor kept ~2/3. When exceeded, the table RESIZES (doubles)
#   and all keys are re-inserted -> amortized O(1) per insert.

# --- CREATION ---
empty_dict = {}
person = {"name": "Manav", "age": 25, "city": "Pune"}
person2 = dict(name="Alice", age=30)      # Alternative constructor

# --- ACCESSING ---
print(person["name"])                     # Manav -> O(1) lookup!
# print(person["email"])                  # ✗ KeyError if key doesn't exist

# Safe access with .get():
print(person.get("email"))                # None (no error)
print(person.get("email", "Not found"))   # "Not found" (default value)

# --- ADD/UPDATE ---
person["email"] = "manav@example.com"     # Add new key -> O(1)
person["age"] = 26                        # Update existing -> O(1)
print(person)

# --- DELETE ---
del person["city"]                        # Delete by key -> O(1)
person.pop("email")                       # Delete and return value -> O(1)
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
print("India" in capitals)                # True -> O(1)
print("USA" in capitals)                  # False

# --- USEFUL DICT METHODS ---
print(capitals.keys())                    # dict_keys(['India', 'France', 'Japan'])
print(capitals.values())                  # dict_values(['New Delhi', 'Paris', 'Tokyo'])
print(capitals.items())                   # dict_items([('India', 'New Delhi'), ...])

# DICT COMPREHENSION (filter/transform dicts):
prices = {"apple": 1.0, "banana": 0.5, "cherry": 3.0}
expensive = {k: v for k, v in prices.items() if v >= 1.0}
print(f"Expensive items: {expensive}")

# MERGING DICTS (Python 3.9+ merge operator |):
defaults = {"theme": "light", "font": "Arial"}
user_prefs = {"theme": "dark"}
merged = defaults | user_prefs           # user_prefs wins on conflict
print(f"Merged: {merged}")               # {'theme': 'dark', 'font': 'Arial'}


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
count_new = defaultdict(int)              # int() -> 0
for word in words:
    count_new[word] += 1                  # No need to check!
print(f"Count (defaultdict): {dict(count_new)}")

# --- DEFAULTDICT DEEP DIVE ---
# defaultdict subclasses dict. It overrides __missing__(key):
# when a key isn't found, it calls the factory (e.g. int, list, set),
# inserts the result, and returns it -- instead of raising KeyError.

# Factory = list  ->  group items by a key (grouping pattern)
students_by_grade = defaultdict(list)
for name, grade in [("Alice", "A"), ("Bob", "B"), ("Carol", "A")]:
    students_by_grade[grade].append(name)
print(f"Grouped: {dict(students_by_grade)}")
# {'A': ['Alice', 'Carol'], 'B': ['Bob']}

# Factory = set  ->  deduplicate while grouping
tags_by_user = defaultdict(set)
for user, tag in [("u1", "python"), ("u1", "ai"), ("u1", "python")]:
    tags_by_user[user].add(tag)
print(f"Tags: {dict(tags_by_user)}")      # {'u1': {'python', 'ai'}}

# WARNING: accessing a key in defaultdict CREATES it (side effect!)
d = defaultdict(int)
_ = d["ghost"]                            # just reading, but now d == {"ghost": 0}
print(f"Side effect: {dict(d)}")          # {'ghost': 0}
# Use d.get("ghost") if you want to read without inserting.


# --- COUNTER (frequency counting in one line) ---
from collections import Counter
word_counts = Counter(words)
print(f"Counter: {word_counts}")          # Counter({'apple': 3, 'banana': 2, 'cherry': 1})
print(f"Top 2: {word_counts.most_common(2)}")  # [('apple', 3), ('banana', 2)]

# --- COUNTER DEEP DIVE ---
# Counter is a dict subclass for counting hashable objects.

# Count characters in a string:
char_count = Counter("abracadabra")
print(f"Chars: {char_count}")             # Counter({'a': 5, 'b': 2, 'r': 2, ...})

# Counter arithmetic (merge/diff frequency tables):
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
print(f"c1 + c2: {c1 + c2}")             # Counter({'a': 4, 'b': 3})  (add counts)
print(f"c1 - c2: {c1 - c2}")             # Counter({'a': 2})          (subtract, drop <=0)

# Multiset operations (intersection/union by min/max count):
print(f"c1 & c2 (min): {c1 & c2}")       # Counter({'a': 1, 'b': 1})
print(f"c1 | c2 (max): {c1 | c2}")       # Counter({'a': 3, 'b': 2})

# elements() yields each item repeated by its count:
print(list(Counter(a=2, b=3).elements())) # ['a', 'a', 'b', 'b', 'b']

# ============================================================
# DICT PERFORMANCE TABLE
# ============================================================
# ┌──────────────────────┬──────────────┬───────────────────────────────┐
# │ Operation            │ Complexity   │ Notes                         │
# ├──────────────────────┼──────────────┼───────────────────────────────┤
# │ len(d)               │ O(1)         │ stored internally              │
# │ d[k]                 │ O(1) avg     │ hash -> bucket; worst O(n)     │
# │ d[k] = v             │ O(1) avg     │ may trigger resize            │
# │ del d[k] / d.pop(k)  │ O(1) avg     │                               │
# │ k in d               │ O(1) avg     │ hash lookup                   │
# │ d.get(k)             │ O(1) avg     │                               │
# │ d.keys/values/items  │ O(1)         │ returns a VIEW (lazy)         │
# │ iteration            │ O(n)         │ visits every entry            │
# │ copy()               │ O(n)         │ shallow copy                  │
# └──────────────────────┴──────────────┴───────────────────────────────┘


# ============================================================
# PART 3: SETS — THE DEDUPLICATOR
# ============================================================
#
# A set is like a mathematical set: unique elements only, no order.
#
# INTERNAL IMPLEMENTATION:
#   A set is a hash table JUST like a dict, but it stores only keys
#   (no values). Membership test and dedup are therefore O(1) avg.
#
#   set = {"apple", "banana"}
#
#   Hash table (simplified):
#   bucket:  0        1        2        3        4        5
#         [ empty ][banana ][ empty ][ empty ][apple  ][ empty ]
#
#   Insertion order is NOT preserved (and iteration order depends on
#   hash values, which are randomized per process via PYTHONHASHSEED).

# --- CREATION ---
empty_set = set()                         # NOT {} (that's a dict!)
fruits_set = {"apple", "banana", "cherry"}
from_list = set([1, 2, 2, 3, 3, 3])      # Removes duplicates!
print(f"From list with dups: {from_list}")  # {1, 2, 3}

# --- ADD/REMOVE ---
fruits_set.add("date")                    # Add -> O(1) avg
fruits_set.discard("banana")              # Remove (no error if missing) -> O(1)
# fruits_set.remove("zzz")                # ✗ KeyError if not present
print(fruits_set)

# --- SET OPERATIONS (like math class!) ---
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7, 8}

print(f"Union: {A | B}")                  # {1, 2, 3, 4, 5, 6, 7, 8}     O(len(A)+len(B))
print(f"Intersection: {A & B}")           # {4, 5}                        O(min(len))
print(f"Difference: {A - B}")             # {1, 2, 3}                     O(len(A))
print(f"Symmetric diff: {A ^ B}")         # {1, 2, 3, 6, 7, 8} (in one but not both)

# Subset / superset checks:
print({1, 2}.issubset(A))                 # True
print(A.issuperset({1, 2}))               # True
print({1, 2, 3} == {3, 2, 1})             # True (order doesn't matter!)

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
_ = 999999 in big_list                    # O(n) -- slow
print(f"List lookup: {time.time() - start:.6f}s")

start = time.time()
_ = 999999 in big_set                     # O(1) -- instant!
print(f"Set lookup:  {time.time() - start:.6f}s")

# --- FROZENSET (immutable set) ---
# Like tuple is to list, frozenset is to set: immutable, hashable.
# Use as a dict key, or when a set must not change.
fs = frozenset([1, 2, 3, 2])              # frozenset({1, 2, 3})
print(f"Frozenset: {fs}")
# fs.add(4)                               # ✗ AttributeError -- no mutation
set_as_key = {frozenset({1, 2}): "pair"}  # OK: frozenset is hashable
print(set_as_key)

# ============================================================
# SET PERFORMANCE TABLE
# ============================================================
# ┌──────────────────────┬──────────────┬───────────────────────────────┐
# │ Operation            │ Complexity   │ Notes                         │
# ├──────────────────────┼──────────────┼───────────────────────────────┤
# │ len(s)               │ O(1)         │                               │
# │ x in s               │ O(1) avg     │ hash lookup                   │
# │ s.add(x)             │ O(1) avg     │ may resize                    │
# │ s.discard(x)         │ O(1) avg     │                               │
# │ s | t (union)        │ O(len(s)+len(t))                          │
# │ s & t (intersection) │ O(min(len(s), len(t)))                    │
# │ s - t (difference)   │ O(len(s))                                  │
# │ s == t               │ O(n)         │ element-wise                 │
# └──────────────────────┴──────────────┴───────────────────────────────┘


# ============================================================
# PART 4: TUPLES — THE IMMUTABLE LIST
# ============================================================
#
# A tuple is like a list but CANNOT BE CHANGED after creation.
# Use for: coordinates, fixed configurations, return multiple values.
#
# INTERNAL IMPLEMENTATION:
#   A tuple is a FIXED-SIZE array of PyObject* pointers -- same as a
#   list, but with NO over-allocation and NO mutability. Because the
#   size is fixed and the layout is compact, tuples use less memory
#   than lists of the same length.
#
#   tuple = (10, 20, 30)
#
#   PyTupleObject:
#   ┌────────┬────────┬────────┬────────┐
#   │  ob[0] │  ob[1] │  ob[2] │  NULL  │   (NULL sentinel marks the end)
#   └───┬────┴───┬────┴───┬────┴────────┘
#       ▼        ▼        ▼
#      10       20       30      <- immutable int objects
#
#   NOTE: the tuple itself is immutable, but if an element is a
#   mutable object (e.g. a list), THAT object can still change:
#       t = ([1, 2], 3)
#       t[0].append(99)    # legal! tuple still points to the same list

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

# Subtle: the tuple is immutable, but contained mutable objects aren't:
t_with_list = ([1, 2], "x")
t_with_list[0].append(3)
print(f"Tuple with mutated list: {t_with_list}")  # ([1, 2, 3], 'x')
# The tuple's REFERENCE didn't change, so this is allowed.

# --- TUPLE UNPACKING ---
# Assign tuple elements to separate variables
x, y = point
print(f"x={x}, y={y}")                    # x=3, y=5

# Swap variables (this works because Python creates a tuple!)
a, b = 10, 20
a, b = b, a

# Extended unpacking (star expression):
first, *middle, last = (1, 2, 3, 4, 5)
print(f"first={first}, middle={middle}, last={last}")  # first=1, middle=[2,3,4], last=5

# --- WHY USE TUPLES INSTEAD OF LISTS? ---
# 1. Safety: can't be accidentally modified
# 2. Can be used as DICT KEYS (lists cannot!)
locations = {(40.7, -74.0): "New York", (34.0, -118.2): "Los Angeles"}
print(locations[(40.7, -74.0)])           # New York

# 3. Slightly faster and less memory than lists
# 4. Signal intent: "this data shouldn't change"

# --- NAMEDTUPLE (readable, self-documenting tuples) ---
from collections import namedtuple

# A namedtuple is a tuple with named fields -- like a tiny class.
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 5)
print(f"{p.x}, {p.y}")                    # 3, 5   (access by name!)
print(p[0])                               # 3       (still indexable)
print(p._asdict())                        # {'x': 3, 'y': 5}

# Great for returning multiple labeled values from a function:
Stats = namedtuple("Stats", ["mean", "median", "mode"])


def summarize(values):
    return Stats(mean=sum(values) / len(values),
                 median=sorted(values)[len(values) // 2],
                 mode=values[0])


s = summarize([1, 2, 3])
print(f"mean={s.mean} median={s.median} mode={s.mode}")

# ============================================================
# TUPLE PERFORMANCE TABLE
# ============================================================
# ┌──────────────────────┬──────────────┬───────────────────────────────┐
# │ Operation            │ Complexity   │ Notes                         │
# ├──────────────────────┼──────────────┼───────────────────────────────┤
# │ len(t)               │ O(1)         │                               │
# │ t[i]                 │ O(1)         │ pointer arithmetic            │
# │ x in t               │ O(n)         │ linear scan                   │
# │ t[a:b]               │ O(b-a)       │ new tuple                     │
# │ t.count(x)/index(x)  │ O(n)         │                               │
# │ hash(t)              │ O(n)         │ hashes each element (cached)  │
# │ creation             │ O(n)         │                               │
# └──────────────────────┴──────────────┴───────────────────────────────┘


# ============================================================
# PART 5: DEQUE — FAST QUEUE
# ============================================================
#
# INTERNAL IMPLEMENTATION (CPython):
#   A deque is a DOUBLY-LINKED LIST OF FIXED-SIZE BLOCKS (arrays of 64
#   PyObject* each), NOT a single linked list. This gives O(1) append/
#   pop at both ends while keeping cache-friendly contiguous storage.
#
#   deque = deque([1, 2, 3])
#
#        left side                        right side
#   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
#   │ [..][..][ 1 ]│<-->│[ 2 ][ 3 ][..]│<-->│[..][..][..] │
#   └──────────────┘    └──────────────┘    └──────────────┘
#        ^                                          ^
#     appendleft                                append
#     popleft                                      pop
#
#   Each block holds up to 64 pointers. Adding beyond a block's edge
#   allocates a new block (O(1)) -- no element shifting needed.

from collections import deque

# A deque (double-ended queue) is like a list but O(1) for both ends.
# Use when you need to add/remove from BOTH front and back frequently.

# LIST:  append()=O(1), pop()=O(1), but insert(0)=O(n), pop(0)=O(n)
# DEQUE: append()=O(1), pop()=O(1), appendleft()=O(1), popleft()=O(1)

dq = deque([1, 2, 3])
dq.append(4)                              # Add to right -> [1, 2, 3, 4]
dq.appendleft(0)                          # Add to left -> [0, 1, 2, 3, 4]
print(f"Deque: {dq}")

dq.pop()                                  # Remove from right -> [0, 1, 2, 3]
dq.popleft()                              # Remove from left -> [1, 2, 3]
print(f"After pops: {dq}")

# For BFS / queue usage: always use deque, not list!
queue = deque()
queue.append("task1")
queue.append("task2")
while queue:
    task = queue.popleft()                # FIFO -- first in, first out
    print(f"  Processing: {task}")

# --- DEQUE USE CASES ---

# 1. BOUNDED QUEUE (sliding window / recent items) with maxlen:
recent = deque(maxlen=3)
for i in range(5):
    recent.append(i)                      # oldest items auto-evicted
print(f"Recent (maxlen=3): {recent}")     # deque([2, 3, 4], maxlen=3)

# 2. STACK (LIFO) -- append/pop from same end:
stack = deque()
stack.append("a")
stack.append("b")
print(stack.pop())                        # 'b' (last in, first out)

# 3. ROTATE (circular buffer):
ring = deque([1, 2, 3, 4, 5])
ring.rotate(2)                            # rotate right by 2
print(f"Rotated +2: {ring}")              # deque([4, 5, 1, 2, 3])
ring.rotate(-1)                           # rotate left by 1
print(f"Rotated -1: {ring}")              # deque([5, 1, 2, 3, 4])

# ============================================================
# DEQUE PERFORMANCE TABLE
# ============================================================
# ┌──────────────────────┬──────────────┬───────────────────────────────┐
# │ Operation            │ Complexity   │ Notes                         │
# ├──────────────────────┼──────────────┼───────────────────────────────┤
# │ append / appendleft  │ O(1)         │ no realloc                    │
# │ pop / popleft        │ O(1)         │ no shift                      │
# │ d[i]                 │ O(n)         │ must walk blocks (SLOW!)      │
# │ x in d               │ O(n)         │ linear scan                   │
# │ insert(i, x)         │ O(n)         │ middle insert is slow         │
# │ rotate(k)            │ O(k)         │ k = abs(rotation)             │
# └──────────────────────┴──────────────┴───────────────────────────────┘
# WARNING: random indexing d[i] is O(n) for deque -- if you need fast
# indexed access, use a list instead!


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

# zip() stops at the SHORTEST iterable. Use zip_longest for uneven:
from itertools import zip_longest
pairs = list(zip_longest([1, 2, 3], ["a", "b"], fillvalue="?"))
print(f"zip_longest: {pairs}")            # [(1, 'a'), (2, 'b'), (3, '?')]

# --- UNPACKING WITH * ---
first, *rest = [1, 2, 3, 4, 5]
print(f"First: {first}, Rest: {rest}")    # First: 1, Rest: [2, 3, 4, 5]

*init, last = [1, 2, 3, 4, 5]
print(f"Init: {init}, Last: {last}")      # Init: [1, 2, 3, 4], Last: 5

# --- ANY() AND ALL() ---
print(any([False, False, True]))          # True (at least one is True)
print(all([True, True, False]))           # False (not all are True)
print(any([]))                            # False (empty = nothing True)
print(all([]))                            # True (vacuously true -- edge case!)

# --- ENUMERATE (index + value together) ---
for idx, val in enumerate(["a", "b", "c"]):
    print(f"  [{idx}] = {val}")


# ============================================================
# PART 7: WHEN TO USE WHICH — DECISION GUIDE
# ============================================================
#
# ┌─────────────────────────────────────────────────────────────────┐
# │  "I need to..."                       ->  Use this              │
# ├─────────────────────────────────────────────────────────────────┤
# │  ...keep things in order              ->  list                   │
# │  ...look things up by a key/name      ->  dict                   │
# │  ...remove duplicates                 ->  set                    │
# │  ...store a fixed, unchanging group   ->  tuple                  │
# │  ...map keys -> lists/sets            ->  defaultdict(list/set)  │
# │  ...count how often things appear     ->  Counter                │
# │  ...add/remove from BOTH ends         ->  deque                  │
# │  ...use a collection as a dict key    ->  tuple / frozenset      │
# │  ...named fields (tiny class)         ->  namedtuple             │
# │  ...a stack (push/pop one end)        ->  list (append/pop)      │
# │  ...a queue (FIFO)                    ->  deque (append/popleft) │
# │  ...priority order                    ->  heapq (see Ch. heap)   │
# └─────────────────────────────────────────────────────────────────┘
#
# QUICK RULES OF THUMB:
#   * Default to list for ordered sequences.
#   * Reach for dict the instant you need lookup by key.
#   * Reach for set the instant you need uniqueness or fast `in`.
#   * Reach for tuple when the data is fixed / must be hashable.
#   * Reach for deque only when you manipulate BOTH ends.


# ============================================================
# PART 8: COMMON PITFALLS
# ============================================================

# --- PITFALL 1: Mutating a list while iterating over it ---
# BAD: removing items while looping skips elements!
# nums_bad = [1, 2, 3, 4, 5]
# for n in nums_bad:
#     if n % 2 == 0:
#         nums_bad.remove(n)        # skips the element after a removal
# Iterate over a COPY instead, or use a comprehension:
nums_bad = [1, 2, 3, 4, 5]
nums_clean = [n for n in nums_bad if n % 2 != 0]
print(f"Filtered (safe): {nums_clean}")

# --- PITFALL 2: Shallow copy vs deep copy ---
original_nested = [[1, 2], [3, 4]]
shallow = original_nested.copy()          # new list, SAME inner lists
shallow[0][0] = 99                        # mutates original's inner list too!
print(f"Shallow copy side effect: {original_nested}")  # [[99, 2], [3, 4]]

import copy
original_nested2 = [[1, 2], [3, 4]]
deep = copy.deepcopy(original_nested2)    # fully independent copy
deep[0][0] = 99
print(f"Deep copy safe: {original_nested2}")            # [[1, 2], [3, 4]]

# --- PITFALL 3: Default mutable arguments ---
# BAD: the default list is shared across ALL calls!
# def add_item(item, lst=[]):       # <- this list is created ONCE
#     lst.append(item)
#     return lst
# Fix: use None and create inside:
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst


print(add_item("a"))                      # ['a']
print(add_item("b"))                      # ['b']  (not ['a', 'b']!)

# --- PITFALL 4: Using `is` instead of `==` for value comparison ---
# `is` checks IDENTITY (same object), `==` checks VALUE (equality).
a_list = [1, 2, 3]
b_list = [1, 2, 3]
print(a_list == b_list)                   # True  (same values)
print(a_list is b_list)                   # False (different objects)
# Use `is` only for None, True, False, or sentinel singletons.

# --- PITFALL 5: Chained comparisons look like math (and they work!) ---
val = 5
print(1 < val < 10)                       # True -- Python allows this!
# But don't confuse with: 1 < val & val < 10  (operator precedence trap)

# --- PITFALL 6: Dict key ordering assumptions before 3.7 ---
# In Python 3.7+, dicts preserve INSERTION order (guaranteed).
# In 3.6 it was an implementation detail of CPython.
# Before 3.6, dict order was ARBITRARY -- don't rely on it in old code.

# --- PITFALL 7: Set/dict keys must be HASHABLE ---
# Lists, dicts, and sets are NOT hashable (they're mutable) -> can't be keys.
# d = {[1, 2]: "x"}            # ✗ TypeError: unhashable type: 'list'
ok = {(1, 2): "x"}                        # OK tuple is hashable
# A tuple containing a list is ALSO unhashable:
# bad = {([1, 2],): "y"}       # ✗ TypeError (inner list is mutable)

# --- PITFALL 8: Modifying a set/dict while iterating ---
# Adding/removing during iteration -> RuntimeError or skipped items.
s = {1, 2, 3, 4}
# for x in s:
#     s.remove(x)              # ✗ RuntimeError: Set changed size during iteration
# Safe: iterate over a copy, or build a new collection:
to_remove = [x for x in s if x % 2 == 0]
for x in to_remove:
    s.discard(x)
print(f"Set after safe removal: {s}")

# --- PITFALL 9: `sorted()` vs `.sort()` return value ---
nums3 = [3, 1, 2]
# nums3 = nums3.sort()         # ✗ nums3 becomes None! .sort() returns None
nums3 = sorted(nums3)                    # OK sorted() returns a new list
print(f"Properly sorted: {nums3}")

# --- PITFALL 10: Integer caching and `is` for small ints ---
# CPython caches small ints (-5..256), so `is` can MISLEAD.
# Using `is` on a literal also raises a SyntaxWarning in 3.8+, so we
# demonstrate the caching with VARIABLES instead:
a256, b256 = 256, 256
print(a256 == b256, a256 is b256)         # True True  (256 is cached)
a257, b257 = 257, 257
print(a257 == b257, a257 is b257)         # True True  (same literal here)
# But 257 from separate computations may NOT be the same object:
big1 = 1000
big2 = 1000
print(big1 == big2, big1 is big2)         # True, but `is` is NOT guaranteed
# Lesson: NEVER use `is` to compare numbers/strings. Use `==`.


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 4 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. List: ordered, mutable. append/pop=O(1). insert/pop(0)=O(n).
   Internally a dynamic array with geometric over-allocation.
2. Dict: key->value. O(1) lookup. Internally an open-addressed hash
   table (sparse index array + dense entries array). Use
   defaultdict/Counter for counting and grouping.
3. Set: unique elements. O(1) membership test. Same hash machinery
   as dict. Union/intersection/difference for math-like ops.
   frozenset = immutable, hashable set.
4. Tuple: immutable list. Fixed array, no over-alloc -> less memory.
   Use for coordinates, dict keys, unpacking. namedtuple adds
   readable field names.
5. Deque: O(1) at both ends (block-based doubly-linked structure).
   Use for queues/BFS. Avoid indexed access (it's O(n)).
6. Patterns: zip(), enumerate(), unpacking with *, any()/all().
7. Pitfalls: mutating while iterating, shallow vs deep copy,
   mutable default args, `is` vs `==`, unhashable keys.

Next: Chapter 5 — Strings Deep Guide
""")
