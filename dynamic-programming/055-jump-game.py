'''
LEETCODE #55: Jump Game
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
You are given an integer array nums. You are initially positioned at
the array's first index, and each element represents your maximum
jump length at that position. Return true if you can reach the last
index, or false otherwise.

=== INTUITION ===
Track the farthest index reachable so far. Iterate left to right;
if current index i is beyond the farthest reachable, we're stuck -> false.
Otherwise update farthest = max(farthest, i + nums[i]).
If farthest reaches last index -> true.

=== APPROACHES ===
Approach 1: Brute Force (Recursion with backtracking)
- Idea: Try every jump length 0..nums[i] at each position.
- Time: O(2^n) worst case
- Space: O(n)

Approach 2: Top-Down DP (Memoization)
- Idea: Memoize reachability from each index (GOOD/BAD/UNKNOWN).
- Time: O(n^2)
- Space: O(n)

Approach 3: Bottom-Up DP / Greedy (Tabulation)
- Idea: Greedily track farthest reachable index.
- Time: O(n)
- Space: O(1)
'''

# === DRY RUN ===
# nums = [2,3,1,1,4]
# i=0: farthest = max(0, 0+2) = 2
# i=1: 1<=2 ok, farthest = max(2, 1+3) = 4  -> reaches last index -> TRUE
#
# nums = [3,2,1,0,4]
# i=0: farthest=3
# i=1: farthest=3
# i=2: farthest=3
# i=3: farthest=3 (can't advance past 0)
# i=4: 4 > 3 -> unreachable -> FALSE

# === COMPLEXITY ANALYSIS ===
# Time: O(n)
# Space: O(1)

# === EDGE CASES ===
# Single element -> True; nums[0]=0 and n>1 -> False

# === INTERVIEW TIPS ===
# - Greedy is optimal here; DP is overkill but good to explain.
# - Follow-up: Jump Game II (min number of jumps).

# === SOLUTION ===

# Approach 1: Brute Force (Recursion) — O(2^n)
def canJump_brute(nums):
    def helper(i):
        if i >= len(nums) - 1:
            return True
        for j in range(1, nums[i] + 1):
            if helper(i + j):
                return True
        return False
    return helper(0)


# Approach 2: Top-Down DP (Memoization) — O(n^2)
def canJump_memo(nums):
    n = len(nums)
    memo = {}

    def dp(i):
        if i >= n - 1:
            return True
        if i in memo:
            return memo[i]
        for j in range(1, nums[i] + 1):
            if dp(i + j):
                memo[i] = True
                return True
        memo[i] = False
        return False

    return dp(0)


# Approach 3: Greedy / Bottom-Up — O(n), O(1)
def canJump(nums):
    farthest = 0
    for i in range(len(nums)):
        if i > farthest:
            return False
        farthest = max(farthest, i + nums[i])
        if farthest >= len(nums) - 1:
            return True
    return True


# === TEST CASES ===
if __name__ == "__main__":
    assert canJump([2, 3, 1, 1, 4]) is True
    assert canJump([3, 2, 1, 0, 4]) is False
    assert canJump([0]) is True
    assert canJump([0, 1]) is False
    assert canJump([2, 0, 0]) is True
    assert canJump_memo([3, 2, 1, 0, 4]) is False
    print("All test cases passed!")
