'''
CHAPTER 2: TWO POINTERS, SLIDING WINDOW & BINARY SEARCH
========================================================

"Three powerful patterns that work on arrays and strings.
Master these and you can solve 20+ LeetCode problems instantly."

CHAPTER ROADMAP:
    PART 1: TWO POINTERS        (opposite-ends, fast/slow, Floyd's cycle)
    PART 2: SLIDING WINDOW      (fixed-size, dynamic, templates)
    PART 3: BINARY SEARCH       (classic, boundaries, answer-space)

Each part follows the same teaching order:
    1. Analogy  →  2. Diagram  →  3. Code  →  4. Dry run  →  5. Why/Proof
========================================================================


PART 1: TWO POINTERS
=====================

WHAT IS IT?
-----------
Instead of using one index to scan an array, you use TWO indexes
("pointers") that move through the array in a coordinated way.

A real-world analogy: Imagine squeezing a sponge from both ends.
    Left hand moves right →, right hand moves left ←
    You're narrowing down from both sides.

Another analogy: two people walking toward each other on a bridge.
They start at opposite ends and meet in the middle. Each step one of
them takes narrows the gap between them.

WHY TWO POINTERS BEATS BRUTE FORCE:
    Brute force two-sum uses nested loops:
        for i in range(n):           # O(n)
            for j in range(n):       # O(n)   →  total O(n²)
    Two pointers uses a single pass with two movers → O(n).
    The trick: we never need to "go back." Each pointer only moves
    forward, so we do at most 2n moves total.

TWO MAIN FLAVORS:
    A) Opposite-ends:  left at start, right at end, move inward
    B) Same-direction: both start at index 0, one runs ahead (fast/slow)


PATTERN 1A: OPPOSITE-ENDS (Left & Right pointers moving inward)
---------------------------------------------------------------
Use when: The array is SORTED, or you need to compare elements from
both ends.

    arr = [1, 3, 5, 7, 9, 11]
           ↑              ↑
          left           right

    left starts at 0, right starts at len-1.
    They move toward each other.

    Visual of the squeeze:

      Start:   [1, 3, 5, 7, 9, 11]
                ↑              ↑
               L              R

      Step 1:  [1, 3, 5, 7, 9, 11]
                     ↑     ↑
                     L     R

      Step 2:  [1, 3, 5, 7, 9, 11]
                        ↑↑
                        LR   ← they meet → loop ends
'''

# --- EXAMPLE: TWO SUM II (sorted array) ---
# "Find two numbers in a SORTED array that add up to target."
def two_sum_sorted(arr, target):
    left = 0
    right = len(arr) - 1

    while left < right:                         # stop when pointers cross
        current_sum = arr[left] + arr[right]    # evaluate the pair under pointers

        if current_sum == target:
            return [left, right]                # exact match → done
        elif current_sum < target:
            left += 1                           # sum too small → need a bigger number
                                                # bigger number lives to the RIGHT of left
        else:
            right -= 1                          # sum too big → need a smaller number
                                                # smaller number lives to the LEFT of right

    return []                                   # no valid pair exists


print("--- Two Pointers: Two Sum II ---")
print(two_sum_sorted([1, 3, 5, 7, 9, 11], 14))  # [1, 5] → arr[1]=3 + arr[5]=11 = 14


'''
WHY DOES THIS WORK? (The Math Behind Opposite-End Pointers)
-----------------------------------------------------------
This is the key insight most tutorials skip. Let's prove we never
"miss" the correct pair.

SETUP:  arr is sorted in non-decreasing order.
        We want indices (i, j) with i < j and arr[i] + arr[j] == target.

CLAIM:  At every step, the correct pair (i*, j*) — if it exists —
        is ALWAYS inside the current [left, right] window.

PROOF BY INVARIANT:
    Initially left=0, right=n-1, so the window contains ALL pairs. ✓

    Inductive step. Suppose (i*, j*) is currently in [left, right].
    We compare arr[left] + arr[right] with target:

      Case A: arr[left] + arr[right] < target.
        For EVERY j in (left, right], arr[left] + arr[j] <= arr[left] + arr[right]
        (because arr is sorted: arr[j] <= arr[right]).
        All those sums are also < target. So arr[left] cannot be the smaller
        element of any valid pair. Safe to discard left → left += 1. ✓

      Case B: arr[left] + arr[right] > target.
        For EVERY i in [left, right), arr[i] + arr[right] >= arr[left] + arr[right].
        All those sums are also > target. So arr[right] cannot be the larger
        element of any valid pair. Safe to discard right → right -= 1. ✓

      Case C: equal → found it.

    The invariant holds: the answer is never thrown away. Since the window
    shrinks each step and we stop when left == right, we either find the pair
    or correctly conclude none exists. ∎

DRY RUN:
    arr = [1, 3, 5, 7, 9, 11], target = 14

    Step 1: left=0(arr[0]=1), right=5(arr[5]=11). Sum=12. 12 < 14 → move left up.
            [1, 3, 5, 7, 9, 11]
             ↑              ↑
            L              R

    Step 2: left=1(arr[1]=3), right=5(arr[5]=11). Sum=14. 14 == 14 → DONE!
            [1, 3, 5, 7, 9, 11]
                ↑           ↑
                L           R

    Because the array is sorted, moving left always increases the sum,
    and moving right always decreases it. This monotonicity guides us in.

COMMON MISTAKES — Two Sum
-------------------------
❌ MISTAKE 1: Using < instead of < for the loop, or off-by-one.
    BAD:   while left <= right:     # pointers can overlap → checks one element twice
    GOOD:  while left < right:      # stop BEFORE they meet (we need TWO distinct indices)

❌ MISTAKE 2: Moving the WRONG pointer when the sum is off.
    BAD:   if current_sum < target: right -= 1   # makes an already-small sum SMALLER!
    GOOD:  if current_sum < target: left += 1    # sum small → grow it → move left up

❌ MISTAKE 3: Applying this to an UNSORTED array.
    The invariant PROOF above relies on sorted order. On unsorted input the
    algorithm is simply wrong. Sort first (O(n log n)) or use a hash map.

INTERVIEW TIPS — Two Pointers
-----------------------------
✅ Always say out loud: "Because the array is sorted, moving a pointer
   in one direction monotonically changes the sum." That's the whole game.
✅ If asked for VALUES (not indices) of a sorted array, return [arr[L], arr[R]].
✅ If the array isn't sorted, you can SORT then two-pointer (O(n log n))
   OR use a hash-map one-pass (O(n) time, O(n) space). Mention the trade-off.
✅ Asked "return 1-indexed indices" (LeetCode 167 style)? Add 1 to results.
'''


# --- EXAMPLE: PALINDROME CHECK ---
def is_palindrome(s):
    """Check if a string reads the same forwards and backwards."""
    left, right = 0, len(s) - 1
    while left < right:                  # compare mirrored pairs
        if s[left] != s[right]:          # mismatch → not a palindrome
            return False
        left += 1                        # squeeze inward from both ends
        right -= 1
    return True                          # all mirrored pairs matched


print("\n--- Two Pointers: Palindrome ---")
print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False

# Dry run of is_palindrome("racecar"):
#   r a c e c a r
#   ↑           ↑    L=0 R=6  'r'=='r' ✓
#     ↑       ↑      L=1 R=5  'a'=='a' ✓
#       ↑   ↑        L=2 R=4  'c'=='c' ✓
#         ↑          L=3 R=3  loop ends (L < R false) → True


'''
PATTERN 1B: SAME-DIRECTION (Fast & Slow pointers)
-------------------------------------------------
Use when: You need to process elements in-place, detect cycles, or
remove duplicates from a sorted array.

    slow
     ↓
    [1, 1, 2, 3, 3, 4]
     ↑
    fast

    slow tracks WHERE to write the next unique element.
    fast scans ahead looking for NEW unique elements.

    Mental model: slow is the "write head" of a tape recorder.
                  fast is the "read head" scanning the source tape.
    They share the same array to save space — in-place overwrite.
'''

# --- EXAMPLE: REMOVE DUPLICATES FROM SORTED ARRAY ---
def remove_duplicates(arr):
    if not arr:
        return 0

    slow = 0                              # write position for next unique value
    for fast in range(1, len(arr)):       # read head scans from index 1 onward
        if arr[fast] != arr[slow]:        # found a value different from last written
            slow += 1                     # advance write head
            arr[slow] = arr[fast]         # overwrite with the new unique value

    return slow + 1                       # count of unique elements


print("\n--- Two Pointers: Remove Duplicates ---")
arr = [1, 1, 2, 3, 3, 3, 4, 5, 5]
count = remove_duplicates(arr)
print(f"{count} unique elements: {arr[:count]}")  # 5 unique: [1, 2, 3, 4, 5]

# Dry run on [1, 1, 2, 3, 3]:
#   slow=0
#   fast=1: arr[1]=1 == arr[0]=1 → skip
#   fast=2: arr[2]=2 != arr[0]=1 → slow=1, arr[1]=2  → [1, 2, 2, 3, 3]
#   fast=3: arr[3]=3 != arr[1]=2 → slow=2, arr[2]=3  → [1, 2, 3, 3, 3]
#   fast=4: arr[4]=3 == arr[2]=3 → skip
#   return slow+1 = 3   (first 3 slots [1,2,3] are the uniques)


'''
PATTERN 1C: FLOYD'S CYCLE DETECTION (Tortoise & Hare)
-----------------------------------------------------
Use when: A linked list or array may contain a CYCLE. Detect it, and
optionally find the cycle's start, in O(n) time and O(1) space.

Analogy: Two runners on a track.
    - Slow runner ("tortoise") moves 1 step.
    - Fast runner ("hare") moves 2 steps.
    If there's a loop, the fast runner will eventually lap the slow one
    and they'll meet. On a straight track (no loop) the hare just finishes.

    straight track:        1 → 2 → 3 → 4 → None     (hare reaches end, no cycle)
    circular track:        1 → 2 → 3 → 4 → back to 2 (hare laps tortoise, they meet)

DETECTION (do they meet?):
    slow = slow.next
    fast = fast.next.next
    Repeat until fast is None or fast.next is None. If they ever point to the
    same node → cycle exists.

WHY MUST THEY MEET? (Proof sketch)
    Suppose the cycle has length L. Once both are inside the cycle:
      - slow position mod L advances by +1 each step.
      - fast position mod L advances by +2 each step.
      - The gap (fast - slow) mod L changes by +1 each step.
    The gap cycles through 0, 1, 2, ..., L-1, 0, ... — it MUST hit 0 within
    at most L steps. Gap 0 means slow == fast. They meet. ∎

FINDING THE CYCLE START (after they meet):
    Move one pointer back to the head. Now advance BOTH one step at a time.
    The node where they meet again is the START of the cycle.

WHY THIS FINDS THE START (Proof sketch)
    Let:
      a = distance from head to cycle start.
      b = distance from cycle start to the meeting point.
      c = distance from meeting point back around to cycle start (so b + c = L).
    At meeting: fast traveled a + b + k·L (some integer k loops),
                slow traveled a + b.
    fast = 2·slow  →  a + b + k·L = 2(a + b)  →  a = k·L − b = c + (k−1)·L.
    So a ≡ c (mod L). Walking 'a' steps from head == walking 'a' steps from
    the meeting point lands both at the cycle start. ∎

    Diagram of the geometry:

        head──a──► start ──b──► meet
                    ▲                │
                    │                │
                    └──────c─────────┘
'''


# --- EXAMPLE: FLOYD'S CYCLE DETECTION ON A LINKED LIST ---
class ListNode:
    """A simple singly-linked list node for the demos below."""
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def has_cycle(head):
    """Return True if the linked list has a cycle (Floyd's algorithm)."""
    slow = head
    fast = head
    while fast and fast.next:              # fast jumps 2; guard against running off the end
        slow = slow.next                   # tortoise: 1 step
        fast = fast.next.next              # hare:     2 steps
        if slow is fast:                   # same node object → cycle confirmed
            return True
    return False                           # hare hit the end → no cycle


def detect_cycle_start(head):
    """Return the node where the cycle begins, or None if no cycle."""
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:                   # phase 1: they meet somewhere in the cycle
            finder = head
            while finder is not slow:      # phase 2: both step 1 at a time
                finder = finder.next
                slow = slow.next
            return finder                  # meeting point == cycle start
    return None


print("\n--- Two Pointers: Floyd's Cycle Detection ---")
# Build: 1 → 2 → 3 → 4, and 4 points back to 2 (cycle starts at node 2)
n1 = ListNode(1); n2 = ListNode(2); n3 = ListNode(3); n4 = ListNode(4)
n1.next = n2; n2.next = n3; n3.next = n4; n4.next = n2   # cycle: 4 → 2
print(has_cycle(n1))                  # True
print(detect_cycle_start(n1).val)     # 2
# A cycle-free list:
a1 = ListNode(1); a2 = ListNode(2); a3 = ListNode(3)
a1.next = a2; a2.next = a3
print(has_cycle(a1))                  # False


'''
COMMON MISTAKES — Floyd's Algorithm
-----------------------------------
❌ MISTAKE 1: Forgetting to guard fast.next.
    BAD:  while fast:  fast = fast.next.next   # crashes if fast.next is None
    GOOD: while fast and fast.next:            # safe: stops before overrunning the end

❌ MISTAKE 2: Comparing VALUES instead of NODE IDENTITY.
    BAD:  if slow.val == fast.val:             # two different nodes can share a value!
    GOOD: if slow is fast:                     # same object in memory

❌ MISTAKE 3: For phase 2, moving only ONE pointer or moving at different speeds.
    Both pointers must move exactly 1 step at a time after resetting one to head.

INTERVIEW TIPS — Floyd's
------------------------
✅ This is the canonical O(1)-space cycle solution. Mention the hash-set
   alternative (store visited nodes) as the simpler O(n)-space approach.
✅ Know BOTH phases: detection AND finding the start. Interviewers love
   asking "now find where the cycle begins" as a follow-up.
✅ Variant: "Middle of the Linked List" uses the SAME fast/slow idea —
   when fast hits the end, slow is at the middle.


CONTAINER WITH MOST WATER (Opposite-Ends, Advanced)
----------------------------------------------------
Problem: Given heights[i], pick two lines that trap the most water
between them. Area = width × min(height[i], height[j]).

Why opposite ends work: Start as wide as possible (max width). The only
way to possibly beat the current area is to move the SHORTER line inward
(moving the taller line can never increase the min-height, and width
only shrinks). So greedy inward move is safe.

    heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]
               ↑                       ↑
              L                       R    width=8, height=min(1,7)=1, area=8
'''


def max_area(height):
    """Container With Most Water — opposite-end two pointers."""
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        h = min(height[left], height[right])   # water limited by shorter wall
        w = right - left
        best = max(best, h * w)                # track the best area seen
        # Move the pointer at the SHORTER wall inward (the only move that
        # could possibly raise the min-height and beat the current area).
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best


print("\n--- Two Pointers: Container With Most Water ---")
print(max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]))  # 49


'''
THREE SUM (Opposite-Ends + Sort)
--------------------------------
Problem: Find all unique triplets that sum to 0.
Approach: Sort, then for each fixed index i, run two-sum (two pointers)
on the rest of the array. Skip duplicates at both the i level and the
L/R level to avoid repeated triplets.

    Time:  O(n²)   (n outer iterations × O(n) two-pointer scan)
    Space: O(1) extra (ignoring output)
'''


def three_sum(nums):
    nums.sort()                                  # enables two-pointer inner scan
    result = []
    n = len(nums)
    for i in range(n - 2):
        if nums[i] > 0:                          # smallest value > 0 → no triplet sums to 0
            break
        if i > 0 and nums[i] == nums[i - 1]:     # skip duplicate fixed values
            continue
        left, right = i + 1, n - 1
        target = -nums[i]                        # we want nums[L] + nums[R] == -nums[i]
        while left < right:
            s = nums[left] + nums[right]
            if s == target:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:   # skip dup L
                    left += 1
                while left < right and nums[right] == nums[right - 1]: # skip dup R
                    right -= 1
                left += 1
                right -= 1
            elif s < target:
                left += 1
            else:
                right -= 1
    return result


print("\n--- Two Pointers: Three Sum ---")
print(three_sum([-1, 0, 1, 2, -1, -4]))  # [[-1, -1, 2], [-1, 0, 1]]


'''
TWO POINTERS SUMMARY:
    - Opposite ends  → sorted arrays, palindromes, container, two/three-sum
    - Same direction → remove duplicates, move zeros
    - Fast/slow      → cycle detection, middle of list
    - Time: O(n) — each element visited at most once
    - Space: O(1) — just two pointer variables


========================================================================

PART 2: SLIDING WINDOW
======================

WHAT IS IT?
-----------
A "window" is a sub-array (contiguous chunk) that slides across the array.
Think of it like a magnifying glass sliding across a document — you only
look at what's under the glass, then slide it one step at a time.

        ┌──────────┐
   ...  │ a b c d  │  e f g  ...     ← window of size 4 over the array
        └──────────┘
   slide →  a  ┌──────────┐
            ...│ b c d e  │ f g ...
               └──────────┘

WHY NOT JUST USE NESTED LOOPS?
    Brute force: try every possible sub-array → O(n²) or O(n³)
    Sliding window: maintain a running sum/count → O(n)!

    Brute force sum of every size-k window:
        for start in range(n):          # O(n)
            total = sum(arr[start:start+k])   # O(k)   → total O(n·k)
    Sliding window reuses the previous sum:
        window_sum += arr[i] - arr[i-k]       # O(1) per step → total O(n)

TWO MAIN FLAVORS:
    A) Fixed-size window: window is always exactly K wide.
    B) Dynamic window:    window grows right and shrinks left to satisfy a rule.


PATTERN 2A: FIXED-SIZE WINDOW
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

    Visualization of the "add new / subtract old" slide:

        before:  [ ... X ] ( a  b  c ) [ Y ... ]     window = (a+b+c)
        slide:   [ ... X   a]( b  c   Y)[ ... ]      window = a+b+c + Y - a = b+c+Y
                 ^                              ^
                 leaves                         enters
'''


# --- EXAMPLE: MAX SUM SUBARRAY OF SIZE K ---
def max_sum_subarray(arr, k):
    if len(arr) < k:
        return 0

    window_sum = sum(arr[:k])                 # sum of the first (leftmost) window
    max_sum = window_sum

    for i in range(k, len(arr)):              # i is the index ENTERING the window
        # arr[i]     → new element entering on the right
        # arr[i - k] → old element leaving on the left
        window_sum += arr[i] - arr[i - k]     # O(1) update instead of O(k) recompute
        max_sum = max(max_sum, window_sum)

    return max_sum


print("\n--- Sliding Window: Fixed Size ---")
print(max_sum_subarray([1, 3, 5, 7, 9, 2, 4], 3))  # 21


# --- TEMPLATE: FIXED-SIZE WINDOW (copy this in interviews) ---
def fixed_window_template(arr, k):
    """
    Generic fixed-size-k window. Replace the 'state' logic with whatever
    the problem needs (sum, product, count of something, etc.).
    """
    n = len(arr)
    if n < k:
        return None

    # 1. Build initial window state from arr[0:k]
    state = sum(arr[:k])
    best = state

    # 2. Slide: add arr[i] (entering), remove arr[i-k] (leaving)
    for i in range(k, n):
        # --- update state with entering/leaving elements ---
        state += arr[i] - arr[i - k]
        # --- update best ---
        best = max(best, state)

    return best


'''
DRY RUN of max_sum_subarray([1,3,5,7,9,2,4], 3):
    init: window_sum = 1+3+5 = 9, max_sum = 9
    i=3: window_sum = 9 + 7 - 1 = 15, max_sum = 15
    i=4: window_sum = 15 + 9 - 3 = 21, max_sum = 21
    i=5: window_sum = 21 + 2 - 5 = 18, max_sum = 21
    i=6: window_sum = 18 + 4 - 7 = 15, max_sum = 21
    return 21

COMMON MISTAKES — Fixed Window
------------------------------
❌ MISTAKE 1: Recomputing the sum from scratch each step.
    BAD:  for i in range(n-k+1): total = sum(arr[i:i+k])   # O(n·k)
    GOOD: window_sum += arr[i] - arr[i-k]                  # O(1) per step

❌ MISTAKE 2: Off-by-one on the entering/leaving indices.
    BAD:  window_sum += arr[i] - arr[i - k + 1]   # subtracts the WRONG element
    GOOD: window_sum += arr[i] - arr[i - k]       # element k positions back leaves

❌ MISTAKE 3: Forgetting the edge case len(arr) < k → return 0/None.

INTERVIEW TIPS — Fixed Window
-----------------------------
✅ State the invariant: "window always covers exactly k elements."
✅ The entering index is i; the leaving index is i-k. Memorize this pair.
✅ Common variants: max/min sum, max product, count of distinct elements
   (use a frequency map as 'state'), first negative in every window.
'''


'''
PATTERN 2B: DYNAMIC WINDOW (grow and shrink)
--------------------------------------------
"The window grows when conditions are good, shrinks when they're violated."

This is used when you're looking for the LONGEST or SHORTEST subarray
that satisfies some condition.

    arr = [1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1], flip at most k=2 zeros

    Goal: Find longest subarray with at most k zeros (can flip 2 zeros to 1s).

    Window grows right. When zeros in window > k, shrink from left.

    General dynamic-window shape:

        left = 0
        for right in range(n):
            add arr[right] to window state
            while window_is_invalid:           # condition violated
                remove arr[left] from state
                left += 1                      # shrink
            # window [left..right] is now valid again
            update best with (right - left + 1)

WHY IS THE DYNAMIC WINDOW O(n)? (Proof)
---------------------------------------
A common worry: "There's a while loop inside a for loop — isn't that O(n²)?"
NO. Here's why:

    AMORTIZED ARGUMENT:
    - The right pointer only moves FORWARD: range(n) → at most n increments.
    - The left pointer only moves FORWARD: it never decreases, only += 1.
    - Over the ENTIRE run, left goes from 0 to at most n.
    - Total pointer moves ≤ 2n. Each move does O(1) state work.
    - Therefore total work = O(2n) = O(n). ∎

    The inner while loop does NOT restart the outer loop. It just catches
    left up. Think of left and right as two runners who only ever advance.
    Combined, they take at most 2n steps regardless of how many times the
    while loop fires.

    Diagram of pointer movement (both monotonic):

        right:  ──────────────────────────►   (always forward)
        left:   ──────► (pauses) ────►        (always forward, sometimes waits)
'''


# --- EXAMPLE: LONGEST SUBSTRING WITHOUT REPEATING CHARACTERS ---
def longest_unique_substring(s):
    """
    Find the length of the longest substring without repeating characters.
    "abcabcbb" → 3 ("abc")
    """
    char_index = {}                            # last seen position of each character
    left = 0                                   # left edge of the window
    max_len = 0

    for right in range(len(s)):                # right edge expands one char at a time
        char = s[right]

        # If we've seen this char AND it's inside our current window → shrink
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1        # jump left just past the previous occurrence

        char_index[char] = right               # update last seen position
        max_len = max(max_len, right - left + 1)

    return max_len


print("\n--- Sliding Window: Dynamic ---")
print(longest_unique_substring("abcabcbb"))  # 3
print(longest_unique_substring("bbbbb"))     # 1
print(longest_unique_substring("pwwkew"))    # 3

# Dry run on "abcabcbb":
#   right=0 'a': left=0, window "a",     max=1
#   right=1 'b': left=0, window "ab",    max=2
#   right=2 'c': left=0, window "abc",   max=3
#   right=3 'a': 'a' seen at 0 ≥ left=0 → left=1, window "bca", max=3
#   right=4 'b': 'b' seen at 1 ≥ left=1 → left=2, window "cab", max=3
#   right=5 'c': 'c' seen at 2 ≥ left=2 → left=3, window "abc", max=3
#   right=6 'b': 'b' seen at 4 ≥ left=3 → left=5, window "cb",  max=3
#   right=7 'b': 'b' seen at 6 ≥ left=5 → left=7, window "b",   max=3
#   return 3


# --- TEMPLATE: DYNAMIC WINDOW — LONGEST VALID (copy this) ---
def dynamic_window_longest_template(s):
    """
    Generic template for 'longest subarray/substring satisfying a condition'.
    Replace the state + validity check with problem-specific logic.
    """
    left = 0
    state = {}                                 # e.g., frequency map, counter, etc.
    best = 0

    for right in range(len(s)):
        # 1. ADD s[right] to state (grow window to the right)
        state[s[right]] = state.get(s[right], 0) + 1

        # 2. WHILE invalid, SHRINK from the left
        while window_is_invalid(state):       # <-- define this per problem
            state[s[left]] -= 1
            if state[s[left]] == 0:
                del state[s[left]]
            left += 1

        # 3. window [left..right] is now valid → consider its length
        best = max(best, right - left + 1)

    return best


def window_is_invalid(state):
    """Placeholder — replace with the real validity rule."""
    return False  # example only


# --- TEMPLATE: DYNAMIC WINDOW — SHORTEST VALID ---
def dynamic_window_shortest_template(arr, target):
    """
    Generic template for 'shortest subarray whose sum >= target'.
    Shows the MINIMIZING variant: shrink aggressively while still valid.
    """
    left = 0
    window_sum = 0
    best = float('inf')

    for right in range(len(arr)):
        window_sum += arr[right]               # grow

        while window_sum >= target:            # still valid → try to shrink
            best = min(best, right - left + 1)
            window_sum -= arr[left]
            left += 1

    return best if best != float('inf') else 0


print("\n--- Sliding Window: Min Size Subarray Sum ---")
print(dynamic_window_shortest_template([2, 3, 1, 2, 4, 3], 7))  # 2  ([4,3])


'''
COMMON MISTAKES — Dynamic Window
--------------------------------
❌ MISTAKE 1: Using `if` instead of `while` to shrink.
    BAD:  if window_invalid: left += 1     # shrinks at most once → may stay invalid
    GOOD: while window_invalid: left += 1  # keep shrinking until valid again
    (Some problems only need `if`, e.g. "at most k" where you never need to
     shrink more than once per step — but `while` is always safe.)

❌ MISTAKE 2: Forgetting to update state when the window shrinks.
    BAD:  while invalid: left += 1         # state still reflects old window!
    GOOD: while invalid:
              remove arr[left] from state
              left += 1

❌ MISTAKE 3: In longest-unique-substring, using a SET and removing naively.
    If you `remove(s[left])` you may erase a char that still appears inside
    the window. The char_index map + `>= left` check avoids this: we JUMP
    left forward instead of stepping and removing one at a time.

INTERVIEW TIPS — Sliding Window
-------------------------------
✅ Decide fixed vs. dynamic FIRST by reading the problem:
     "exactly k"           → fixed
     "longest/shortest ... such that ..." → dynamic
✅ Name your window state explicitly (sum, count map, deque...) up front.
✅ For dynamic windows, write the shrink loop as `while not valid`.
✅ Classic problems: Max Sum Subarray (fixed), Longest Substring Without
   Repeating Characters (dynamic), Minimum Window Substring, Longest
   Repeating Character Replacement, Permutation in String.

SLIDING WINDOW SUMMARY:
    - Fixed size: window always K wide. Add new, subtract old. O(n).
    - Dynamic size: window grows right, shrinks left when condition breaks. O(n).
    - Key insight: NEVER recalculate from scratch. Maintain running state.
    - Time: O(n) — each element enters and leaves the window at most once
    - Space: O(k) for tracking window contents (hash map or set)


========================================================================

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

    Search space shrinks geometrically:

        [================================]   n elements
        [             ]                    n/2
        [      ]                            n/4
        [ ]                                   1   ← found or absent

THE ALGORITHM (MEMORIZE THIS)
'''


def binary_search(arr, target):
    """
    Find target in a sorted array.
    Returns the index if found, -1 if not found.
    """
    left = 0
    right = len(arr) - 1

    while left <= right:                       # <= so a single-element window is checked
        mid = (left + right) // 2              # look at the middle index

        if arr[mid] == target:
            return mid                         # exact match
        elif arr[mid] < target:
            left = mid + 1                     # target in RIGHT half → discard left (incl. mid)
        else:
            right = mid - 1                    # target in LEFT half → discard right (incl. mid)

    return -1                                  # search space empty → not present


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

    Formal: After k steps the search space is ≤ n / 2^k. We stop when
    n / 2^k ≤ 1, i.e., 2^k ≥ n, i.e., k ≥ log₂(n). So at most ⌈log₂ n⌉ steps.

THE THREE BINARY SEARCH VARIANTS (know all three!)
-------------------------------------------------
Most binary-search bugs come from mixing up these three loop conditions.
Pick the right variant by deciding: "Could `mid` itself be the answer?"

VARIANT A: EXACT MATCH (the one above)
    Loop:   while left <= right
    Update: left = mid + 1   /   right = mid - 1
    Use:    "find target" — mid is consumed on every branch.

VARIANT B: LEFTMOST / LOWER BOUND (first index where arr[i] >= target)
    Loop:   while left < right
    Update: left = mid + 1 (when arr[mid] < target)
            right = mid     (when arr[mid] >= target — mid could be the answer!)
    Use:    "find first >= target", "count elements < target", insert position.

VARIANT C: RIGHTMOST / UPPER BOUND (last index where arr[i] <= target)
    Loop:   while left < right
    Update: left = mid      (when arr[mid] <= target — mid could be the answer!)
            right = mid - 1 (when arr[mid] > target)
    Use:    "find last <= target", right insertion position.
'''


# --- VARIANT B: LEFTMOST INDEX (lower bound) ---
def lower_bound(arr, target):
    """First index i such that arr[i] >= target. Returns len(arr) if all < target."""
    left, right = 0, len(arr)                  # note: right = len(arr), not len-1
    while left < right:
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1                     # mid too small → discard mid too
        else:
            right = mid                        # mid is a candidate → keep it, look left
    return left


# --- VARIANT C: RIGHTMOST INDEX (upper bound style) ---
def upper_bound_last(arr, target):
    """Last index i such that arr[i] <= target. Returns -1 if all > target."""
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] <= target:
            result = mid                       # mid is a candidate → save, look right
            left = mid + 1
        else:
            right = mid - 1
    return result


print("\n--- Binary Search: Boundary Variants ---")
b = [1, 3, 3, 3, 5, 7, 9]
print(lower_bound(b, 3))          # 1  (first index where val >= 3)
print(upper_bound_last(b, 3))     # 3  (last index where val <= 3)


'''
COMMON MISTAKES — Binary Search
------------------------------
❌ MISTAKE 1: Infinite loop from wrong mid + wrong update.
    With `right = mid` you MUST use `mid = (left + right) // 2` (floor).
    Using `right = mid - 1` together with `left = mid` can loop forever
    when left and right differ by 1, because mid floors to left and
    left = mid never advances.

❌ MISTAKE 2: Mixing loop conditions across variants.
    BAD:  while left <= right: ... right = mid      # can skip the answer
    Each variant has ONE correct (loop, update) pair. Don't mix and match.

❌ MISTAKE 3: Integer overflow (mainly Java/C++, but good to know).
    (left + right) can overflow a 32-bit int. Use mid = left + (right - left) // 2.
    In Python this is a non-issue (arbitrary-precision ints), but interviewers
    love hearing you mention it.

❌ MISTAKE 4: Forgetting the array must be SORTED. Binary search on unsorted
    input silently returns wrong answers.

INTERVIEW TIPS — Binary Search
-----------------------------
✅ Before writing code, say which variant you need: exact / leftmost / rightmost.
✅ Use `left + (right - left) // 2` and mention overflow safety.
✅ Tracing a 3-4 step dry run on the whiteboard catches almost all off-by-one bugs.
'''


'''
BINARY SEARCH ON ANSWER SPACE (The "Koko" Pattern)
====================================================
Many hard problems don't give you a sorted array to search — they give you
a QUESTION and you binary search over the range of possible ANSWERS.

THE PATTERN:
    "Find the minimum X such that condition(X) is true."
    (where condition is MONOTONIC — once true for X, it stays true for bigger X)

Monotonicity is the whole enabler:
      X:        1  2  3  4  5  6  7  8 ...
      cond(X):  F  F  F  T  T  T  T  T   ← flips once, then stays
                                  ↑
                          smallest X where true = our answer

    We binary search for that flip point exactly like searching a sorted array.

If condition(mid) is TRUE  → mid works, but maybe smaller works → search LEFT  (right = mid)
If condition(mid) is FALSE → mid too small                     → search RIGHT (left = mid + 1)


EXAMPLE: KOKO EATING BANANAS (LeetCode 875)
-------------------------------------------
Problem: Koko has piles of bananas. She eats k bananas/hour (k per pile per
hour, can't split across piles in one hour). Find the MINIMUM integer k such
that she finishes all piles within H hours.

Why binary search?
    - k ranges from 1 to max(piles) (eating faster than the biggest pile
      gains nothing).
    - condition(k) = "can finish in H hours at speed k" is MONOTONIC:
      faster speed (bigger k) only helps. Once she can finish at speed k,
      she can finish at any speed > k.
    - So binary search the smallest k where condition(k) is true.
'''


def koko_eating_bananas(piles, h):
    """Minimum eating speed k to finish all piles within h hours."""

    def can_finish(k):
        # hours needed = ceil(pile / k) summed over all piles
        hours = 0
        for p in piles:
            hours += (p + k - 1) // k          # integer ceiling division
        return hours <= h

    left, right = 1, max(piles)                 # search space: speeds 1 .. max(piles)
    while left < right:                         # variant B-style: find leftmost true
        mid = (left + right) // 2
        if can_finish(mid):                     # mid speed works → try slower (smaller)
            right = mid
        else:                                   # mid too slow → need faster (bigger)
            left = mid + 1
    return left


print("\n--- Binary Search on Answer: Koko Eating Bananas ---")
print(koko_eating_bananas([3, 6, 7, 11], 8))  # 4

# Dry run, piles=[3,6,7,11], h=8:
#   left=1, right=11
#   mid=6: can_finish(6)? hours=1+1+2+2=6 ≤8 ✓ → right=6
#   mid=3: can_finish(3)? hours=1+2+3+4=10 >8 ✗ → left=4
#   mid=4: can_finish(4)? hours=1+2+2+3=8  ≤8 ✓ → right=4
#   left==right==4 → return 4


# --- TEMPLATE: BINARY SEARCH ON ANSWER SPACE (copy this) ---
def answer_space_template(low, high, feasible):
    """
    Find the minimum value in [low, high] where feasible(value) is True.
    `feasible` MUST be monotonic (False...False, True...True).
    """
    left, right = low, high
    while left < right:
        mid = (left + right) // 2
        if feasible(mid):                       # mid works → maybe smaller works too
            right = mid
        else:                                   # mid fails → need bigger
            left = mid + 1
    return left


'''
More "binary search on answer" problems (same template):
    - Split Array Largest Sum (minimize the largest subarray sum)
    - Capacity To Ship Packages Within D Days (minimize ship capacity)
    - Aggressive Cows / Magnetic Force Between Balls (maximize min distance)
    - Min Days to Make m Bouquets
    - Find the Smallest Divisor Given a Threshold

INTERVIEW TIPS — Answer-Space Search
------------------------------------
✅ The hardest part is RECOGNIZING the pattern. Trigger phrases:
   "minimum X such that ...", "maximum X such that ...", "is it possible in ...".
✅ Always verify monotonicity out loud before coding.
✅ The feasible() helper is usually a greedy/linear check — keep it simple.
✅ Set the search bounds generously: low=1, high=max(input) or sum(input).

BINARY SEARCH REQUIREMENTS:
    1. The array MUST be sorted (or the search space must be monotonic)
    2. You must be able to eliminate half the space with each check
    3. Time: O(log n) — or O(log(range) · cost_of_feasible) for answer-space
    4. Space: O(1) — just left, right, mid variables
'''


# === VERIFY EVERYTHING RUNS ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 2 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. TWO POINTERS — two indices moving coordinately. O(n) time, O(1) space.
   - Opposite ends:  sorted arrays, palindromes, container, two/three-sum.
     * Works because sorted order makes the sum monotonic in each pointer.
   - Same direction: remove duplicates, move zeros (read/write heads).
   - Fast/slow:      cycle detection (Floyd's), middle of list.
     * They MUST meet in a cycle because the gap mod L changes by +1/step.

2. SLIDING WINDOW — a sub-array that slides across. O(n), avoids nested loops.
   - Fixed size:  add the entering element, subtract the leaving one.
   - Dynamic:     grow right, shrink left while invalid.
     * O(n) despite nested loops because BOTH pointers only move forward
       (≤ 2n total moves). This is the amortized argument.
   - Never recompute window state from scratch — maintain it incrementally.

3. BINARY SEARCH — find an element in a sorted array. O(log n).
   - Cut the search space in half each step.
   - Three variants: exact match, leftmost (lower bound), rightmost.
   - Answer-space pattern: "minimum X where feasible(X)" with monotonic
     feasible — e.g., Koko Eating Bananas, Split Array Largest Sum.
   - Watch the (loop-condition, update-rule) pairing to avoid infinite loops.

Next: Chapter 3 — Stacks, Queues & Linked Lists
""")
