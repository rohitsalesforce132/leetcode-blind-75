'''
LEETCODE #70: Climbing Stairs
DIFFICULTY: Easy
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
You are climbing a staircase. It takes n steps to reach the top.
Each time you can either climb 1 or 2 steps. In how many distinct
ways can you climb to the top?

=== INTUITION ===
At step i, you arrived either from step i-1 (1 step) or step i-2 (2 steps).
So ways(i) = ways(i-1) + ways(i-2). This is the Fibonacci recurrence!

=== APPROACHES ===
Approach 1: Brute Force (Recursion)
- Idea: Explore every choice (1 or 2 steps) at each step.
- Time: O(2^n) — branching tree
- Space: O(n) — recursion stack

Approach 2: Top-Down DP (Memoization)
- Idea: Cache results of the recursion.
- Time: O(n)
- Space: O(n)

Approach 3: Bottom-Up DP (Tabulation)
- Idea: Build the answer from base cases up.
- Time: O(n)
- Space: O(1) — only track two values
'''

# === DRY RUN ===
# n = 5
# dp[0]=1, dp[1]=1
# dp[2] = dp[1]+dp[0] = 2
# dp[3] = dp[2]+dp[1] = 3
# dp[4] = dp[3]+dp[2] = 5
# dp[5] = dp[4]+dp[3] = 8
# Answer: 8

# === COMPLEXITY ANALYSIS ===
# Time: O(n)
# Space: O(1)

# === EDGE CASES ===
# n = 1 -> 1; n = 2 -> 2; n = 0 -> 1 (by convention)

# === INTERVIEW TIPS ===
# - Recognize Fibonacci pattern; mention matrix exponentiation for O(log n).
# - Ask about overflow for very large n.

# === SOLUTION ===

# Approach 1: Brute Force (Recursion) — O(2^n)
def climbStairs_brute(n):
    if n <= 1:
        return 1
    return climbStairs_brute(n - 1) + climbStairs_brute(n - 2)


# Approach 2: Top-Down DP (Memoization) — O(n)
def climbStairs_memo(n):
    memo = {}

    def dp(i):
        if i <= 1:
            return 1
        if i in memo:
            return memo[i]
        memo[i] = dp(i - 1) + dp(i - 2)
        return memo[i]

    return dp(n)


# Approach 3: Bottom-Up DP (Tabulation) — O(n), O(1) space
def climbStairs(n):
    if n <= 2:
        return n
    prev2, prev1 = 1, 1  # ways(0), ways(1)
    for i in range(2, n + 1):
        curr = prev1 + prev2
        prev2, prev1 = prev1, curr
    return prev1


# === TEST CASES ===
if __name__ == "__main__":
    assert climbStairs(1) == 1
    assert climbStairs(2) == 2
    assert climbStairs(3) == 3
    assert climbStairs(4) == 5
    assert climbStairs(5) == 8
    assert climbStairs(10) == 89
    assert climbStairs_memo(5) == 8
    assert climbStairs_memo(10) == 89
    print("All test cases passed!")
