'''
CHAPTER 0: BIG-O NOTATION — THE LANGUAGE OF CODE SPEED
=======================================================

"Big-O is the FIRST thing an interviewer evaluates. Before you even write
code, they're thinking: 'Does this candidate understand efficiency?'
Master Big-O and you speak the language of engineering."

---

PART 1: WHY BIG-O EXISTS — THE CORE PROBLEM
============================================

Imagine you're at a library looking for a specific book.

PERSON A's strategy: Start at shelf 1, check every book, shelf by shelf,
until you find it.
    → If the library has 1,000 books, worst case you check 1,000 books.
    → If it has 1,000,000 books, worst case you check 1,000,000 books.
    → Time grows PROPORTIONALLY with library size.

PERSON B's strategy: The books are sorted alphabetically. Open the middle
of the library. If your book comes AFTER the middle, tear off the first
half. Repeat with what's left.
    → If 1,000 books: ~10 checks (each step halves the search space).
    → If 1,000,000 books: ~20 checks.
    → Time grows LOGARITHMICALLY — barely increases even for huge inputs.

    1,000 books:       Person A = 1,000 steps.    Person B = 10 steps.
    1,000,000 books:   Person A = 1,000,000 steps. Person B = 20 steps.
    1,000,000,000:     Person A = 1,000,000,000.   Person B = 30 steps.

Person B's strategy is INSANELY faster at scale. But HOW DO WE EXPRESS
this difference precisely? That's what Big-O is for.

    Person A: O(n) — "linear time"
    Person B: O(log n) — "logarithmic time"

Big-O gives us a mathematical way to say "how does the runtime GROW
as the input gets larger?"

---

PART 2: THE FIVE BIG-O CATEGORIES YOU MUST KNOW
================================================

Think of these as SPEED TIERS. Every algorithm falls into one of these:

┌──────────┬──────────┬─────────────┬────────────────────────────────────┐
│ Big-O    │ Name     │ Example n=1M│ Analogy                            │
├──────────┼──────────┼─────────────┼────────────────────────────────────┤
│ O(1)     │ Constant │ 1           │ Looking at a clock — always        │
│          │          │             │ instant regardless of context      │
├──────────┼──────────┼─────────────┼────────────────────────────────────┤
│ O(log n) │ Logarithm│ 20          │ Finding a word in a dictionary —   │
│          │          │             │ halve the pages each time          │
├──────────┼──────────┼─────────────┼────────────────────────────────────┤
│ O(n)     │ Linear   │ 1,000,000   │ Reading every page of a book —     │
│          │          │             │ one page at a time                 │
├──────────┼──────────┼─────────────┼────────────────────────────────────┤
│ O(n²)    │ Quadratic│ 1,000,000,000,000│ Comparing every page to     │
│          │          │ (1 trillion)│ every other page                   │
├──────────┼──────────┼─────────────┼────────────────────────────────────┤
│ O(2^n)   │ Exponent.│ ∞ (impossible)│ Trying every possible combination │
│          │          │             │ of pages                           │
└──────────┴──────────┴─────────────┴────────────────────────────────────┘

THE GOLDEN RANKING (fastest to slowest):
    O(1) > O(log n) > O(n) > O(n log n) > O(n²) > O(2^n)
     ↑                                                    ↑
   FASTEST                                           SLOWEST

---

PART 3: EACH CATEGORY IN DETAIL WITH CODE
==========================================
'''

# ============================================================
# O(1) — CONSTANT TIME: "It doesn't matter how big the input is"
# ============================================================

def constant_time_example():
    """
    No matter if the array has 10 items or 10 billion items,
    this function does the SAME amount of work: one operation.

    ANALOGY: Checking your watch. It takes the same time whether
    you've been alive 10 years or 100 years. The operation is
    independent of any input size.
    """

    # --- O(1): Accessing array by index ---
    def get_first(arr):
        return arr[0]  # Direct memory address lookup. Always instant.

    # --- O(1): Hash map lookup ---
    def lookup_key(dictionary, key):
        return dictionary.get(key)  # Hash function → direct slot.

    # --- O(1): Math operations ---
    def is_even(n):
        return n % 2 == 0  # One operation regardless of n's size.

    # --- O(1): Checking the length of a Python list ---
    def get_length(arr):
        return len(arr)  # Python stores length as a property. Instant.

    # VISUALIZATION:
    # arr = [10, 25, 37, 48, 50, ... , 999999]
    # get_first(arr) → just reads memory address of arr[0]. O(1).
    #
    # Even if arr has 10 billion elements, reading arr[0] is
    # the same as reading arr[0] of a 5-element array.

    print("O(1): Always instant, regardless of input size")


# ============================================================
# O(log n) — LOGARITHMIC TIME: "Halve the problem each step"
# ============================================================

def logarithmic_time_example():
    """
    The defining characteristic: each step CUTS THE SEARCH SPACE IN HALF.

    This is why binary search is so powerful:
      1,000 items:      ~10 steps (log₂1000 ≈ 10)
      1,000,000 items:  ~20 steps (log₂1000000 ≈ 20)
      1,000,000,000:    ~30 steps (log₂1000000000 ≈ 30)

    Going from 1 million to 1 BILLION items only adds 10 more steps!

    ANALOGY: Phone book search.
    To find "Smith" in a phone book with 1 million names:
      Step 1: Open to middle (500,000th name). "Smith" is in second half.
              Tear off first half. Now 500,000 names.
      Step 2: Open to middle (250,000th). Still second half. Tear off.
              Now 250,000 names.
      Step 3: 125,000. Step 4: 62,500. Step 5: 31,250...
      Step 20: Found "Smith". Only 20 steps!

    KEY INSIGHT: "log n" means "how many times can I divide n by 2
    until I reach 1?" That's the number of steps.
    """

    # --- O(log n): Binary Search ---
    def binary_search(sorted_arr, target):
        """
        Find target in a SORTED array. Returns index or -1.

        WHY IT WORKS: The array is sorted. If target < middle,
        it MUST be in the left half. We can discard the right half.
        Each step eliminates half the remaining elements.
        """
        left = 0
        right = len(sorted_arr) - 1
        steps = 0

        while left <= right:
            steps += 1
            mid = (left + right) // 2

            if sorted_arr[mid] == target:
                print(f"  Found in {steps} steps (log₂({len(sorted_arr)}) ≈ {len(sorted_arr).bit_length()})")
                return mid
            elif sorted_arr[mid] < target:
                left = mid + 1   # Target is in RIGHT half. Discard left.
            else:
                right = mid - 1  # Target is in LEFT half. Discard right.

        return -1

    # DEMONSTRATION
    small = list(range(1, 1001))  # 1,000 sorted numbers
    large = list(range(1, 1000001))  # 1,000,000 sorted numbers

    print("Binary search on 1,000 elements:")
    binary_search(small, 742)

    print("Binary search on 1,000,000 elements:")
    binary_search(large, 742857)

    # VISUALIZATION:
    # [1, 2, 3, ..., 500000, 742857, ..., 1000000]
    #  Step 1: Check middle (500000). 742857 > 500000 → search right half
    #  Step 2: Check middle of [500001..1000000] (750000). 742857 < 750000 → left
    #  Step 3: Check middle of [500001..750000] (625000). 742857 > 625000 → right
    #  ... Step 20: Found 742857.
    #  Only 20 steps for 1 MILLION elements!


# ============================================================
# O(n) — LINEAR TIME: "Check every item, one by one"
# ============================================================

def linear_time_example():
    """
    The most common time complexity. You process EVERY element once.

    ANALOGY: Reading a book. To find a specific word, you read page by
    page. If the book has 1,000 pages, you might read up to 1,000 pages.

    If you have a SINGLE for loop that processes each element once,
    it's O(n). This is the BASELINE — the "acceptable" efficiency for
    most problems.
    """

    # --- O(n): Finding the maximum value ---
    def find_max(arr):
        max_val = arr[0]  # O(1)
        for num in arr:   # Loop runs n times
            if num > max_val:  # O(1) comparison
                max_val = num
        return max_val
    # Total: n iterations × O(1) work = O(n)

    # --- O(n): Summing an array ---
    def array_sum(arr):
        total = 0           # O(1)
        for num in arr:     # n iterations
            total += num    # O(1)
        return total
    # O(n)

    # --- O(n): Searching for a value (linear search) ---
    def linear_search(arr, target):
        for i in range(len(arr)):  # n iterations
            if arr[i] == target:
                return i
        return -1
    # O(n) — worst case: target is at the end or not present

    # VISUALIZATION:
    # arr = [10, 25, 37, 48, 50]
    # find_max:
    #   Check 10 → max=10
    #   Check 25 → max=25
    #   Check 37 → max=37
    #   Check 48 → max=48
    #   Check 50 → max=50  ← 5 checks for 5 elements. Linear.

    # --- TRICKY O(n): Two sequential loops is still O(n) ---
    def two_loops(arr):
        for x in arr:      # n iterations
            print(x)
        for y in arr:      # n iterations
            print(y)
        # Total: n + n = 2n → but we drop the constant → O(n)

    print("O(n): Process each element once. Two sequential loops = still O(n)")


# ============================================================
# O(n log n) — LINEARITHMIC TIME: "The sorting zone"
# ============================================================

def linearithmic_time_example():
    """
    This is the time complexity of EFFICIENT SORTING algorithms
    (merge sort, quicksort). It's also the theoretical BEST possible
    time for comparison-based sorting.

    ANALOGY: Sorting a deck of 52 cards.
    You compare cards and arrange them. For n cards, you need about
    n × log(n) comparisons.

    n = 1,000:       1,000 × 10 = 10,000 operations
    n = 1,000,000:   1,000,000 × 20 = 20,000,000 operations

    This is WORSE than O(n) but MUCH BETTER than O(n²).

    The most common O(n log n) operations in interviews:
      - Sorting an array: sorted(arr) or arr.sort()
      - Merge Sort algorithm
      - Quicksort (average case)
    """
    import heapq

    # --- O(n log n): Sorting ---
    arr = [5, 2, 8, 1, 9, 3, 7, 4, 6]
    arr.sort()  # Python's Timsort is O(n log n)
    print(f"Sorted: {arr}")

    # When you see sorted(arr) in your solution, you've used O(n log n).
    # This is why sorting is often a SETUP step that enables faster
    # algorithms afterward (like binary search or two pointers).

    print("O(n log n): Sorting. The best possible for comparison-based sort.")


# ============================================================
# O(n²) — QUADRATIC TIME: "Every element vs every element"
# ============================================================

def quadratic_time_example():
    """
    A nested loop (loop inside a loop) where both iterate over n items.

    ANALOGY: In a room of n people, you want to find if anyone has the
    same birthday. You ask EACH person to compare with EACH other person.
    n=10: 100 comparisons. n=100: 10,000 comparisons. n=1000: 1,000,000.

    O(n²) is a RED FLAG in interviews. If your solution is O(n²), the
    interviewer will almost always ask "Can you do better?" The answer
    is usually YES — by using a hash map (O(n)) or sorting + two pointers (O(n log n)).

    COMMON O(n²) PATTERNS (usually bad):
      - Nested for loops
      - For each element, scan the rest of the array
      - Bubble sort, insertion sort, selection sort
    """

    # --- O(n²): Find all pairs ---
    def find_pairs(arr):
        pairs = []
        for i in range(len(arr)):          # n iterations
            for j in range(i + 1, len(arr)):  # up to n iterations
                pairs.append((arr[i], arr[j]))
        return pairs
    # Inner loop runs n + (n-1) + (n-2) + ... + 1 = n(n+1)/2 → O(n²)

    # --- O(n²): Bubble Sort ---
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):              # n iterations
            for j in range(n - i - 1):  # up to n iterations
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr
    # O(n²) — two nested loops

    # VISUALIZATION OF n²:
    #     arr = [1, 2, 3, 4, 5]
    #     i=0: compare (1,2) (1,3) (1,4) (1,5)  → 4 comparisons
    #     i=1: compare (2,3) (2,4) (2,5)         → 3 comparisons
    #     i=2: compare (3,4) (3,5)               → 2 comparisons
    #     i=3: compare (4,5)                     → 1 comparison
    #     Total: 4+3+2+1 = 10 = 5×4/2 = n(n-1)/2 → O(n²)
    #
    #     For n=100: 4,950 comparisons
    #     For n=1000: 499,500 comparisons
    #     For n=1,000,000: 499,999,500,000 comparisons ← VERY SLOW

    print("O(n²): Nested loops. Usually a sign you need a better algorithm.")


# ============================================================
# O(2^n) — EXPONENTIAL TIME: "Every additional element DOUBLES the work"
# ============================================================

def exponential_time_example():
    """
    Each additional input element DOUBLES the runtime.

    n = 10:  ~1,024 operations
    n = 20:  ~1,048,576 operations
    n = 30:  ~1,073,741,824 operations (over 1 BILLION)
    n = 50:  ~1,125,899,906,842,624 (impossible)

    ANALOGY: You have n friends. How many possible groups can you form?
    Each friend can be IN or OUT (2 choices per friend).
    Total groups = 2^n. For 30 friends: over 1 billion groups.

    O(2^n) solutions come from:
      - Naive recursion without memoization (e.g., Fibonacci)
      - Generating all subsets of a set
      - Backtracking without pruning

    In interviews, O(2^n) is only acceptable if the problem REQUIRES it
    (like generating all subsets — you can't do better because the OUTPUT
    itself is 2^n items).
    """

    # --- O(2^n): Naive Fibonacci ---
    def fib_naive(n):
        if n <= 1:
            return n
        return fib_naive(n - 1) + fib_naive(n - 2)
    # Each call makes 2 more calls. This creates a binary tree of calls.
    #
    #                      fib(5)
    #                    /        \
    #                fib(4)       fib(3)
    #               /     \       /     \
    #           fib(3)  fib(2)  fib(2) fib(1)
    #           /    \   /   \   /   \
    #       fib(2) fib(1) ...  ...
    #
    # Notice: fib(3) is computed TWICE. fib(2) is computed THREE times.
    # This redundant computation is why it's exponential.

    print(f"fib(10) = {fib_naive(10)}")   # 55
    print(f"fib(20) = {fib_naive(20)}")   # 6765
    # fib(40) would take ~30 seconds. fib(50) would take hours.

    print("O(2^n): Exponential. Every additional element doubles work. AVOID.")


# ============================================================
# COMPARISON TABLE
# ============================================================

def comparison_table():
    """
    HOW FAST EACH COMPLEXITY IS FOR DIFFERENT INPUT SIZES:

    n              O(1)    O(log n)    O(n)        O(n log n)      O(n²)                O(2^n)
    ─────────────────────────────────────────────────────────────────────────────────────────────
    10             1       3           10          30              100                  1,024
    100            1       7           100         700             10,000               10³⁰
    1,000          1       10          1,000       10,000          1,000,000            ∞
    10,000         1       13          10,000      130,000         100,000,000          ∞
    100,000        1       17          100,000     1,700,000       10,000,000,000       ∞
    1,000,000      1       20          1,000,000   20,000,000      1,000,000,000,000   ∞
    10,000,000     1       23          10,000,000  230,000,000     100,000,000,000,000 ∞

    KEY OBSERVATIONS:
    1. O(1) and O(log n) are basically INSTANT for any input size.
    2. O(n) scales linearly — 10 million items takes 10 million operations.
    3. O(n log n) is slightly worse than O(n) but still very usable.
    4. O(n²) becomes unusable around n=10,000 (100 billion operations).
    5. O(2^n) is unusable for n > 25.

    INTERVIEW THRESHOLDS (rules of thumb):
    - LeetCode constraints say n ≤ 10:   O(n!) or O(2^n) is fine (backtracking)
    - LeetCode constraints say n ≤ 100:  O(n³) is acceptable
    - LeetCode constraints say n ≤ 1000: O(n²) is acceptable
    - LeetCode constraints say n ≤ 10⁵:  You need O(n log n) or O(n)
    - LeetCode constraints say n ≤ 10⁶:  You need O(n) or O(log n)
    - LeetCode constraints say n ≤ 10⁹:  You need O(log n) or O(1)
    """
    pass


# ============================================================
# PART 4: SPACE COMPLEXITY
# ============================================================

def space_complexity():
    """
    Big-O doesn't just describe TIME — it also describes MEMORY/SPACE.

    Time complexity:  How much TIME does the algorithm use as n grows?
    Space complexity: How much MEMORY does the algorithm use as n grows?

    ANALOGY:
      Time:  How long it takes to organize your books.
      Space: How many boxes you need to organize them.

    COMMON SPACE COMPLEXITIES:

    O(1) Space (constant):
      You use a fixed number of variables, regardless of input size.

      def find_max(arr):
          max_val = arr[0]   # One variable. O(1) space.
          for num in arr:
              if num > max_val:
                  max_val = num
          return max_val
      # Even if arr has 1 million items, we only use 1 variable (max_val).

    O(n) Space (linear):
      You create a new data structure proportional to input size.

      def copy_array(arr):
          new_arr = []          # New array of size n
          for item in arr:
              new_arr.append(item)
          return new_arr
      # If arr has 1 million items, new_arr also has 1 million items. O(n) space.

    O(n) Space (from hash map):
      def count_frequency(arr):
          freq = {}             # Hash map with up to n entries
          for item in arr:
              freq[item] = freq.get(item, 0) + 1
          return freq
      # In the worst case (all unique items), freq has n entries. O(n) space.

    THE TIME-SPACE TRADEOFF:
      Often you can trade SPACE for TIME (or vice versa).

      Example: "Find if array has duplicates"
        O(n²) time, O(1) space: Compare every pair (nested loop)
        O(n) time, O(n) space: Use a hash set to track seen items

      The hash set approach is 100× faster but uses n extra memory.
      In interviews, the O(n) time + O(n) space solution is almost always
      preferred over O(n²) time + O(1) space.
    """
    pass


# ============================================================
# PART 5: THE FOUR RULES OF DETERMINING BIG-O
# ============================================================

def big_o_rules():
    """
    RULE 1: DROP CONSTANTS
    ─────────────────────
    O(2n) → O(n). O(500) → O(1). O(3n²) → O(n²).

    Why? Big-O describes the GROWTH RATE, not the exact count.
    As n → infinity, the constant multiplier doesn't matter.
    2n and 100n both grow LINEARLY.
    """

    def rule1_example(arr):
        # This is O(2n) but we simplify to O(n)
        count = 0
        for x in arr:        # n iterations
            count += 1
        for y in arr:        # n iterations
            count += 1
        return count
    # O(2n) → O(n)

    """
    RULE 2: DROP LOWER-ORDER TERMS
    ──────────────────────────────
    O(n² + n) → O(n²). O(n + log n) → O(n). O(n² + n log n + n) → O(n²).

    Why? As n → infinity, the higher-order term DOMINATES.
    For n = 1,000,000: n² = 10¹² but n = 10⁶.
    The n² term is a MILLION TIMES larger than n. So n is irrelevant.
    """

    def rule2_example(arr):
        # This is O(n² + n) but we simplify to O(n²)
        n = len(arr)
        for i in range(n):          # n² part
            for j in range(n):
                print(arr[i], arr[j])
        for k in range(n):          # n part (lower order)
            print(arr[k])
    # O(n² + n) → O(n²)

    """
    RULE 3: DIFFERENT INPUTS → DIFFERENT VARIABLES
    ──────────────────────────────────────────────
    If you have two different arrays of different sizes, use two variables.
    Don't use n for both. This is a COMMON MISTAKE.
    """

    def rule3_example(arr_a, arr_b):
        # This is NOT O(n²). It's O(a × b) where a = len(arr_a), b = len(arr_b).
        for a in arr_a:          # a iterations (arr_a's size)
            for b in arr_b:      # b iterations (arr_b's size)
                print(a, b)
    # If arr_a and arr_b are DIFFERENT sizes, this is O(a × b), NOT O(n²).
    # Only call it O(n²) if both arrays are guaranteed to be the same size.

    """
    RULE 4: LOOP WITH HALVING IS O(log n)
    ──────────────────────────────────────
    Any loop that HALVES the search space each iteration is O(log n),
    regardless of the total input size.
    """

    def rule4_example(n):
        # This is O(log n), NOT O(n)
        steps = 0
        while n > 1:
            n = n // 2    # Halve n each time
            steps += 1
        return steps
    # log₂(1,000,000) = ~20 steps. O(log n).


# ============================================================
# PART 6: PRACTICE EXERCISES (Test Yourself)
# ============================================================

def practice_exercises():
    """
    Determine the Big-O time complexity for each function.
    Answers are in the comments below each function.
    """

    # --- Exercise 1 ---
    def exercise_1(arr):
        total = 0                    # O(1)
        for i in range(len(arr)):    # n iterations
            total += arr[i]          # O(1)
        return total
    # ANSWER: O(n) — single loop, each iteration is O(1)

    # --- Exercise 2 ---
    def exercise_2(arr):
        result = []
        for i in range(len(arr)):           # n iterations
            for j in range(len(arr)):       # n iterations
                if arr[i] < arr[j]:
                    result.append((i, j))
        return result
    # ANSWER: O(n²) — nested loop, both iterate over the same array

    # --- Exercise 3 ---
    def exercise_3(arr, target):
        left, right = 0, len(arr) - 1
        while left <= right:               # Halves each iteration
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return -1
    # ANSWER: O(log n) — binary search, halves the search space each step

    # --- Exercise 4 ---
    def exercise_4(n):
        if n <= 1:
            return n
        return exercise_4(n - 1) + exercise_4(n - 2)
    # ANSWER: O(2^n) — each call makes 2 more calls. Binary recursion tree.

    # --- Exercise 5 ---
    def exercise_5(arr):
        freq = {}                            # O(n) space
        for item in arr:                     # n iterations
            freq[item] = freq.get(item, 0) + 1
        max_count = 0
        for key, value in freq.items():      # up to n iterations
            max_count = max(max_count, value)
        return max_count
    # ANSWER: O(n) time — two sequential loops (n + n = 2n → O(n))
    #         O(n) space — hash map with up to n entries

    # --- Exercise 6 (TRICKY) ---
    def exercise_6(n):
        count = 0
        for i in range(n):         # n iterations
            j = 1
            while j < n:           # This inner loop is O(log n)!
                j *= 2             # j DOUBLES each time
                count += 1
        return count
    # ANSWER: O(n log n) — outer loop is n, inner loop is log n. n × log n.

    # --- Exercise 7 (TRICKY) ---
    def exercise_7(arr):
        arr.sort()                 # O(n log n)
        for i in range(len(arr)):  # O(n)
            print(arr[i])
        return arr
    # ANSWER: O(n log n) — sorting dominates. n log n + n → O(n log n).
    # (The sorting is the bottleneck, so the linear scan doesn't matter.)

    # --- Exercise 8 (VERY TRICKY) ---
    def exercise_8(n):
        result = 0
        for i in range(1, n + 1):  # n iterations
            for j in range(1, i + 1):  # i iterations (NOT n!)
                result += 1
        return result
    # ANSWER: O(n²) — inner loop runs 1 + 2 + 3 + ... + n = n(n+1)/2 times.
    # Even though inner loop doesn't always run n times, the TOTAL is n²/2 → O(n²).


# ============================================================
# PART 7: BIG-O IN INTERVIEWS — HOW TO TALK ABOUT IT
# ============================================================

def interview_big_o():
    """
    In an interview, you must STATE the time and space complexity of your
    solution. Here's the exact format to use:

    FORMAT:
      "This solution runs in O(?) time and O(?) space.
       The time complexity is O(?) because [REASON].
       The space complexity is O(?) because [REASON]."

    EXAMPLE 1 (Hash Map solution):
      "This runs in O(n) time and O(n) space.
       Time is O(n) because we iterate through the array once, and each
       hash map operation is O(1).
       Space is O(n) because in the worst case, we store all n elements
       in the hash map."

    EXAMPLE 2 (Binary search solution):
      "This runs in O(log n) time and O(1) space.
       Time is O(log n) because we halve the search space each iteration.
       Space is O(1) because we only use three variables: left, right, mid."

    EXAMPLE 3 (Sorting + two pointers):
      "This runs in O(n log n) time and O(1) or O(n) space.
       Time is O(n log n) because sorting dominates (the two-pointer scan
       afterward is only O(n)).
       Space depends on the sort implementation — O(1) for in-place sort,
       O(n) if sorting creates a copy."

    COMMON INTERVIEWER FOLLOW-UPS:
      "Can you do better?"
        → They want a lower Big-O. Think: hash map, binary search, two pointers.

      "What if the input is already sorted?"
        → You might skip the sorting step, making it O(n) instead of O(n log n).

      "What about space?"
        → They want the space complexity. Don't forget to mention it!

      "What's the worst case?"
        → Big-O IS the worst case (technically Big-O is an upper bound).
          Make sure you're considering the worst case, not best case.
    """
    pass


# ============================================================
# PART 8: THE MASTER CHEAT SHEET
# ============================================================

def master_cheat_sheet():
    """
    ┌──────────────────────────────────────────────────────────────────┐
    │              BIG-O COMPLEXITY CHEAT SHEET                         │
    ├──────────────┬──────────┬───────────────────────────────────────┤
    │ Data Structure│ Access   │ Search   │ Insert   │ Delete          │
    ├──────────────┼──────────┼──────────┼──────────┼─────────────────┤
    │ Array        │ O(1)     │ O(n)     │ O(n)     │ O(n)            │
    │ Hash Map     │ N/A      │ O(1)     │ O(1)     │ O(1)            │
    │ Linked List  │ O(n)     │ O(n)     │ O(1)*    │ O(1)*           │
    │ BST (balanced)│ O(log n)│ O(log n) │ O(log n) │ O(log n)        │
    │ Heap         │ O(1)**   │ O(n)     │ O(log n) │ O(log n)        │
    │ Stack        │ O(1)***  │ O(n)     │ O(1)     │ O(1)            │
    │ Queue        │ O(1)***  │ O(n)     │ O(1)     │ O(1)            │
    ├──────────────┴──────────┴──────────┴──────────┴─────────────────┤
    │ * At known position (head). ** Peek at root only.               │
    │ *** Top/front only.                                             │
    ├─────────────────────────────────────────────────────────────────┤
    │ Algorithm          │ Time         │ Space  │ Notes               │
    ├─────────────────────┼──────────────┼────────┼─────────────────────┤
    │ Binary Search      │ O(log n)     │ O(1)   │ Requires sorted     │
    │ Linear Search      │ O(n)         │ O(1)   │ Works on unsorted   │
    │ Merge Sort         │ O(n log n)   │ O(n)   │ Stable sort         │
    │ Quicksort          │ O(n log n)*  │ O(log n)│ In-place. *Avg case │
    │ BFS / DFS          │ O(V + E)     │ O(V)   │ Graph traversal     │
    │ Backtracking       │ O(2^n) / O(n!)│ O(n)  │ Depends on problem  │
    │ DP (tabulation)    │ O(n) to O(n²)│ O(n)   │ Problem-dependent   │
    └─────────────────────┴──────────────┴────────┴─────────────────────┘

    THE "WHAT COMPLEXITY DO I NEED?" GUIDE (based on n constraints):
      n ≤ 10      → O(n!) or O(2^n) is fine
      n ≤ 100     → O(n³) acceptable
      n ≤ 1,000   → O(n²) acceptable
      n ≤ 100,000 → Need O(n log n) or O(n)
      n ≤ 1,000,000 → Need O(n) or O(log n)
      n > 10⁹     → Need O(log n) or O(1)
    """
    pass


# === VERIFY ===
if __name__ == "__main__":
    print("=" * 60)
    print("CHAPTER 0: BIG-O NOTATION — COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Big-O describes HOW runtime grows as input size increases.
2. O(1) > O(log n) > O(n) > O(n log n) > O(n²) > O(2^n).
3. Drop constants: O(2n) = O(n). Drop lower terms: O(n² + n) = O(n²).
4. Loop over n → O(n). Nested loop → O(n²). Halving loop → O(log n).
5. Sorting is O(n log n). Hash map ops are O(1).
6. Space complexity: how much EXTRA memory your code uses.
7. Time-space tradeoff: often trade O(n²) time + O(1) space
   for O(n) time + O(n) space.
8. ALWAYS state both time AND space complexity in interviews.

Next: Chapter 1 — Arrays & Hash Maps (the foundation of everything)
""")
