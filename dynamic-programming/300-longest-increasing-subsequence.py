'''
LEETCODE #300: Longest Increasing Subsequence
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
Given an integer array nums, return the length of the longest strictly
increasing subsequence.

=== INTUITION ===
For each index i, look back at all j < i where nums[j] < nums[i].
dp[i] = 1 + max(dp[j] for valid j). Answer = max(dp).
A faster approach uses patience sorting with binary search.

=== APPROACHES ===
Approach 1: Brute Force (Recursion — take/skip)
- Idea: At each element, decide include/exclude; track prev value.
- Time: O(2^n)
- Space: O(n)

Approach 2: Top-Down DP (Memoization)
- Idea: Memoize on (index, prev_index).
- Time: O(n^2)
- Space: O(n^2)

Approach 3a: Bottom-Up DP (Tabulation)
- Idea: dp[i] = longest LIS ending at index i.
- Time: O(n^2)
- Space: O(n)

Approach 3b: Patience Sorting (Binary Search) — OPTIMAL
- Idea: Maintain tails array; binary search insertion point.
- Time: O(n log n)
- Space: O(n)
'''

# === DRY RUN ===
# nums = [10,9,2,5,3,7,101,18]
# dp init = [1]*8
# i=1 (9): j=0 (10) not < 9 -> dp[1]=1
# i=2 (2): no j<2 has val<2 -> dp[2]=1
# i=3 (5): j=2 (2)<5 -> dp[3]=dp[2]+1=2
# i=4 (3): j=2 (2)<3 -> dp[4]=dp[2]+1=2
# i=5 (7): j=3 (5)<7 -> dp[5]=dp[3]+1=3
# i=6 (101): j=5 (7)<101 -> dp[6]=dp[5]+1=4
# i=7 (18): j=5 (7)<18 -> dp[7]=dp[5]+1=4
# Answer: max(dp)=4

# === COMPLEXITY ANALYSIS ===
# DP: O(n^2) time, O(n) space
# Patience: O(n log n) time, O(n) space

# === EDGE CASES ===
# Empty array -> 0; all equal -> 1; strictly decreasing -> 1

# === INTERVIEW TIPS ===
# - Patience sorting is the "wow" answer; explain tails[] carefully.
# - Follow-up: reconstruct the actual subsequence (store parent indices).

# === SOLUTION ===

# Approach 1: Brute Force (Recursion) — O(2^n)
def lengthOfLIS_brute(nums):
    def helper(i, prev_idx):
        if i == len(nums):
            return 0
        # skip current
        skip = helper(i + 1, prev_idx)
        # take current (if strictly increasing)
        take = 0
        if prev_idx == -1 or nums[i] > nums[prev_idx]:
            take = 1 + helper(i + 1, i)
        return max(skip, take)
    return helper(0, -1)


# Approach 2: Top-Down DP (Memoization) — O(n^2)
def lengthOfLIS_memo(nums):
    n = len(nums)
    memo = {}

    def dp(i, prev_idx):
        if i == n:
            return 0
        if (i, prev_idx) in memo:
            return memo[(i, prev_idx)]
        skip = dp(i + 1, prev_idx)
        take = 0
        if prev_idx == -1 or nums[i] > nums[prev_idx]:
            take = 1 + dp(i + 1, i)
        memo[(i, prev_idx)] = max(skip, take)
        return memo[(i, prev_idx)]

    return dp(0, -1)


# Approach 3a: Bottom-Up DP (Tabulation) — O(n^2)
def lengthOfLIS_dp(nums):
    if not nums:
        return 0
    n = len(nums)
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


# Approach 3b: Patience Sorting (Binary Search) — O(n log n)
import bisect


def lengthOfLIS(nums):
    tails = []  # tails[k] = smallest tail of all increasing subsequences of length k+1
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)


# === TEST CASES ===
if __name__ == "__main__":
    assert lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert lengthOfLIS([0, 1, 0, 3, 2, 3]) == 4
    assert lengthOfLIS([7, 7, 7, 7]) == 1
    assert lengthOfLIS([]) == 0
    assert lengthOfLIS([1, 2, 3, 4, 5]) == 5
    assert lengthOfLIS_dp([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert lengthOfLIS_memo([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    print("All test cases passed!")
