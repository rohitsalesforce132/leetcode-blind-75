'''
LEETCODE #35: Search Insert Position
DIFFICULTY: Easy
TOPIC: Binary Search

=== PROBLEM STATEMENT ===
Given a sorted array of distinct integers and a target value, return the
index if the target is found. If not, return the index where it would be if
it were inserted in order.

You must write an algorithm with O(log n) runtime complexity.

=== INTUITION ===
This is binary search with a twist: if the target is not found, we return
the position where it would be inserted. The key observation is that when
the while loop exits (left > right), `left` points exactly to the insertion
point — because `left` is the first index where nums[left] >= target would
hold (or it points past the end of the array).

=== APPROACHES ===
Approach 1: Brute Force / Linear Search
- Idea: Walk through the array; return index if equal, or the first index
  where nums[i] > target.
- Time: O(n)
- Space: O(1)

Approach 2: Optimal — Binary Search
- Idea: Standard binary search; when the loop ends, `left` is the insert pos.
- Time: O(log n)
- Space: O(1)

=== DRY RUN ===
nums = [1, 3, 5, 6], target = 2

Step 1: left=0, right=3
        mid = 1, nums[1] = 3 > 2 => right = 0
Step 2: left=0, right=0
        mid = 0, nums[0] = 1 < 2 => left = 1
Loop exits: left=1, right=0 -> return 1

Output: 1   (2 would be inserted at index 1, between 1 and 3)

=== COMPLEXITY ANALYSIS ===
Time: O(log n)
Space: O(1)

=== EDGE CASES ===
- Target smaller than all elements -> return 0
- Target larger than all elements -> return len(nums)
- Empty array -> return 0
- Target at very beginning or end
- Array with one element

=== INTERVIEW TIPS ===
- This is essentially "lower bound" in C++ terms — the first position
  where you could insert the value while maintaining sorted order.
- Mention: this is the same technique used in insertion sort to find the
  correct position.
- Follow-up: How would you handle duplicates? (Still works — `left` lands
  on the first valid insertion position.)
'''

# === SOLUTION ===
from typing import List


def searchInsert(nums: List[int], target: int) -> int:
    """Return index of target, or the insertion index if not found."""
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    # At this point, left > right. `left` is the insertion point.
    return left


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: target found in middle
    assert searchInsert([1, 3, 5, 6], 5) == 2
    # Test 2: target absent — insert in middle
    assert searchInsert([1, 3, 5, 6], 2) == 1
    # Test 3: target absent — insert at end
    assert searchInsert([1, 3, 5, 6], 7) == 4
    # Test 4: target absent — insert at start
    assert searchInsert([1, 3, 5, 6], 0) == 0
    # Test 5: single element, present
    assert searchInsert([1], 1) == 0
    # Test 6: single element, absent — larger
    assert searchInsert([1], 2) == 1
    # Test 7: empty array
    assert searchInsert([], 5) == 0
    print("All tests passed!")
