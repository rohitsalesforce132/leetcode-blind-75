'''
LEETCODE #45: Jump Game II
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
You are given a 0-indexed array of integers nums of length n. You are
initially positioned at nums[0]. Each element represents your maximum
jump length. Return the minimum number of jumps to reach nums[n-1].
It is guaranteed the input is generated such that you can reach the
last index.

=== INTUITION ===
Use BFS-like greedy: track current level range [start, end] and the
farthest reachable from this level. When we exhaust the current level,
we must jump; new level = [end+1, farthest].

=== APPROACHES ===
Approach 1: Brute Force (Recursion)
- Idea: Try all jump lengths at each index; track min jumps.
- Time: O(2^n)
- Space: O(n)

Approach 2: Top-Down DP (Memoization)
- Idea: dp(i) = min jumps from i to end.
- Time: O(n^2)
- Space: O(n)

Approach 3: Greedy BFS (Optimal)
- Idea: Level-by-level expansion; count jumps when moving to next level.
- Time: O(n)
- Space: O(1)
'''

# === DRY RUN ===
# nums = [2,3,1,1,4]
# jumps=0, cur_end=0, farthest=0
# i=0: farthest=max(0,0+2)=2; i==cur_end -> jumps=1, cur_end=2
# i=1: farthest=max(2,1+3)=4; i!=cur_end
# i=2: farthest=max(4,2+1)=4; i==cur_end -> jumps=2, cur_end=4
# i=3: farthest=max(4,3+1)=4; (loop ends before i=4)
# Answer: 2

# === COMPLEXITY ANALYSIS ===
# Time: O(n)
# Space: O(1)

# === EDGE CASES ===
# n=1 -> 0 jumps needed

# === INTERVIEW TIPS ===
# - BFS / greedy level idea mirrors "minimum jumps" problems.
# - Avoid counting a jump at the last index (use range(n-1)).

# === SOLUTION ===

# Approach 1: Brute Force (Recursion) — O(2^n)
def jump_brute(nums):
    n = len(nums)
    res = [float('inf')]

    def helper(i, jumps):
        if i >= n - 1:
            res[0] = min(res[0], jumps)
            return
        for k in range(1, nums[i] + 1):
            helper(i + k, jumps + 1)
    helper(0, 0)
    return res[0]


# Approach 2: Top-Down DP (Memoization) — O(n^2)
def jump_memo(nums):
    n = len(nums)
    memo = {}

    def dp(i):
        if i >= n - 1:
            return 0
        if i in memo:
            return memo[i]
        best = float('inf')
        for k in range(1, nums[i] + 1):
            best = min(best, 1 + dp(i + k))
        memo[i] = best
        return best

    return dp(0)


# Approach 3: Greedy BFS — O(n), O(1) space
def jump(nums):
    n = len(nums)
    if n <= 1:
        return 0
    jumps = 0
    cur_end = 0
    farthest = 0
    for i in range(n - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
            if cur_end >= n - 1:
                break
    return jumps


# === TEST CASES ===
if __name__ == "__main__":
    assert jump([2, 3, 1, 1, 4]) == 2
    assert jump([2, 3, 0, 1, 4]) == 2
    assert jump([0]) == 0
    assert jump([1, 1, 1, 1]) == 3
    assert jump([1, 2]) == 1
    assert jump_memo([2, 3, 1, 1, 4]) == 2
    print("All test cases passed!")
