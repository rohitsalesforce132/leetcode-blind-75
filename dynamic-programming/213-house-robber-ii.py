'''
LEETCODE #213: House Robber II
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
You are a professional robber planning to rob houses along a street.
Each house has a certain amount of money stashed. All houses at this
place are arranged in a circle — the first house is the neighbor of
the last one. Adjacent houses cannot be robbed on the same night.

Given an integer array nums representing money in each house, return
the maximum amount you can rob tonight without alerting the police.

=== INTUITION ===
Since first and last are adjacent, you can NEVER rob both.
So split into two linear cases:
  Case A: rob houses [0 .. n-2]  (exclude last)
  Case B: rob houses [1 .. n-1]  (exclude first)
Answer = max(Case A, Case B). Each case reduces to House Robber I.

=== APPROACHES ===
Approach 1: Brute Force (Recursion)
- Idea: Try all subsets without adjacent picks; check circular constraint.
- Time: O(2^n)
- Space: O(n)

Approach 2: Top-Down DP (Memoization)
- Idea: Memoize the linear robber helper on each slice.
- Time: O(n)
- Space: O(n)

Approach 3: Bottom-Up DP (Tabulation)
- Idea: Run linear robber on [0..n-2] and [1..n-1], take max.
- Time: O(n)
- Space: O(1)
'''

# === DRY RUN ===
# nums = [2,3,2]
# Case A: [2,3] -> max(2,3)=3
# Case B: [3,2] -> max(3,2)=3
# Answer: 3
#
# nums = [1,2,3,1]
# Case A: [1,2,3] -> rob_linear=4 (houses 1 and 3)
# Case B: [2,3,1] -> rob_linear=3 (houses 2 and 1)
# Answer: 4

# === COMPLEXITY ANALYSIS ===
# Time: O(n)
# Space: O(1)

# === EDGE CASES ===
# Single house -> nums[0]; empty -> 0

# === INTERVIEW TIPS ===
# - Key insight: break the circle by excluding one end.
# - Don't double-count; if n==1, don't slice into two empty arrays.

# === SOLUTION ===

# Linear House Robber (O(1) space) — reused helper
def _rob_linear(nums):
    prev2, prev1 = 0, 0
    for num in nums:
        curr = max(prev1, prev2 + num)
        prev2, prev1 = prev1, curr
    return prev1


# Approach 1: Brute Force (Recursion) — O(2^n)
def rob_brute(nums):
    def helper(arr, i):
        if i < 0:
            return 0
        return max(helper(arr, i - 1), helper(arr, i - 2) + arr[i])
    if len(nums) == 1:
        return nums[0]
    return max(helper(nums[:-1], len(nums) - 2),
               helper(nums[1:], len(nums) - 2))


# Approach 2: Top-Down DP (Memoization) — O(n)
def rob_memo(nums):
    if len(nums) == 1:
        return nums[0]
    memo = {}

    def dp(arr, i):
        if i < 0:
            return 0
        if (id(arr), i) in memo:
            return memo[(id(arr), i)]
        memo[(id(arr), i)] = max(dp(arr, i - 1), dp(arr, i - 2) + arr[i])
        return memo[(id(arr), i)]

    return max(dp(nums[:-1], len(nums) - 2),
               dp(nums[1:], len(nums) - 2))


# Approach 3: Bottom-Up DP (Tabulation) — O(n), O(1) space
def rob(nums):
    if len(nums) == 1:
        return nums[0]
    return max(_rob_linear(nums[:-1]), _rob_linear(nums[1:]))


# === TEST CASES ===
if __name__ == "__main__":
    assert rob([2, 3, 2]) == 3
    assert rob([1, 2, 3, 1]) == 4
    assert rob([1, 2, 3]) == 3
    assert rob([1]) == 1
    assert rob([0, 0, 0, 0]) == 0
    assert rob([2, 3]) == 3
    print("All test cases passed!")
