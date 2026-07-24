'''
LEETCODE #33: Search in Rotated Sorted Array
DIFFICULTY: Medium
TOPIC: Binary Search

=== PROBLEM STATEMENT ===
There is an integer array nums sorted in ascending order (with distinct
values). The array may have been rotated at an unknown pivot index. Given
the array nums after rotation and an integer target, return the index of
target if it is in the array, or -1 if not.

You must write an algorithm with O(log n) runtime complexity.

=== INTUITION ===
Even though the array is rotated, at any given midpoint, one of the two
halves (left or right) is always normally sorted. By identifying which half
is sorted, we can decide whether the target lies within it:

1. If nums[left] <= nums[mid]: left half is sorted.
   - If nums[left] <= target < nums[mid]: search left half.
   - Else: search right half.
2. Else: right half is sorted.
   - If nums[mid] < target <= nums[right]: search right half.
   - Else: search left half.

=== APPROACHES ===
Approach 1: Brute Force / Linear Scan
- Idea: Scan every element.
- Time: O(n)
- Space: O(1)

Approach 2: Optimal — Binary Search (identify sorted half)
- Idea: At each step, figure out which half is sorted and check if target
  is in that half.
- Time: O(log n)
- Space: O(1)

=== DRY RUN ===
nums = [4, 5, 6, 7, 0, 1, 2], target = 0

Step 1: left=0, right=6
        mid=3, nums[mid]=7
        nums[left]=4 <= 7 => left half [4,5,6,7] is sorted.
        Is 4 <= 0 < 7? No => target is in right half. left = mid+1 = 4.
Step 2: left=4, right=6
        mid=5, nums[mid]=1
        nums[left]=0 <= 1 => left half [0,1] is sorted.
        Is 0 <= 0 < 1? Yes => target in left half. right = mid-1 = 4.
Step 3: left=4, right=4
        mid=4, nums[mid]=0 == target => return 4.

Output: 4

=== COMPLEXITY ANALYSIS ===
Time: O(log n)
Space: O(1)

=== EDGE CASES ===
- Array not rotated (sorted) — the logic still works.
- Single-element array.
- Two-element arrays.
- Target smaller than all or larger than all elements.
- Target is the pivot element itself.

=== INTERVIEW TIPS ===
- The trick is realizing that one half is ALWAYS sorted — this is the
  fundamental invariant of a rotated sorted array.
- Drawing the array as a rotated line graph helps visualize which side is
  sorted.
- Follow-up: LeetCode 81 (same problem with duplicates) — when
  nums[left]==nums[mid]==nums[right], we can't tell which side is sorted;
  we shrink the range by moving left++/right--.
- A common bug: forgetting the boundary conditions (<= vs <). Test with
  two-element arrays.
'''

# === SOLUTION ===
from typing import List


def search(nums: List[int], target: int) -> int:
    """Search target in rotated sorted array with distinct elements."""
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (mid_offset := (right - left) // 2)

        if nums[mid] == target:
            return mid

        # Left half sorted?
        if nums[left] <= nums[mid]:
            # Is target within the sorted left half?
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Right half is sorted.
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: standard rotated case
    assert search([4, 5, 6, 7, 0, 1, 2], 0) == 4
    # Test 2: target absent
    assert search([4, 5, 6, 7, 0, 1, 2], 3) == -1
    # Test 3: single element, present
    assert search([1], 0) == -1
    # Test 4: two elements, target is first
    assert search([3, 1], 3) == 0
    # Test 5: two elements, target is second
    assert search([3, 1], 1) == 1
    # Test 6: unrotated array
    assert search([1, 2, 3, 4, 5], 4) == 3
    # Test 7: target at boundaries
    assert search([4, 5, 6, 7, 0, 1, 2], 4) == 0
    assert search([4, 5, 6, 7, 0, 1, 2], 2) == 6
    print("All tests passed!")
