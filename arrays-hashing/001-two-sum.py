'''
LEETCODE #1: Two Sum
DIFFICULTY: Easy
TOPIC: Arrays & Hashing

=== PROBLEM STATEMENT ===
Given an array of integers nums and an integer target, return indices of the
two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may
not use the same element twice. You can return the answer in any order.

Example 1: Input: nums = [2,7,11,15], target = 9  Output: [0,1]
Example 2: Input: nums = [3,2,4], target = 6       Output: [1,2]
Example 3: Input: nums = [3,3], target = 6          Output: [0,1]

=== INTUITION ===
- We need two numbers a and b where a + b = target, i.e. b = target - a.
- If we already saw a's "complement" requirement, we can find the pair in one pass.
- A hash map gives O(1) lookup: store value -> index while iterating.
- For each element, check if its complement already exists in the map.
- This turns an O(n^2) brute force into O(n) by trading space for time.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: Try every pair (i, j) with i < j; return when nums[i] + nums[j] == target.
- Time: O(n^2)
- Space: O(1)

Approach 2: Hash Map (One Pass) - OPTIMAL
- Idea: Iterate once; for each nums[i], check if (target - nums[i]) is in map.
        If yes, return [map[complement], i]. Otherwise store nums[i] -> i.
- Time: O(n)
- Space: O(n)

Approach 3: Two-Pass Hash Map
- Idea: First pass builds the full map; second pass looks up complements.
- Time: O(n)
- Space: O(n)
- (One-pass is preferred: it naturally avoids using the same element twice.)

=== DRY RUN ===
nums = [2, 7, 11, 15], target = 9

Step 1: i=0, nums[0]=2
  complement = 9 - 2 = 7
  map = {} -> 7 not in map
  store: map = {2: 0}

Step 2: i=1, nums[1]=7
  complement = 9 - 7 = 2
  map = {2: 0} -> 2 IS in map at index 0
  return [0, 1]

Result: [0, 1]  (2 + 7 = 9)  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - single pass through the array; each hash map op is O(1) amortized.
Space: O(n) - in the worst case we store n-1 entries before finding the pair.

=== EDGE CASES ===
- Exactly two elements that sum to target (minimum valid input).
- Duplicate values that are the answer, e.g. [3,3] target=6.
- Negative numbers and zero: target = 0, nums = [-1, 1].
- Very large array (stress test hash map performance).
- No solution (problem guarantees one exists, but discuss what to do).

=== INTERVIEW TIPS ===
- State the O(n) one-pass hash map approach immediately; brute force is a
  starting point but never the final answer.
- Clarify "exactly one solution" and "cannot reuse the same element".
- Follow-up: What if the array is sorted? -> Two pointers, O(n) time, O(1) space.
- Follow-up: Return values instead of indices? -> sorting is viable.
- Mention that Python dict preserves insertion order (3.7+), but not needed here.
'''

# === SOLUTION ===
from typing import List


def twoSum(nums: List[int], target: int) -> List[int]:
    """One-pass hash map: value -> index."""
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []  # Problem guarantees a solution; unreachable.


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert twoSum([2, 7, 11, 15], 9) == [0, 1]
    # Test 2: Answer not at the start
    assert twoSum([3, 2, 4], 6) == [1, 2]
    # Test 3: Duplicate values forming the answer
    assert twoSum([3, 3], 6) == [0, 1]
    # Test 4: Negative numbers
    assert twoSum([-1, -2, -3, -4, -5], -8) == [2, 4]
    # Test 5: Zero involved
    assert twoSum([0, 4, 3, 0], 0) == [0, 3]
    # Test 6: Larger gap
    assert twoSum([1, 5, 8, 11, 14], 19) == [1, 3]
    print("All tests passed!")
