'''
LEETCODE #153: Find Minimum in Rotated Sorted Array
DIFFICULTY: Medium
TOPIC: Binary Search

=== PROBLEM STATEMENT ===
Suppose an array of length n sorted in ascending order is rotated between
1 and n times. For example, nums = [0,1,2,4,5,6,7] might become
[4,5,6,7,0,1,2]. Notice that rotating an array [a[0], a[1], ..., a[n-1]]
once results in [a[n-1], a[0], ..., a[n-2]].

Given the sorted rotated array nums of unique elements, return the minimum
element of the array.

You must write an algorithm with O(log n) runtime complexity.

=== INTUITION ===
In a rotated sorted array, the minimum element is the "pivot" — the point
where the rotation broke the order. The property we exploit: comparing
nums[mid] to nums[right] tells us which side is unsorted (and thus which
side contains the minimum).

- If nums[mid] > nums[right]: the minimum is in the right half (because the
  right side contains the rotation point). Move left = mid + 1.
- If nums[mid] <= nums[right]: the right half is sorted, so the minimum is
  at mid or in the left half. Move right = mid.

We compare to nums[right] (not nums[left]) because comparing to nums[left]
can't distinguish a fully-sorted (unrotated) array from a rotated one.

=== APPROACHES ===
Approach 1: Brute Force / Linear Scan
- Idea: Scan all elements and return the minimum.
- Time: O(n)
- Space: O(1)

Approach 2: Optimal — Binary Search
- Idea: Compare nums[mid] with nums[right] to decide which half to keep.
- Time: O(log n)
- Space: O(1)

=== DRY RUN ===
nums = [4, 5, 6, 7, 0, 1, 2]

Step 1: left=0, right=6
        mid = 3, nums[3]=7, nums[6]=2
        7 > 2 => min is in right half, left = 4
Step 2: left=4, right=6
        mid = 5, nums[5]=1, nums[6]=2
        1 <= 2 => min is at mid or left of it, right = 5
Step 3: left=4, right=5
        mid = 4, nums[4]=0, nums[5]=1
        0 <= 1 => right = 4
Loop exits: left == right == 4 => return nums[4] = 0

Output: 0

=== COMPLEXITY ANALYSIS ===
Time: O(log n)
Space: O(1)

=== EDGE CASES ===
- Array not rotated (already sorted) — e.g., [1, 2, 3, 4]
- Single-element array
- Two-element arrays — rotated and unrotated
- Minimum at index 0 or index 1

=== INTERVIEW TIPS ===
- Always clarify whether the array has duplicates (LeetCode 154 is the
  hard version with duplicates; same idea but nums[mid]==nums[right] needs
  special handling — decrement right).
- Drawing the rotated array visually helps. Think of two sorted subarrays
  separated by the pivot.
- Be careful with the condition `nums[mid] > nums[right]` vs `nums[mid] >=
  nums[right]` — since elements are distinct, strict > is correct here.
'''

# === SOLUTION ===
from typing import List


def findMin(nums: List[int]) -> int:
    """Find minimum in rotated sorted array with distinct elements."""
    left, right = 0, len(nums) - 1

    while left < right:
        mid = left + (right - left) // 2

        if nums[mid] > nums[right]:
            # The pivot (and therefore the minimum) is in the right half.
            left = mid + 1
        else:
            # Right half is sorted; minimum is at mid or to its left.
            right = mid

    return nums[left]


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: rotated array
    assert findMin([4, 5, 6, 7, 0, 1, 2]) == 0
    # Test 2: unrotated (sorted) array
    assert findMin([1, 2, 3, 4, 5]) == 1
    # Test 3: single element
    assert findMin([1]) == 1
    # Test 4: two elements rotated
    assert findMin([3, 1]) == 1
    # Test 5: two elements sorted
    assert findMin([1, 2]) == 1
    # Test 6: rotation at the very end
    assert findMin([2, 1]) == 1
    print("All tests passed!")
