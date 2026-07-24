'''
LEETCODE #238: Product of Array Except Self
DIFFICULTY: Medium
TOPIC: Arrays & Hashing

=== PROBLEM STATEMENT ===
Given an integer array nums, return an array answer such that answer[i] is
equal to the product of all the elements of nums except nums[i].

The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit
integer. You must write an algorithm that runs in O(n) time and without using
the division operation.

Example 1: Input: nums = [1,2,3,4]       Output: [24,12,8,6]
Example 2: Input: nums = [-1,1,0,-3,3]   Output: [0,0,9,0,0]

=== INTUITION ===
- answer[i] = (product of everything left of i) * (product of everything right of i)
- We can compute prefix products left-to-right, then suffix products right-to-left.
- Combine: answer[i] = prefix[i] * suffix[i].
- Optimization: do it in-place in the answer array to achieve O(1) extra space.
- Division is banned, so we cannot simply compute totalProduct / nums[i].

=== APPROACHES ===
Approach 1: Prefix and Suffix Arrays
- Idea: Build prefix[] (product of all elements to the left) and suffix[]
        (product of all elements to the right); answer[i] = prefix[i] * suffix[i].
- Time: O(n)
- Space: O(n) for the two arrays.

Approach 2: Single Output Array - OPTIMAL
- Idea: First pass left-to-right stores prefix products in answer[].
        Second pass right-to-left multiplies by running suffix product.
- Time: O(n)
- Space: O(1) extra (output array doesn't count toward space complexity per problem).

=== DRY RUN ===
nums = [1, 2, 3, 4]

First pass (left to right): store prefix (product of all to the left)
  i=0: answer[0] = prefix_so_far = 1;   prefix_so_far = 1 * 1 = 1
  i=1: answer[1] = prefix_so_far = 1;   prefix_so_far = 1 * 2 = 2
  i=2: answer[2] = prefix_so_far = 2;   prefix_so_far = 2 * 3 = 6
  i=3: answer[3] = prefix_so_far = 6;   prefix_so_far = 6 * 4 = 24
  answer = [1, 1, 2, 6]

Second pass (right to left): multiply by suffix (product of all to the right)
  suffix_so_far = 1
  i=3: answer[3] = 6 * 1 = 6;   suffix_so_far = 1 * 4 = 4
  i=2: answer[2] = 2 * 4 = 8;   suffix_so_far = 4 * 3 = 12
  i=1: answer[1] = 1 * 12 = 12; suffix_so_far = 12 * 2 = 24
  i=0: answer[0] = 1 * 24 = 24; suffix_so_far = 24 * 1 = 24
  answer = [24, 12, 8, 6]

Result: [24, 12, 8, 6]  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - two linear passes.
Space: O(1) extra (only the output array; doesn't count per problem statement).

=== EDGE CASES ===
- Array containing zeros: a single zero makes every other entry 0;
  two or more zeros makes ALL entries 0.
- Array containing negative numbers: sign tracking matters.
- Single element array (conceptually answer = [1] but constraint n >= 2).
- All elements are 1.
- Very large products (guaranteed to fit 32-bit per problem).

=== INTERVIEW TIPS ===
- State the constraint clearly: O(n) time, NO division.
- The key insight: product except self = prefix product * suffix product.
- Explain the in-place optimization to reduce space from O(n) to O(1).
- Walk through the two-pass approach on a whiteboard; interviewers love this.
- Follow-up: What if division were allowed? -> count zeros; O(n) one pass.
- Follow-up: What about overflow? -> problem guarantees 32-bit fit; in general use longs.
'''

# === SOLUTION ===
from typing import List


def productExceptSelf(nums: List[int]) -> List[int]:
    """Two-pass in-place approach using the output array."""
    n = len(nums)
    answer = [1] * n

    # First pass: prefix products (left to right)
    prefix = 1
    for i in range(n):
        answer[i] = prefix
        prefix *= nums[i]

    # Second pass: multiply by suffix products (right to left)
    suffix = 1
    for i in range(n - 1, -1, -1):
        answer[i] *= suffix
        suffix *= nums[i]

    return answer


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert productExceptSelf([1, 2, 3, 4]) == [24, 12, 8, 6]
    # Test 2: Contains a zero
    assert productExceptSelf([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
    # Test 2b: Contains two zeros -> all zeros
    assert productExceptSelf([0, 0]) == [0, 0]
    # Test 3: Two elements
    assert productExceptSelf([3, 2]) == [2, 3]
    # Test 4: All ones
    assert productExceptSelf([1, 1, 1, 1]) == [1, 1, 1, 1]
    # Test 5: Negative numbers
    assert productExceptSelf([-1, -2, -3, -4]) == [-24, -12, -8, -6]
    print("All tests passed!")
