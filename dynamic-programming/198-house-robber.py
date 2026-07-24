'''
LEETCODE #198: House Robber
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
You are a professional robber planning to rob houses along a street.
Each house has a certain amount of money stashed; the only constraint
stopping you from robbing each of them is that adjacent houses have
security systems connected, and it will automatically contact the
police if two adjacent houses are broken into on the same night.

Given an integer array nums representing the amount of money of each
house, return the maximum amount of money you can rob tonight without
alerting the police.

=== INTUITION ===
At each house i, you have two choices:
  1. Skip it -> loot = dp[i-1]
  2. Rob it   -> loot = dp[i-2] + nums[i]
Take the max of the two.

=== APPROACHES ===
Approach 1: Brute Force (Recursion)
- Idea: For each house, try rob/skip and recurse.
- Time: O(2^n)
- Space: O(n)

Approach 2: Top-Down DP (Memoization)
- Idea: Cache max loot from index i onward.
- Time: O(n)
- Space: O(n)

Approach 3: Bottom-Up DP (Tabulation)
- Idea: Build dp array left to right, O(1) space variant.
- Time: O(n)
- Space: O(1)
'''

# === DRY RUN ===
# nums = [2,7,9,3,1]
# dp[0] = 2
# dp[1] = max(2,7) = 7
# dp[2] = max(7, 2+9) = 11
# dp[3] = max(11, 7+3) = 11
# dp[4] = max(11, 11+1) = 12
# Answer: 12

# === COMPLEXITY ANALYSIS ===
# Time: O(n)
# Space: O(1)

# === EDGE CASES ===
# Empty list -> 0; single house -> nums[0]

# === INTERVIEW TIPS ===
# - Circular variant = House Robber II; tree variant = common follow-up.
# - Common pitfall: dp[i-2] must be the best up to i-2, not nums[i-2].

# === SOLUTION ===

# Approach 1: Brute Force (Recursion) — O(2^n)
def rob_brute(nums):
    def helper(i):
        if i < 0:
            return 0
        return max(helper(i - 1), helper(i - 2) + nums[i])
    return helper(len(nums) - 1)


# Approach 2: Top-Down DP (Memoization) — O(n)
def rob_memo(nums):
    memo = {}

    def dp(i):
        if i < 0:
            return 0
        if i in memo:
            return memo[i]
        memo[i] = max(dp(i - 1), dp(i - 2) + nums[i])
        return memo[i]

    return dp(len(nums) - 1)


# Approach 3: Bottom-Up DP (Tabulation) — O(n), O(1) space
def rob(nums):
    prev2, prev1 = 0, 0  # dp[i-2], dp[i-1]
    for num in nums:
        curr = max(prev1, prev2 + num)
        prev2, prev1 = prev1, curr
    return prev1


# === TEST CASES ===
if __name__ == "__main__":
    assert rob([1, 2, 3, 1]) == 4
    assert rob([2, 7, 9, 3, 1]) == 12
    assert rob([2, 1, 1, 2]) == 4
    assert rob([]) == 0
    assert rob([5]) == 5
    assert rob_memo([2, 7, 9, 3, 1]) == 12
    print("All test cases passed!")
