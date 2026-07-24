'''
LEETCODE #167: Two Sum II - Input Array Is Sorted
DIFFICULTY: Medium
TOPIC: Two Pointers

=== PROBLEM STATEMENT ===
Given a 1-indexed array of integers numbers that is already sorted in
non-decreasing order, find two numbers such that they add up to a specific
target number. Let these two numbers be numbers[index1] and numbers[index2]
where 1 <= index1 < index2 <= numbers.length.

Return the indices of the two numbers, index1 and index2, added by one (i.e.,
index1 + 1, index2 + 1) as an integer array [index1, index2] of length 2.
The tests are generated such that there is exactly one solution. You may not
use the same element twice.

Example 1: Input: numbers = [2,7,11,15], target = 9  Output: [1,2]
Example 2: Input: numbers = [2,3,4], target = 6       Output: [1,3]
Example 3: Input: numbers = [-1,0], target = -1       Output: [1,2]

=== INTUITION ===
- The array is SORTED, so two pointers exploit this structure.
- Place one pointer at the start (left), one at the end (right).
- If their sum < target: we need a bigger sum -> move left rightward.
- If their sum > target: we need a smaller sum -> move right leftward.
- If sum == target: found it. Return 1-indexed positions.
- This works because moving left increases the sum and moving right decreases it.

=== APPROACHES ===
Approach 1: Hash Map (ignores sorted property)
- Idea: Same as Two Sum I; map value -> index.
- Time: O(n)
- Space: O(n)
- Works but wastes the sorted structure and uses extra space.

Approach 2: Two Pointers - OPTIMAL (exploits sorted input)
- Idea: left=0, right=n-1; adjust pointers based on sum vs target.
- Time: O(n)
- Space: O(1)

Approach 3: Binary Search
- Idea: For each numbers[i], binary search for target - numbers[i] in i+1:.
- Time: O(n log n)
- Space: O(1)

=== DRY RUN ===
numbers = [2, 7, 11, 15], target = 9

  left=0, right=3: numbers[0]+numbers[3] = 2+15 = 17 > 9 -> right--
  left=0, right=2: numbers[0]+numbers[2] = 2+11 = 13 > 9 -> right--
  left=0, right=1: numbers[0]+numbers[1] = 2+7  = 9 == 9 -> FOUND

Return [left+1, right+1] = [1, 2]  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - pointers move at most n steps total.
Space: O(1) - only two pointer variables.

=== EDGE CASES ===
- Two elements only (minimum input).
- Negative numbers: [-3, 2, 3, 4], target = 0 -> [1, 3].
- Target is the sum of the two smallest or two largest.
- Duplicates that form the answer: [1, 2, 2, 3], target = 4 -> [2, 3].
- Very large array (O(n) is essential).

=== INTERVIEW TIPS ===
- The sorted property is the key signal to use two pointers.
- Always explain WHY moving pointers works (sum increases with left, decreases with right).
- Remember the 1-indexed output requirement (add 1 to each index).
- Compare to Two Sum I: hash map vs two pointers based on input properties.
- Follow-up: 3Sum (#15) extends this idea to triplets.
- Binary search alternative shows up if interviewer wants O(1) space without two pointers.
'''

# === SOLUTION ===
from typing import List


def twoSum(numbers: List[int], target: int) -> List[int]:
    """Two-pointer approach exploiting the sorted input: O(n) time, O(1) space."""
    left, right = 0, len(numbers) - 1
    while left < right:
        current_sum = numbers[left] + numbers[right]
        if current_sum == target:
            return [left + 1, right + 1]  # 1-indexed
        elif current_sum < target:
            left += 1  # need a bigger sum
        else:
            right -= 1  # need a smaller sum
    return []  # unreachable; problem guarantees exactly one solution


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert twoSum([2, 7, 11, 15], 9) == [1, 2]
    # Test 2: Non-adjacent indices
    assert twoSum([2, 3, 4], 6) == [1, 3]
    # Test 3: Negative numbers
    assert twoSum([-1, 0], -1) == [1, 2]
    # Test 4: Two elements only
    assert twoSum([5, 5], 10) == [1, 2]
    # Test 5: Larger array
    assert twoSum([1, 3, 4, 5, 7, 10, 11], 9) == [3, 4]
    # Test 6: Answer at the extremes
    assert twoSum([1, 100], 101) == [1, 2]
    print("All tests passed!")
