'''
LEETCODE #704: Binary Search
DIFFICULTY: Easy
TOPIC: Binary Search

=== PROBLEM STATEMENT ===
Given an array of integers nums which is sorted in ascending order, and an
integer target, write a function to search target in nums. If target exists,
return its index. Otherwise, return -1.

You must write an algorithm with O(log n) runtime complexity.

=== INTUITION ===
The array is sorted, so we can use binary search:
1. Start with two pointers: left at the beginning, right at the end.
2. Find the middle element.
3. If the middle element equals the target, we're done.
4. If the target is smaller than mid, search the left half.
5. If the target is larger than mid, search the right half.
6. Repeat until found or the pointers cross.

The key insight: because the array is sorted, each comparison tells us
which half of the remaining search space can be eliminated.

=== APPROACHES ===
Approach 1: Brute Force / Linear Search
- Idea: Scan every element and check if it equals target.
- Time: O(n)
- Space: O(1)

Approach 2: Optimal — Iterative Binary Search
- Idea: Use two pointers to halve the search space each iteration.
- Time: O(log n)
- Space: O(1)

Approach 3: Recursive Binary Search
- Idea: Same halving logic but with recursion.
- Time: O(log n)
- Space: O(log n) for call stack

=== DRY RUN ===
nums = [-1, 0, 3, 5, 9, 12], target = 9

Step 1: left=0, right=5
        mid = (0+5)//2 = 2
        nums[2] = 3 < 9 => target must be in right half
        left = mid + 1 = 3

Step 2: left=3, right=5
        mid = (3+5)//2 = 4
        nums[4] = 9 == 9 => FOUND, return 4

Output: 4

=== COMPLEXITY ANALYSIS ===
Time: O(log n) — we halve the search space each iteration.
Space: O(1) — only a few variables used.

=== EDGE CASES ===
- Empty array (nums = []) -> return -1
- Target smaller than the smallest element -> return -1
- Target larger than the largest element -> return -1
- Single-element array where element equals / does not equal target
- Target at the very first or very last index
- Duplicate elements (still fine; we return any valid index)

=== INTERVIEW TIPS ===
- Always clarify: "Is the array sorted?" — binary search REQUIRES sorting.
- Mention the overflow bug: mid = left + (right - left) // 2 is safer than
  (left + right) // 2 for very large indices (not a practical concern in
  Python, but interviewers love this detail).
- Discuss iterative vs recursive trade-offs.
- Follow-up: Can you find the first/last occurrence of a duplicate target?
  (That leads to the "lower_bound"/"upper_bound" variants.)
'''

# === SOLUTION ===
from typing import List


def search(nums: List[int], target: int) -> int:
    """Iterative binary search returning index of target, or -1."""
    left, right = 0, len(nums) - 1

    while left <= right:
        # Avoids potential integer overflow in other languages.
        mid = left + (right - left) // 2

        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1    # target in right half
        else:
            right = mid - 1   # target in left half

    return -1


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: target present
    assert search([-1, 0, 3, 5, 9, 12], 9) == 4
    # Test 2: target absent
    assert search([-1, 0, 3, 5, 9, 12], 2) == -1
    # Test 3: single element — present
    assert search([5], 5) == 0
    # Test 4: single element — absent
    assert search([5], 2) == -1
    # Test 5: target at start
    assert search([1, 2, 3, 4, 5], 1) == 0
    # Test 6: target at end
    assert search([1, 2, 3, 4, 5], 5) == 4
    # Test 7: empty array
    assert search([], 1) == -1
    print("All tests passed!")
