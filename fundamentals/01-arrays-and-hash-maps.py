'''
CHAPTER 1: ARRAYS & HASH MAPS — THE COMPLETE DEEP DIVE
========================================================

"These two data structures are the foundation of all interview problem
solving. 80% of LeetCode problems can be solved with arrays and hash maps.
Master them and you can solve almost any problem."

---

PART 1: ARRAYS — THE MOST FUNDAMENTAL DATA STRUCTURE
=====================================================

WHAT IS AN ARRAY?
-----------------
An array is a collection of elements stored CONTIGUOUSLY in memory.
This means all elements are placed side-by-side, like a row of lockers.

    Memory address:  1000   1004   1008   1012   1016
    Index:           [ 0 ]  [ 1 ]  [ 2 ]  [ 3 ]  [ 4 ]
    Value:           [ 10]  [ 25]  [ 37]  [ 48]  [ 50]

Each locker:
    - Has an INDEX (position number), starting from 0
    - Stores exactly one value
    - Occupies a fixed amount of memory (4 bytes for int, 8 for float, etc.)

WHY INDEX STARTS AT 0:
    The index is actually an OFFSET from the start of the array.
    arr[0] means "start address + 0 bytes offset"
    arr[3] means "start address + 3 × element_size bytes"

    If the array starts at memory address 1000 and each int is 4 bytes:
    arr[0] → address 1000 + (0 × 4) = 1000
    arr[1] → address 1000 + (1 × 4) = 1004
    arr[2] → address 1000 + (2 × 4) = 1008
    arr[3] → address 1000 + (3 × 4) = 1012

    This is why arr[3] is O(1) — Python calculates the memory address
    with simple math: base_address + index × element_size. Instant.
'''

# --- CREATING ARRAYS ---
fruits = ["apple", "banana", "cherry", "date"]
print(fruits)              # ['apple', 'banana', 'cherry', 'date']

# Different ways to create arrays:
empty = []                          # Empty array
zeros = [0] * 5                     # [0, 0, 0, 0, 0]
range_list = list(range(5))         # [0, 1, 2, 3, 4]
matrix = [[0] * 3 for _ in range(3)]  # 3×3 grid: [[0,0,0],[0,0,0],[0,0,0]]

# --- ACCESSING BY INDEX ---
print(fruits[0])           # 'apple'  (first element)
print(fruits[3])           # 'date'   (fourth element)
print(fruits[-1])          # 'date'   (last element — Python negative indexing)
print(fruits[-2])          # 'cherry' (second to last)

# --- MODIFYING ---
fruits[1] = "blueberry"    # Replace index 1
print(fruits)              # ['apple', 'blueberry', 'cherry', 'date']


'''
THE O(1) INDEX ACCESS — WHY IS IT INSTANT?
------------------------------------------
Because arrays are contiguous, Python can compute the exact memory address
of any element with simple math:

    address_of(arr[i]) = base_address + (i × element_size)

    arr = [10, 25, 37, 48, 50]  (base_address = 1000, element_size = 4 bytes)
    arr[3] → 1000 + (3 × 4) = 1012 → Go directly to address 1012 → read 48

    No matter how big the array is, this calculation takes the same time.
    That's why array access is O(1) — constant time.

DYNAMIC ARRAYS IN PYTHON
------------------------
Python lists are "dynamic arrays." They automatically resize when you
add elements:

    1. Python starts by allocating space for ~4 elements
    2. When you append beyond capacity, Python:
       a. Allocates a NEW larger array (usually 2× the size)
       b. Copies all existing elements to the new array
       c. Frees the old array
    3. This is why append() is "amortized O(1)" — occasionally slow
       (during resize), but averages to O(1) over many operations.

    AMORTIZED O(1) EXPLAINED:
      10 appends: maybe 1 resize. 9 are O(1), 1 is O(n).
      Average: (9×1 + 1×n) / 10 ≈ O(1) when averaged over many calls.

COMMON ARRAY OPERATIONS — THE COMPLETE COST TABLE
--------------------------------------------------
| Operation              | Code             | Time    | Space | Why?                          |
|------------------------|------------------|---------|-------|-------------------------------|
| Access by index        | arr[3]           | O(1)    | O(1)  | Direct address calculation    |
| Modify by index        | arr[3] = x       | O(1)    | O(1)  | Same as access                |
| Append to end          | arr.append(x)    | O(1)*   | O(1)  | Just write to next slot       |
| Insert at front        | arr.insert(0, x) | O(n)    | O(1)  | Must SHIFT all elements right |
| Insert at index i      | arr.insert(i, x) | O(n)    | O(1)  | Shift elements from i onward  |
| Delete from end        | arr.pop()        | O(1)    | O(1)  | Just remove last slot         |
| Delete from front      | arr.pop(0)       | O(n)    | O(1)  | Must SHIFT all elements left  |
| Delete by value        | arr.remove(x)    | O(n)    | O(1)  | Find (O(n)) + shift (O(n))    |
| Find element           | x in arr         | O(n)    | O(1)  | Must scan until found         |
| Get length             | len(arr)         | O(1)    | O(1)  | Python stores length as attr  |
| Slice                  | arr[1:4]         | O(k)    | O(k)  | k = slice length. Creates copy|
| Sort                   | arr.sort()       | O(n log n)| O(1)| Timsort algorithm             |
| Reverse                | arr.reverse()    | O(n)    | O(1)  | Swap elements from both ends  |

* Amortized O(1)
'''

# --- THE INSERT PROBLEM — VISUALIZED ---
# Why is inserting at the front O(n)?
arr = [10, 25, 37, 48, 50]
print("\nBefore insert:", arr)

# Insert 99 at index 0:
# Step 1: Python allocates space for one more element
# Step 2: SHIFT every element RIGHT by one position
#
#   [10, 25, 37, 48, 50, __]
#   [10, 25, 37, 48, 50, 50]  ← 50 moves to slot 5
#   [10, 25, 37, 48, 48, 50]  ← 48 moves to slot 4
#   [10, 25, 37, 37, 48, 50]  ← 37 moves to slot 3
#   [10, 25, 25, 37, 48, 50]  ← 25 moves to slot 2
#   [10, 10, 25, 37, 48, 50]  ← 10 moves to slot 1
# Step 3: Write 99 at slot 0
#   [99, 10, 25, 37, 48, 50]
#
# Every element had to move! If there are n elements, that's n shifts → O(n).

arr.insert(0, 99)
print("After insert at 0:", arr)  # [99, 10, 25, 37, 48, 50]

# --- APPEND IS O(1) — VISUALIZED ---
# When there's space, append just writes to the next slot. No shifting needed.
arr2 = [10, 25, 37]
#   [10, 25, 37, __]  ← slot 3 is empty
#   Write 48 to slot 3
#   [10, 25, 37, 48]
# Done! O(1).

arr2.append(48)
print("After append:", arr2)  # [10, 25, 37, 48]


'''
ARRAY SLICING — THE COMPLETE GUIDE
-----------------------------------
Slicing creates a NEW array (a copy of a portion of the original).

Syntax: arr[start:stop:step]
    start: beginning index (INCLUSIVE). Default: 0
    stop:  ending index (EXCLUSIVE). Default: len(arr)
    step:  how to move. Default: 1. Negative = backwards.

    MEMORY HOOK: "Start is IN, stop is OUT."
    arr[1:4] → includes index 1, 2, 3 (NOT 4)
'''

word = "Hello World"

# Basic slicing
print(word[0:5])       # "Hello"     (indices 0,1,2,3,4)
print(word[6:])        # "World"     (from index 6 to end)
print(word[:5])        # "Hello"     (from start to index 4)
print(word[:])         # "Hello World" (entire string — creates a COPY)

# Step slicing
print(word[::2])       # "HloWrd"   (every 2nd character)
print(word[1::2])      # "el ol"    (every 2nd, starting at 1)
print(word[::-1])      # "dlroW olleH" (REVERSED! Very common interview trick)

# Negative slicing
print(word[-5:])       # "World"    (last 5 characters)
print(word[-1])        # "d"        (last character)

# 2D ARRAY SLICING (matrix)
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
# Get row 1: matrix[1] → [4, 5, 6]
# Get column 1: [row[1] for row in matrix] → [2, 5, 8]
# Get sub-matrix (top-left 2×2): [row[:2] for row in matrix[:2]] → [[1,2],[4,5]]

print(f"\nMatrix row 1: {matrix[1]}")          # [4, 5, 6]
print(f"Matrix col 1: {[row[1] for row in matrix]}")  # [2, 5, 8]


'''
PART 2: HASH MAPS (PYTHON DICTIONARIES)
========================================

WHAT IS A HASH MAP?
-------------------
A hash map is a data structure that stores KEY-VALUE PAIRS and provides
O(1) average-time lookup, insertion, and deletion.

Real-world analogy: A DICTIONARY (the book kind).
    "apple" → "A round fruit with red or green skin"
    "banana" → "A long curved fruit"

    You don't read every page to find "banana." You use the alphabetical
    ordering to jump directly to B.

In Python, a hash map is called a "dict":
'''

# --- CREATING A HASH MAP ---
ages = {
    "Alice": 30,
    "Bob": 25,
    "Charlie": 35,
}

# Empty hash map
empty_dict = {}
also_empty = dict()

# From pairs
from_pairs = dict([("a", 1), ("b", 2)])

# --- ACCESSING BY KEY ---
print(ages["Alice"])        # 30 — O(1) average lookup!

# Safe access (no KeyError if key doesn't exist):
print(ages.get("David"))         # None (key doesn't exist → returns None)
print(ages.get("David", 0))      # 0 (custom default value)
# print(ages["David"])           # ← KeyError! Use .get() to avoid this.


'''
HOW DOES A HASH MAP WORK UNDER THE HOOD?
-----------------------------------------
(This is one of the MOST COMMON interview questions. Understand this deeply.)

STEP 1: You store a key-value pair: ages["Alice"] = 30

STEP 2: Python runs "Alice" through a HASH FUNCTION.
    A hash function takes any input and produces a fixed-size number.
    Same input always gives the same number.

    "Alice" → hash function → 3448392018 (a large integer)

STEP 3: Python takes that large number and computes the bucket index:
    bucket_index = hash_value % table_size

    If the table has 8 slots: 3448392018 % 8 = 2
    So "Alice" goes into slot 2.

STEP 4: The key-value pair is stored at slot 2.

    ┌───┬───┬───┬───┬───┬───┬───┬───┐
    │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │   ← 8 slots (buckets)
    └───┴───┴─║─┴───┴───┴───┴───┴───┘
                ↑
            "Alice": 30

STEP 5: When you ask for ages["Alice"]:
    → Hash "Alice" → 3448392018
    → 3448392018 % 8 = 2
    → Go to slot 2
    → Found "Alice": 30 → return 30

    ALL OF THIS IS O(1) — constant time, regardless of how many items
    are in the hash map!

WHY IS IT O(1)? Because the hash function directly computes WHERE the
key is stored. No scanning needed. It's like knowing the exact shelf
number for a book, rather than searching shelf by shelf.
'''

# --- ADDING AND UPDATING ---
ages["David"] = 28         # Add new key → O(1)
ages["Alice"] = 31         # Update existing key → O(1
print(ages)

# --- DELETING ---
del ages["David"]          # Delete by key → O(1)
removed = ages.pop("Bob")  # Delete and return the value → O(1)
print(ages)

# --- CHECKING IF KEY EXISTS ---
print("Alice" in ages)     # True → O(1)
print("Bob" in ages)       # False → O(1)


'''
HASH COLLISIONS — WHAT IF TWO KEYS HASH TO THE SAME SLOT?
----------------------------------------------------------
Collision: "Alice" hashes to slot 2. "Alicia" ALSO hashes to slot 2.
    What happens?

SOLUTION: Each slot holds a LINKED LIST of entries.

    Slot 2: [("Alice", 30)] → [("Alicia", 28)]

    When looking up "Alice":
    1. Hash "Alice" → slot 2
    2. Walk the linked list at slot 2
    3. Compare each key: "Alice" == "Alice"? YES → return 30

    If the linked list is short (1-2 entries), this is still effectively O(1).
    With a good hash function and a properly sized table, collisions are rare.

WORST CASE: Everything hashes to the same slot → one giant linked list → O(n).
    This is extremely rare with Python's built-in hash function.

PYTHON'S RESIZING STRATEGY:
    When the hash map gets > 2/3 full, Python resizes it (doubles the capacity)
    and rehashes all keys. This keeps collisions rare and operations O(1).
'''

# --- ITERATING OVER A HASH MAP ---
capitals = {"India": "New Delhi", "France": "Paris", "Japan": "Tokyo"}

# Iterate over keys (default)
for country in capitals:
    print(f"  Key: {country}")

# Iterate over values
for capital in capitals.values():
    print(f"  Value: {capital}")

# Iterate over key-value pairs (MOST COMMON)
for country, capital in capitals.items():
    print(f"  {country} → {capital}")


'''
HASH MAP OPERATIONS — ALL O(1)!
-------------------------------
| Operation      | Code            | Time (avg) | Time (worst) | Notes                    |
|----------------|-----------------|------------|--------------|--------------------------|
| Get value      | dict[key]       | O(1)       | O(n)         | Worst case: all collide  |
| Safe get       | dict.get(key)   | O(1)       | O(n)         | Returns None if missing  |
| Set value      | dict[key] = val | O(1)       | O(n)         | Creates or updates       |
| Delete         | del dict[key]   | O(1)       | O(n)         | Removes key-value pair   |
| Check key      | key in dict     | O(1)       | O(n)         | Membership test          |
| Iterate        | for k in dict   | O(n)       | O(n)         | Visit each entry         |

Compare to an array where finding an element is O(n) — you must scan!
THIS is why hash maps are the most powerful tool in interviews.
'''

# --- HASH SET (SET) ---
# A set is a hash map with only keys (no values). All operations are O(1).
unique_numbers = {1, 2, 3, 4, 5}
unique_numbers.add(6)       # O(1)
unique_numbers.discard(1)   # O(1)
print(3 in unique_numbers)  # True — O(1)

# Convert list to set to remove duplicates
names = ["Alice", "Bob", "Alice", "Charlie", "Bob"]
unique_names = list(set(names))
print(unique_names)  # ['Charlie', 'Bob', 'Alice'] (order not guaranteed)


'''
PART 3: COLLECTIONS MODULE — POWER-UPS FOR HASH MAPS
=====================================================

Python's collections module provides specialized dictionaries that solve
common interview patterns.
'''

# --- DEFAULTDICT: Auto-initialize missing keys ---
from collections import defaultdict

# PROBLEM: Counting word frequencies without defaultdict
words = "the cat sat on the mat the cat".split()
count_regular = {}
for word in words:
    if word in count_regular:
        count_regular[word] += 1
    else:
        count_regular[word] = 1
# Verbose! The if/else is annoying.

# WITH DEFAULTDICT: Cleaner
count_default = defaultdict(int)  # int() → 0, so missing keys default to 0
for word in words:
    count_default[word] += 1      # No if/else needed!
print(f"\nWord counts: {dict(count_default)}")

# DEFAULTDICT WITH LIST: Group items
# "Group words by their first letter"
word_list = ["apple", "ant", "banana", "berry", "cat", "cherry"]
groups = defaultdict(list)
for w in word_list:
    groups[w[0]].append(w)  # Missing key auto-creates empty list
print(f"Grouped by first letter: {dict(groups)}")
# {'a': ['apple', 'ant'], 'b': ['banana', 'berry'], 'c': ['cat', 'cherry']}

# --- COUNTER: One-line frequency counting ---
from collections import Counter

# The REGULAR way (5 lines):
freq = {}
for word in words:
    freq[word] = freq.get(word, 0) + 1

# The COUNTER way (1 line):
freq_counter = Counter(words)
print(f"Counter: {freq_counter}")
print(f"Most common 2: {freq_counter.most_common(2)}")  # [('the', 3), ('cat', 2)]

# Counter also supports set operations:
c1 = Counter("aabbbcc")
c2 = Counter("abbcccddd")
print(f"Intersection: {c1 & c2}")  # Minimum counts: {'a': 1, 'b': 2, 'c': 2}
print(f"Union: {c1 | c2}")         # Maximum counts: {'a': 2, 'b': 3, 'c': 3, 'd': 3}


'''
PART 4: THE #1 INTERVIEW PATTERN — "HAVE I SEEN THIS BEFORE?"
==============================================================

This pattern solves an incredible number of problems. The core idea:

    "If you need to find two things that relate to each other,
     put the FIRST thing in a hash map, then look it up when
     you see the SECOND thing."

PATTERN STRUCTURE:
    seen = {}
    for item in collection:
        complement = target - item  # or some relationship
        if complement in seen:
            return [seen[complement], item]  # Found the pair!
        seen[item] = index  # Store for later lookup

WHY IT WORKS:
    Instead of checking every pair (O(n²)), you store each element as you go.
    For each new element, check if its "partner" was already seen.
    This turns O(n²) into O(n) — a massive speedup.
'''

# === TWO SUM (LeetCode #1) ===
# "Find two numbers that add up to target. Return their indices."
def two_sum(nums, target):
    """
    BRUTE FORCE: For each number, check every other number. O(n²).
    HASH MAP: Store each number. For the next number, check if
              (target - number) is already in the map. O(n).

    Example: nums = [2, 7, 11, 15], target = 9
    Step 1: See 2. Need 9-2=7. Is 7 in map? No. Store 2→0.
    Step 2: See 7. Need 9-7=2. Is 2 in map? YES! Return [0, 1].
    """
    seen = {}  # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:          # O(1) lookup
            return [seen[complement], i]
        seen[num] = i                   # O(1) store
    return []

print(f"\n--- Two Sum ---")
print(two_sum([2, 7, 11, 15], 9))    # [0, 1]
print(two_sum([3, 2, 4], 6))         # [1, 2]
print(two_sum([3, 3], 6))            # [0, 1]


# === CONTAINS DUPLICATE (LeetCode #217) ===
# "Does the array have any duplicates?"
def has_duplicate(nums):
    """Hash set approach. O(n) time, O(n) space."""
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

print(f"\n--- Contains Duplicate ---")
print(has_duplicate([1, 2, 3, 1]))       # True
print(has_duplicate([1, 2, 3, 4]))       # False


# === VALID ANAGRAM (LeetCode #242) ===
# "Are two strings anagrams (same characters, same counts)?"
def is_anagram(s, t):
    """
    Hash map approach: count characters in both strings, compare.
    O(n) time, O(1) space (26 letters = constant).

    Counter shortcut: Counter(s) == Counter(t)
    """
    if len(s) != len(t):
        return False

    char_count = {}
    for char in s:
        char_count[char] = char_count.get(char, 0) + 1

    for char in t:
        if char not in char_count:
            return False
        char_count[char] -= 1
        if char_count[char] < 0:
            return False

    return True

print(f"\n--- Valid Anagram ---")
print(is_anagram("listen", "silent"))    # True
print(is_anagram("hello", "world"))      # False


# === GROUP ANAGRAMS (LeetCode #49) ===
# "Group words that are anagrams of each other."
def group_anagrams(strs):
    """
    Key insight: Anagrams have the same SORTED string.
    "eat" → sorted → "aet"
    "tea" → sorted → "aet"  ← same key!
    "ate" → sorted → "aet"  ← same key!

    Use sorted string as hash map key. O(n × k log k) where k = avg word length.
    """
    groups = defaultdict(list)
    for word in strs:
        key = ''.join(sorted(word))  # Sort the word to create a canonical key
        groups[key].append(word)

    return list(groups.values())

print(f"\n--- Group Anagrams ---")
result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
print(result)  # [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]


# === TOP K FREQUENT ELEMENTS (LeetCode #347) ===
# "Return the K most frequent elements."
def top_k_frequent(nums, k):
    """
    Three approaches:
    1. Counter + sorting: O(n log n) — sort all by frequency
    2. Counter + heap: O(n log k) — maintain heap of size k
    3. Counter + bucket sort: O(n) — BUCKET SORT! (best)

    Bucket sort approach:
    - Create buckets where bucket[i] = list of numbers with frequency i
    - Iterate from highest frequency bucket down, collecting k elements
    """
    # Step 1: Count frequencies
    freq = Counter(nums)

    # Step 2: Bucket sort — bucket[i] contains all numbers that appear i times
    max_freq = max(freq.values()) if freq else 0
    buckets = [[] for _ in range(max_freq + 1)]
    for num, count in freq.items():
        buckets[count].append(num)

    # Step 3: Collect top k from highest frequency buckets
    result = []
    for i in range(len(buckets) - 1, 0, -1):  # Go from high to low frequency
        for num in buckets[i]:
            result.append(num)
            if len(result) == k:
                return result
    return result

print(f"\n--- Top K Frequent ---")
print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))  # [1, 2]


# === PRODUCT OF ARRAY EXCEPT SELF (LeetCode #238) ===
# "For each index, return the product of ALL other elements. No division."
def product_except_self(nums):
    """
    Key insight: product[i] = (product of everything LEFT of i)
                              × (product of everything RIGHT of i)

    Example: [1, 2, 3, 4]
    Left products:  [1, 1, 2, 6]     (running product from left, start with 1)
    Right products: [24, 12, 4, 1]   (running product from right, start with 1)
    Result:         [24, 12, 8, 6]   (left × right at each position)

    Time: O(n). Space: O(1) extra (output array doesn't count).
    """
    n = len(nums)
    result = [1] * n

    # Left pass: result[i] = product of all elements to the LEFT of i
    left_product = 1
    for i in range(n):
        result[i] = left_product
        left_product *= nums[i]

    # Right pass: multiply by product of all elements to the RIGHT of i
    right_product = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right_product
        right_product *= nums[i]

    return result

print(f"\n--- Product Except Self ---")
print(product_except_self([1, 2, 3, 4]))  # [24, 12, 8, 6]


'''
PART 5: COMMON MISTAKES AND HOW TO AVOID THEM
=============================================

MISTAKE 1: Modifying an array while iterating over it
'''
# BAD: Removing items while iterating skips elements
# nums = [1, 2, 3, 4, 5]
# for i in range(len(nums)):
#     if nums[i] % 2 == 0:
#         nums.pop(i)  # BUG! Indices shift after removal.

# GOOD: Create a new list or iterate backwards
nums = [1, 2, 3, 4, 5]
filtered = [x for x in nums if x % 2 != 0]  # Create new list

'''
MISTAKE 2: Using list when you need O(1) membership test
'''
# BAD: O(n) membership test on a list
big_list = list(range(100000))
# if 99999 in big_list:  # O(n) — scans every element

# GOOD: O(1) membership test on a set
big_set = set(big_list)
# if 99999 in big_set:   # O(1) — instant!

'''
MISTAKE 3: Mutable default arguments
'''
# BAD: Default list is shared across calls!
def add_item_bad(item, lst=[]):
    lst.append(item)
    return lst
# print(add_item_bad(1))  # [1]
# print(add_item_bad(2))  # [1, 2] — NOT [2]! The default list persists.

# GOOD: Use None as default
def add_item_good(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

'''
MISTAKE 4: Shallow copy vs deep copy
'''
import copy

original = [[1, 2], [3, 4]]
shallow = original[:]      # Shallow copy: outer list copied, inner lists shared
shallow[0][0] = 99
# print(original)  # [[99, 2], [3, 4]] — original is modified!

original2 = [[1, 2], [3, 4]]
deep = copy.deepcopy(original2)  # Deep copy: everything is copied
deep[0][0] = 99
# print(original2)  # [[1, 2], [3, 4]] — original is safe


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 1 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Array = contiguous memory. O(1) access by index. O(n) insert/delete.
2. Hash Map = key→value with O(1) lookup via hash function + bucket.
3. Collisions handled by linked lists per bucket. Rare with good hash.
4. Pattern: "Seen it before?" → Hash map lookup. Turns O(n²) → O(n).
5. Pattern: "Count things" → Counter or defaultdict(int).
6. Pattern: "Group items" → defaultdict(list) with canonical key.
7. Pattern: "Top K frequent" → Counter + bucket sort (O(n)).
8. Slicing: arr[start:stop:step]. arr[::-1] reverses.
9. Use SET for O(1) membership tests (not lists).
10. Avoid modifying arrays while iterating. Use list comprehensions.

Next: Chapter 2 — Two Pointers, Sliding Window & Binary Search
""")
