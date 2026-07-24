'''
CHAPTER 2: TWO POINTERS, SLIDING WINDOW & BINARY SEARCH
========================================================

"Three powerful patterns that work on arrays and strings.
Master these and you can solve 20+ LeetCode problems instantly."

---

PART 1: TWO POINTERS
=====================

WHAT IS IT?
-----------
Instead of using one index to scan an array, you use TWO indexes
("pointers") that move through the array in a coordinated way.

A real-world analogy: Imagine squeezing a sponge from both ends.
    Left hand moves right →, left hand moves left ←
    You're narrowing down from both sides.

PATTERN 1: OPPOSITE-ENDS (Left & Right pointers moving inward)
--------------------------------------------------------------
Use when: The array is SORTED, or you need to compare elements from
both ends.

    arr = [1, 3, 5, 7, 9, 11]
           ↑              ↑
          left           right

    left starts at 0, right starts at len-1.
    They move toward each other.
'''

# --- EXAMPLE: TWO SUM II (sorted array) ---
# "Find two numbers in a SORTED array that add up to target."
def two_sum_sorted(arr, target):
    left = 0
    right = len(arr) - 1

    while left < right:
        current_sum = arr[left] + arr[right]

        if current_sum == target:
            return [left, right]       # Found it!
        elif current_sum < target:
            left += 1                  # Sum too small → need bigger number → move left right
        else:
            right -= 1                 # Sum too big → need smaller number → move right left

    return []

print("--- Two Pointers: Two Sum II ---")
print(two_sum_sorted([1, 3, 5, 7, 9, 11], 14))  # [1, 5] → arr[1]=3 + arr[5]=11 = 14


'''
WHY DOES THIS WORK?
    arr = [1, 3, 5, 7, 9, 11], target = 14

    Step 1: left=0(arr[0]=1), right=5(arr[5]=11). Sum=12. 12 < 14 → move left up.
    Step 2: left=1(arr[1]=3), right=5(arr[5]=11). Sum=14. 14 == 14 → DONE!

    Because the array is sorted, moving left always increases the sum,
    and moving right always decreases it. This guides us to the answer.

PATTERN 2: SAME-DIRECTION (Fast & Slow pointers)
------------------------------------------------
Use when: You need to process elements in-place, detect cycles, or
remove duplicates from a sorted array.

    slow
     ↓
    [1, 1, 2, 3, 3, 4]
     ↑
    fast

    slow tracks where to write the next unique element.
    fast scans ahead looking for new unique elements.
'''

# --- EXAMPLE: REMOVE DUPLICATES FROM SORTED ARRAY ---
def remove_duplicates(arr):
    if not arr:
        return 0

    slow = 0  # Points to the last unique element

    for fast in range(1, len(arr)):
        if arr[fast] != arr[slow]:   # Found a new unique element
            slow += 1                # Move slow forward
            arr[slow] = arr[fast]    # Write unique element

    return slow + 1  # Number of unique elements

print("\n--- Two Pointers: Remove Duplicates ---")
arr = [1, 1, 2, 3, 3, 3, 4, 5, 5]
count = remove_duplicates(arr)
print(f"{count} unique elements: {arr[:count]}")  # 5 unique: [1, 2, 3, 4, 5]


# --- EXAMPLE: PALINDROME CHECK ---
def is_palindrome(s):
    """Check if a string reads the same forwards and backwards."""
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

print("\n--- Two Pointers: Palindrome ---")
print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False


'''
TWO POINTERS SUMMARY:
    - Opposite ends → sorted arrays, palindromes, container problems
    - Same direction → remove duplicates, cycle detection
    - Time: O(n) — each element visited at most once
    - Space: O(1) — just two pointer variables


PART 2: SLIDING WINDOW
======================

WHAT IS IT?
-----------
A "window" is a sub-array (contiguous chunk) that slides across the array.
Think of it like a magnifying glass sliding across a document — you only
look at what's under the glass, then slide it one step at a time.

WHY NOT JUST USE NESTED LOOPS?
    Brute force: try every possible sub-array → O(n²) or O(n³)
    Sliding window: maintain a running sum/count → O(n)!

PATTERN 1: FIXED-SIZE WINDOW
-----------------------------
"The window is always exactly K elements wide."

    arr = [1, 3, 5, 7, 9, 2, 4], k = 3

    Window [1, 3, 5]     → sum = 9
    Slide → [3, 5, 7]    → sum = 15  (added 7, removed 1)
    Slide → [5, 7, 9]    → sum = 21  (added 9, removed 3)
    Slide → [7, 9, 2]    → sum = 18  (added 2, removed 5)
    Slide → [9, 2, 4]    → sum = 15  (added 4, removed 7)

    Maximum sum = 21!

Key trick: When the window slides, you DON'T recalculate the sum from scratch.
You ADD the new element entering the window and SUBTRACT the old element leaving.
This is why it's O(n) instead of O(n*k).
'''

# --- EXAMPLE: MAX SUM SUBARRAY OF SIZE K ---
def max_sum_subarray(arr, k):
    if len(arr) < k:
        return 0

    # Compute sum of first window
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # Slide the window
    for i in range(k, len(arr)):
        # Add new element (entering window), subtract old element (leaving window)
        window_sum += arr[i] - arr[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum

print("\n--- Sliding Window: Fixed Size ---")
print(max_sum_subarray([1, 3, 5, 7, 9, 2, 4], 3))  # 21


'''
PATTERN 2: DYNAMIC WINDOW (grow and shrink)
--------------------------------------------
"The window grows when conditions are good, shrinks when they're violated."

This is used when you're looking for the LONGEST or SHORTEST subarray
that satisfies some condition.

    arr = [1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1], flip at most k=2 zeros

    Goal: Find longest subarray with at most k zeros (can flip 2 zeros to 1s).

    Window grows right. When zeros in window > k, shrink from left.
'''

# --- EXAMPLE: LONGEST SUBSTRING WITHOUT REPEATING CHARACTERS ---
def longest_unique_substring(s):
    """
    Find the length of the longest substring without repeating characters.
    "abcabcbb" → 3 ("abc")
    """
    char_index = {}  # Last seen position of each character
    left = 0         # Left edge of window
    max_len = 0

    for right in range(len(s)):
        char = s[right]

        # If we've seen this char AND it's inside our current window → shrink
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1  # Jump left past the duplicate

        char_index[char] = right          # Update last seen position
        max_len = max(max_len, right - left + 1)

    return max_len

print("\n--- Sliding Window: Dynamic ---")
print(longest_unique_substring("abcabcbb"))  # 3
print(longest_unique_substring("bbbbb"))     # 1
print(longest_unique_substring("pwwkew"))    # 3


'''
SLIDING WINDOW SUMMARY:
    - Fixed size: window always K wide. Add new, subtract old. O(n).
    - Dynamic size: window grows right, shrinks left when condition breaks. O(n).
    - Key insight: NEVER recalculate from scratch. Maintain running state.
    - Time: O(n) — each element enters and leaves the window at most once
    - Space: O(k) for tracking window contents (hash map or set)


PART 3: BINARY SEARCH
======================

WHAT IS IT?
-----------
A way to find an element in a SORTED array in O(log n) time by repeatedly
cutting the search space in half.

Real-world analogy: Finding a word in a dictionary.
    You don't read page 1, page 2, page 3...
    You open to the MIDDLE. If your word is earlier, tear off the back half.
    Repeat with the remaining half. Each step eliminates half the book.

THE ALGORITHM (MEMORIZE THIS)
'''

def binary_search(arr, target):
    """
    Find target in a sorted array.
    Returns the index if found, -1 if not found.
    """
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2  # Look at the middle

        if arr[mid] == target:
            return mid             # Found it!
        elif arr[mid] < target:
            left = mid + 1         # Target is in the RIGHT half → discard left
        else:
            right = mid - 1        # Target is in the LEFT half → discard right

    return -1  # Not found

print("\n--- Binary Search ---")
arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
print(binary_search(arr, 7))    # 3 (index of 7)
print(binary_search(arr, 6))    # -1 (not found)
print(binary_search(arr, 19))   # 9 (last element)
print(binary_search(arr, 1))    # 0 (first element)


'''
DRY RUN: Searching for 7 in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

    Step 1: left=0, right=9. mid=4. arr[4]=9. 9 > 7 → search LEFT half.
            right = 3
            [1, 3, 5, 7]  9  11  13  15  17  19
             ↑     ↑
           left  right

    Step 2: left=0, right=3. mid=1. arr[1]=3. 3 < 7 → search RIGHT half.
            left = 2
            [1, 3] 5, 7  9  11  13  15  17  19
                  ↑  ↑
               left  right

    Step 3: left=2, right=3. mid=2. arr[2]=5. 5 < 7 → search RIGHT half.
            left = 3
            ... 5, [7] 9  11  13  15  17  19
                  ↑   ↑
               left  right
                     mid

    Step 4: left=3, right=3. mid=3. arr[3]=7. 7 == 7 → FOUND! Return 3.

    4 steps for 10 elements. For 1,000,000 elements: only ~20 steps!

WHY IS IT O(log n)?
    Each step halves the search space:
    n → n/2 → n/4 → n/8 → ... → 1
    How many times can you halve n until you get to 1? Answer: log₂(n).
    log₂(1,000,000) ≈ 20.

THE BINARY SEARCH TEMPLATE (for harder problems)
-------------------------------------------------
Many LeetCode problems are "binary search on the answer."
The pattern:

    "Find the minimum X such that condition(X) is true."
    (where condition is monotonic — once it's true for X, it's true for all larger X)

    - If condition(mid) is true → try smaller: right = mid
    - If condition(mid) is false → try bigger: left = mid + 1

This applies to problems like Koko Eating Bananas, Split Array Largest Sum, etc.

BINARY SEARCH REQUIREMENTS:
    1. The array MUST be sorted (or the search space must be monotonic)
    2. You must be able to eliminate half the space with each check
    3. Time: O(log n) — incredibly fast
    4. Space: O(1) — just left, right, mid variables

COMMON MISTAKES IN BINARY SEARCH:
    1. `left < right` vs `left <= right` — depends on the problem
    2. `right = mid` vs `right = mid - 1` — depends on whether mid could be the answer
    3. Integer overflow in other languages: use `left + (right - left) // 2`
'''

# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 2 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Two Pointers: Two indices moving coordinately. O(n), O(1) space.
   - Opposite ends: sorted arrays, palindromes
   - Same direction: duplicates, cycle detection
2. Sliding Window: Sub-array that slides across. O(n), avoids nested loops.
   - Fixed size: add new element, subtract old
   - Dynamic: grow right, shrink left
3. Binary Search: Find element in sorted array. O(log n).
   - Cut search space in half each step
   - Requires sorted input
   - Template: "min X where condition(X) is true"

Next: Chapter 3 — Stacks, Queues & Linked Lists
""")
