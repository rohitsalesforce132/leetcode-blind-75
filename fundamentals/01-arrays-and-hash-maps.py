'''
CHAPTER 1: ARRAYS & HASH MAPS
==============================

"The two most fundamental data structures. Almost every LeetCode problem
starts with one of these."

---

PART 1: ARRAYS
==============

WHAT IS AN ARRAY?
-----------------
A real-world analogy: An array is like a ROW OF LOCKERS in a hallway.

    Locker:  [ 0 ][ 1 ][ 2 ][ 3 ][ 4 ]
    Value:   [ 10][ 25][ 37][ 48][ 50]
              ↑
           index 0

- Each "locker" (slot) stores one value.
- Each locker has a NUMBER (the INDEX) starting from 0.
- The lockers are placed right next to each other in memory.

In Python, we call arrays "lists":
'''

# --- CREATING ARRAYS ---
fruits = ["apple", "banana", "cherry", "date"]
print(fruits)          # ['apple', 'banana', 'cherry', 'date']

# --- ACCESSING BY INDEX ---
print(fruits[0])       # 'apple'  (first element, index 0)
print(fruits[3])       # 'date'   (fourth element, index 3)
print(fruits[-1])      # 'date'   (last element, Python trick: negative index)

# --- MODIFYING ---
fruits[1] = "blueberry"  # Replace index 1
print(fruits)          # ['apple', 'blueberry', 'cherry', 'date']


'''
THE KEY PROPERTY: O(1) INDEX ACCESS
------------------------------------
Because lockers are placed side-by-side in memory, if you know the index,
Python can jump directly to that locker. No matter if the array has 10 items
or 10 million items — accessing arr[5] is always instant.

This is called O(1) — constant time.

But there's a catch...

COMMON ARRAY OPERATIONS AND THEIR COST
--------------------------------------
| Operation          | Code                | Time    | Why?                              |
|--------------------|---------------------|---------|-----------------------------------|
| Access by index    | arr[3]              | O(1)    | Direct memory jump                |
| Append to end      | arr.append(x)       | O(1)*   | Just add to next slot             |
| Insert at front    | arr.insert(0, x)   | O(n)    | Must SHIFT all elements right     |
| Insert at middle   | arr.insert(i, x)   | O(n)    | Must shift elements after i       |
| Delete from front  | arr.pop(0)          | O(n)    | Must SHIFT all elements left      |
| Delete from end    | arr.pop()           | O(1)    | Just remove last slot             |
| Find an element    | arr.index(x) or `in`| O(n)    | Must check every element          |
| Get length         | len(arr)            | O(1)    | Python tracks this                |

* append is "amortized O(1)" — occasionally Python resizes the underlying
  array, but averaged over many appends it's O(1).

THE INSERT PROBLEM — VISUALIZED
--------------------------------
Why is inserting at the front O(n)?

    BEFORE: [10, 25, 37, 48, 50, __ ]
             0    1    2    3    4

    Insert 99 at index 0:
    Step 1: Shift everything RIGHT by one slot
       [10, 25, 37, 48, 50, 50]   ← 50 moves to slot 5
       [10, 25, 37, 48, 48, 50]   ← 48 moves to slot 4
       [10, 25, 37, 37, 48, 50]   ← 37 moves to slot 3
       [10, 25, 25, 37, 48, 50]   ← 25 moves to slot 2
       [10, 10, 25, 37, 48, 50]   ← 10 moves to slot 1
    Step 2: Write 99 at index 0
       [99, 10, 25, 37, 48, 50]

    Every element had to move! If there are n elements, that's n shifts → O(n).
'''

# --- DEMONSTRATION ---
arr = [10, 25, 37, 48, 50]
print("\nBefore insert:", arr)
arr.insert(0, 99)      # Insert at front — O(n) operation
print("After insert: ", arr)  # [99, 10, 25, 37, 48, 50]


'''
PART 2: HASH MAPS (PYTHON DICTIONARIES)
========================================

WHAT IS A HASH MAP?
-------------------
A real-world analogy: A hash map is like a DICTIONARY (the book kind).

In a real dictionary:
    "apple" → "A round fruit with red or green skin"
    "banana" → "A long curved yellow fruit"

You don't read every page to find "banana." You flip directly to B.

In Python, a hash map is called a "dict":
'''

# --- CREATING A HASH MAP ---
ages = {
    "Alice": 30,
    "Bob": 25,
    "Charlie": 35,
}

# --- ACCESSING BY KEY ---
print(ages["Alice"])     # 30 — instant lookup, O(1)

# --- ADDING/UPDATING ---
ages["David"] = 28       # Add new person
ages["Alice"] = 31       # Update existing
print(ages)              # {'Alice': 31, 'Bob': 25, 'Charlie': 35, 'David': 28}

# --- CHECKING IF KEY EXISTS ---
print("Bob" in ages)     # True
print("Eve" in ages)     # False

# --- DELETING ---
del ages["David"]
print(ages)              # {'Alice': 31, 'Bob': 25, 'Charlie': 35}


'''
HOW DOES A HASH MAP WORK UNDER THE HOOD?
-----------------------------------------
(This is the #1 interview question about hash maps.)

Step 1: You store a key-value pair: ages["Alice"] = 30

Step 2: Python runs "Alice" through a HASH FUNCTION.
    A hash function is like a meat grinder — you put something in,
    it produces a number out. Same input always gives same number.

    "Alice" → hash function → 34483920

Step 3: Python takes that big number and does modulo (%) by the table size.
    34483920 % 8 (if table has 8 slots) = 0
    So "Alice" goes into slot 0.

    ┌───┬───┬───┬───┬───┬───┬───┬───┐
    │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │   ← 8 slots (buckets)
    └───┴───┴───┴───┴───┴───┴───┴───┘
      ↑
    Alice: 30

Step 4: When you ask for ages["Alice"] again, same process:
    "Alice" → hash → 34483920 → % 8 → slot 0 → found! → return 30

This is why hash maps are O(1) — the hash function directly tells us
WHICH SLOT to look at. No scanning needed!

HASH COLLISIONS (What if two keys hash to the same slot?)
----------------------------------------------------------
    "Alice" → slot 0
    "Alicia" → slot 0  ← COLLISION! Same slot!

    Solution: Each slot holds a LINKED LIST of entries.
    Slot 0: [Alice:30] → [Alicia:28]

    When looking up "Alice": go to slot 0, walk the linked list,
    find "Alice". If the list is short (which it usually is with a
    good hash function + large table), this is still effectively O(1).

    In the worst case (everything collides), it degenerates to O(n),
    but this is extremely rare in practice.

HASH MAP OPERATIONS — ALL O(1)!
-------------------------------
| Operation     | Code          | Time  |
|---------------|---------------|-------|
| Get value     | dict[key]     | O(1)  |
| Set value     | dict[key] = v | O(1)  |
| Delete        | del dict[key] | O(1)  |
| Check key     | key in dict   | O(1)  |

Compare this to an array where finding an element is O(n)!
THIS is why hash maps are the most important data structure in interviews.

---

PART 3: THE #1 INTERVIEW PATTERN — "SEEN IT BEFORE"
===================================================

If you can ask "Have I seen this value before?" → use a hash map.

THE PATTERN:
    "I need to find two things that relate to each other"
    → Put the FIRST thing in a hash map as key
    → When you see the SECOND thing, look it up in the hash map

Example: Two Sum (LeetCode #1)
    "Find two numbers that add up to target."

    NAIVE: For each number, check every other number. O(n²).
    SMART: As you walk through the array, store each number in a hash map.
           For each number, check if (target - number) is in the map.

    nums = [2, 7, 11, 15], target = 9

    Step 1: See 2. Need 9-2=7. Is 7 in map? No. Store 2 → index 0.
            map = {2: 0}
    Step 2: See 7. Need 9-7=2. Is 2 in map? YES! Return [0, 1].

    O(n) time, O(n) space. One pass!
'''

# === THE TWO SUM PATTERN ===
def two_sum(nums, target):
    seen = {}  # hash map: value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:          # O(1) lookup
            return [seen[complement], i]
        seen[num] = i                   # O(1) store
    return []

print("\n--- Two Sum Demo ---")
print(two_sum([2, 7, 11, 15], 9))   # [0, 1]
print(two_sum([3, 2, 4], 6))        # [1, 2]


'''
COMMON HASH MAP PATTERNS IN INTERVIEWS
--------------------------------------
1. "Find pair / group" → hash map for O(1) lookup (Two Sum, Anagram)
2. "Count occurrences" → hash map as frequency counter
3. "Find unique/duplicates" → hash map or hash set
4. "Map one value to another" → hash map as lookup table
'''

# --- FREQUENCY COUNTER PATTERN ---
def count_characters(word):
    """Count how many times each character appears."""
    freq = {}  # hash map: char → count
    for char in word:
        if char in freq:
            freq[char] += 1
        else:
            freq[char] = 1
    return freq

print("\n--- Frequency Counter Demo ---")
print(count_characters("hello"))  # {'h': 1, 'e': 1, 'l': 2, 'o': 1}

# Python shortcut:
from collections import Counter
print(dict(Counter("hello")))      # same result


# --- HASH SET PATTERN (unique elements only, no values) ---
def has_duplicate(nums):
    """Check if any value appears twice."""
    seen = set()  # a set is a hash map with only keys, no values
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

print("\n--- Duplicate Detection Demo ---")
print(has_duplicate([1, 2, 3, 1]))      # True
print(has_duplicate([1, 2, 3, 4]))      # False


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 1 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Array  = row of lockers. O(1) access by index. O(n) insert/delete.
2. Hash Map = dictionary. O(1) get/set/lookup by KEY. THE most powerful tool.
3. Pattern: "Seen it before?" → Use a hash map.
4. Pattern: "Count things" → Hash map as frequency counter.
5. Pattern: "Find duplicates" → Hash set.

Next: Chapter 2 — Two Pointers, Sliding Window, Binary Search
""")
