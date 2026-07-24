'''
LEETCODE #287: Find the Duplicate Number
DIFFICULTY: Medium
TOPIC: Linked List (Floyd's Cycle Detection)

=== PROBLEM STATEMENT ===
Given an array of integers nums containing n + 1 integers where each integer
is in the range [1, n] inclusive. There is only one repeated number in nums,
return this repeated number.

You must solve the problem without modifying the array nums and using only
constant extra space.

=== INTUITION ===
Because all values are in [1, n] and there are n+1 positions, we can treat
the array as a linked list where nums[i] is the "next pointer" from node i.
Since values are in [1, n], we never point to index 0, so index 0 is a valid
starting point that leads into the "list."

A duplicate value means two different indices point to the same next index,
creating a cycle (like a linked list cycle). We can find the duplicate using
Floyd's cycle detection — exactly like Linked List Cycle (LeetCode 141/142).

Phase 1: Find the meeting point (slow and fast pointers).
Phase 2: Reset one pointer to 0, move both at the same speed; they meet at
the cycle entrance, which is the duplicate number.

=== APPROACHES ===
Approach 1: Brute Force — Sorting
- Idea: Sort the array, then find adjacent duplicates.
- Time: O(n log n)
- Space: O(1) or O(n) depending on sort
- NOTE: Modifies the array (or uses O(n) copy) — violates constraints.

Approach 2: Hash Set
- Idea: Track seen numbers in a set.
- Time: O(n)
- Space: O(n) — violates the O(1) space constraint.

Approach 3: Optimal — Floyd's Cycle Detection
- Idea: Treat array as linked list; find cycle entrance.
- Time: O(n)
- Space: O(1)

=== DRY RUN ===
nums = [1, 3, 4, 2, 2]  (n=4, values in [1,4])

Interpretation as a linked list:
  0 -> 1 -> 3 -> 2 -> 4 -> 2 -> 4 -> 2 -> ...  (cycle between 2 and 4)

Phase 1: Find meeting point.
  slow = nums[0] = 1
  fast = nums[0] = 1
  Step 1: slow = nums[1] = 3, fast = nums[nums[1]] = nums[3] = 2
  Step 2: slow = nums[3] = 2, fast = nums[nums[2]] = nums[4] = 2
  slow == fast == 2 (meeting point)

Phase 2: Find cycle entrance.
  slow2 = 0
  Step 1: slow = nums[2] = 4, slow2 = nums[0] = 1
  Step 2: slow = nums[4] = 2, slow2 = nums[1] = 3
  Step 3: slow = nums[2] = 4, slow2 = nums[3] = 2
  Hmm, they don't meet here... let me recompute.

  Actually, the meeting point is at index 2 (value 2). Let me redo:

  Phase 1:
    slow = nums[0] = 1, fast = nums[0] = 1
    Iteration 1: slow = nums[1] = 3, fast = nums[nums[1]] = nums[3] = 2
    Iteration 2: slow = nums[3] = 2, fast = nums[nums[2]] = nums[4] = 2
    Now slow = fast = 2. Meeting point at INDEX 2.

  Phase 2:
    slow2 = 0, slow = 2 (the meeting point)
    Iteration 1: slow2 = nums[0] = 1, slow = nums[2] = 4
    Iteration 2: slow2 = nums[1] = 3, slow = nums[4] = 2
    Iteration 3: slow2 = nums[3] = 2, slow = nums[2] = 4
    Hmm, not converging...

  CORRECTION: In Phase 2, both pointers should advance using nums[ptr].
  Let me be very careful:
    ptr1 = 0, ptr2 = meeting_point_index = 2
    Iteration 1: ptr1 = nums[0] = 1, ptr2 = nums[2] = 4
    Iteration 2: ptr1 = nums[1] = 3, ptr2 = nums[4] = 2
    Iteration 3: ptr1 = nums[3] = 2, ptr2 = nums[2] = 4
    They never meet — something is wrong with the dry run.

  Let me recheck the meeting point computation:
    slow starts at nums[0]=1, fast starts at nums[0]=1.
    BUT we should move first, then compare. Let me redo:

    slow=1, fast=1
    Move: slow = nums[slow] = nums[1] = 3
          fast = nums[nums[fast]] = nums[nums[1]] = nums[3] = 2
    Compare: 3 != 2
    Move: slow = nums[3] = 2
          fast = nums[nums[2]] = nums[4] = 2
    Compare: 2 == 2 -> Meeting point value = 2

  Phase 2: Both from their positions, one step at a time:
    ptr1 = nums[0] = 1, ptr2 = 2 (at meeting point)
    Move: ptr1 = nums[1] = 3, ptr2 = nums[2] = 4
    Move: ptr1 = nums[3] = 2, ptr2 = nums[4] = 2
    Compare: 2 == 2 -> The duplicate is 2!

Output: 2

=== COMPLEXITY ANALYSIS ===
Time: O(n)
Space: O(1)

=== EDGE CASES ===
- Duplicate appears exactly twice
- Duplicate appears more than twice
- Duplicate is 1 or n
- All elements are the same
- The cycle includes index 0

=== INTERVIEW TIPS ===
- The insight of mapping the array to a linked list is non-obvious — it's
  worth explaining in detail: nums[i] represents the "next node" from i.
- Constraints (no array modification, O(1) space) are KEY — they eliminate
  sorting and hash sets. Ask about these constraints upfront.
- The mathematical proof for Phase 2: Let L = distance to cycle start,
  C = cycle length, M = meeting point distance into cycle.
  slow = L + M, fast = L + M + kC. Since fast = 2*slow: L + M + kC = 2L + 2M
  => L = kC - M. So starting from head (distance L) and meeting point
  (distance M into cycle, need kC - M more to complete k loops) both arrive
  at the cycle start simultaneously.
- Follow-up: Can you find ALL duplicates? (Would need O(n) space or modify
  the array.)
'''

# === SOLUTION ===
from typing import List


def findDuplicate(nums: List[int]) -> int:
    """Floyd's cycle detection to find the duplicate number."""
    # Phase 1: Find the meeting point inside the cycle.
    slow = nums[0]
    fast = nums[0]

    while True:
        slow = nums[slow]               # 1 step
        fast = nums[nums[fast]]          # 2 steps
        if slow == fast:
            break

    # Phase 2: Find the entrance to the cycle (the duplicate).
    slow2 = nums[0]
    while slow != slow2:
        slow = nums[slow]
        slow2 = nums[slow2]

    return slow


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: standard case
    assert findDuplicate([1, 3, 4, 2, 2]) == 2
    # Test 2: duplicate is 1
    assert findDuplicate([1, 1, 2]) == 1
    # Test 3: multiple appearances of the duplicate
    assert findDuplicate([2, 5, 9, 6, 9, 3, 8, 9, 7, 1]) == 9
    # Test 4: all elements cycle through
    assert findDuplicate([3, 1, 3, 4, 2]) == 3
    # Test 5: two elements
    assert findDuplicate([1, 1]) == 1
    print("All tests passed!")
