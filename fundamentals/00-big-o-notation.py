'''
CHAPTER 0: BIG-O NOTATION — HOW FAST IS YOUR CODE?
===================================================

"Before you learn data structures, you need to know how to TALK about
how fast or slow your code is. Big-O is that language."

---

WHY DO WE NEED BIG-O?
---------------------
Imagine two people write code to find a number in a list:

    # Person A: checks every number one by one
    def find_a(numbers, target):
        for n in numbers:
            if n == target:
                return True
        return False

    # Person B: checks the middle, eliminates half (only works on sorted lists)
    def find_b(numbers, target):
        lo, hi = 0, len(numbers) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if numbers[mid] == target:
                return True
            elif numbers[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return False

Which is faster? Person B — but by HOW MUCH?

If the list has 1,000,000 numbers:
    Person A: up to 1,000,000 checks
    Person B: at most ~20 checks (cuts in half each time)

Big-O gives us a precise way to say this:
    Person A: O(n)  — "linear time" — grows proportionally with input size
    Person B: O(log n) — "logarithmic time" — grows VERY slowly

---

THE ANALOGY: LOOKING FOR A NAME IN A PHONE BOOK
-----------------------------------------------
Imagine finding "Smith" in a phone book with 1,000,000 names.

O(1) — CONSTANT TIME:
    You already know the page number. You flip to it directly.
    It doesn't matter if the book has 100 pages or 1,000,000 pages.
    Same speed. Examples: array index lookup, hash map lookup.

O(log n) — LOGARITHMIC TIME:
    You open to the MIDDLE of the book. "Smith" is in the second half.
    You tear off the first half. Repeat: open middle of remaining half.
    Each step eliminates HALF the book.
    For 1,000,000 names: about 20 steps. Examples: binary search.

O(n) — LINEAR TIME:
    You read every single name from page 1 until you find "Smith."
    For 1,000,000 names: up to 1,000,000 steps. Examples: for loop over array.

O(n log n) — LINEARITHMIC TIME:
    You sort the phone book. Then binary search it.
    Examples: merge sort, quicksort. This is the best possible for sorting.

O(n^2) — QUADRATIC TIME:
    For every name, you compare it against every other name.
    1,000,000 names = 1,000,000,000,000 comparisons. BAD.
    Examples: nested for loops (loop inside a loop).

O(2^n) — EXPONENTIAL TIME:
    For every additional name added to the book, the work DOUBLES.
    20 names = ~1,000,000 steps. 30 names = ~1,000,000,000 steps.
    Examples: generating all subsets, naive recursive Fibonacci.

---

VISUAL COMPARISON: HOW FAST DOES EACH GROW?
-------------------------------------------
(Imagine n = input size, like how many items are in a list)

    n = 10         n = 100        n = 1,000      n = 1,000,000
    ─────────────────────────────────────────────────────────────
    O(1):     1          1              1              1           ← Always instant
    O(log n): 3          6              10             20          ← Barely grows
    O(n):     10         100            1,000          1,000,000   ← Proportional
    O(n²):    100        10,000         1,000,000      10^12       ← Exploding
    O(2^n):   1,024      10^30          ∞              ∞           ← Unusable


    SPEED (best to worst):  O(1) > O(log n) > O(n) > O(n log n) > O(n²) > O(2^n)

---

SPACE COMPLEXITY (MEMORY)
-------------------------
Big-O also describes how much MEMORY your code uses, not just time.

    O(1) space: You use a fixed number of variables, regardless of input size.
                Example: finding max in an array (one variable `max_val`).

    O(n) space: You create a new array/dict of size proportional to input.
                Example: creating a copy of the input array.

    O(n²) space: You create an n×n grid. Example: adjacency matrix for a graph.

---

HOW TO FIGURE OUT BIG-O OF YOUR CODE (3 RULES)
----------------------------------------------
Rule 1: A simple for loop over n items → O(n)

    for i in range(n):     # runs n times
        print(i)           # O(1) each time
    # Total: O(n)

Rule 2: A nested for loop (loop inside a loop) → O(n²)

    for i in range(n):         # runs n times
        for j in range(n):     # each time, runs n more times
            print(i, j)        # n × n = n²
    # Total: O(n²)

Rule 3: Cutting the search space in half each step → O(log n)

    while lo <= hi:
        mid = (lo + hi) // 2    # check middle
        if target < mid:
            hi = mid - 1        # eliminate right half
        else:
            lo = mid + 1        # eliminate left half
    # Total: O(log n)

---

THE GOLDEN RULE OF BIG-O
------------------------
"Big-O tells you what happens when n gets VERY large."
- We ignore constants: O(2n) is just O(n). O(100) is just O(1).
- We ignore lower-order terms: O(n² + n) is just O(n²).
- We care about the WORST CASE (unless stated otherwise).

In an interview, always state:
1. Time complexity: "This runs in O(n) time because we loop through the array once."
2. Space complexity: "This uses O(n) space because we store a hash map of all elements."

---

PRACTICE: WHAT'S THE BIG-O?
---------------------------
'''

# ========== PRACTICE EXERCISES ==========

# --- Exercise 1 ---
def exercise_1(n):
    """What is the time complexity?"""
    total = 0                          # O(1)
    for i in range(n):                 # loop n times
        total += i                     # O(1) each time
    return total
# ANSWER: O(n) — single loop over n items


# --- Exercise 2 ---
def exercise_2(n):
    """What is the time complexity?"""
    total = 0                          # O(1)
    for i in range(n):                 # outer loop: n times
        for j in range(n):             # inner loop: n times each
            total += i * j             # O(1)
    return total
# ANSWER: O(n²) — nested loop


# --- Exercise 3 ---
def exercise_3(n):
    """What is the time complexity?"""
    result = []                        # O(1)
    for i in range(n):                 # loop n times
        result.append(i * 2)           # O(1) amortized
    return result
# ANSWER: O(n) — single loop. Space is also O(n) for the result list.


# --- Exercise 4 ---
def exercise_4(n):
    """What is the time complexity?"""
    if n <= 1:
        return 1
    return exercise_4(n - 1) + exercise_4(n - 1)
# ANSWER: O(2^n) — each call makes 2 more calls, doubling each time


# --- Exercise 5 ---
def exercise_5(sorted_arr, target):
    """What is the time complexity?"""
    lo, hi = 0, len(sorted_arr) - 1
    while lo <= hi:                     # cuts in half each time
        mid = (lo + hi) // 2
        if sorted_arr[mid] == target:
            return mid
        elif sorted_arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
# ANSWER: O(log n) — binary search, halves each time


# --- VERIFY ALL EXERCISES ---
if __name__ == "__main__":
    print("=" * 60)
    print("CHAPTER 0: BIG-O NOTATION — VERIFICATION")
    print("=" * 60)

    print("\n1. exercise_1(10) =", exercise_1(10), "→ O(n)")
    print("2. exercise_2(10) =", exercise_2(10), "→ O(n²)")
    print("3. exercise_3(5)  =", exercise_3(5),  "→ O(n)")
    print("4. exercise_4(5)  =", exercise_4(5),  "→ O(2^n) — grows FAST")
    print("5. exercise_5([1,3,5,7,9,11], 7) =", exercise_5([1,3,5,7,9,11], 7), "→ O(log n)")

    print("\n✅ Chapter 0 complete! Now you can talk about code speed.")
    print("   Next: Chapter 1 — Arrays & Hash Maps")
