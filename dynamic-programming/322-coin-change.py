'''
LEETCODE #322: Coin Change
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
You are given an integer array coins representing coins of different
denominations and an integer amount representing a total amount of money.
Return the fewest number of coins needed to make up that amount. If that
amount cannot be made, return -1. You may use each coin unlimited times.

=== INTUITION ===
dp[a] = minimum coins needed to make amount a.
Base: dp[0] = 0.
For each amount a from 1..amount, for each coin c:
  if a >= c: dp[a] = min(dp[a], 1 + dp[a - c])
Answer = dp[amount], or -1 if still infinity.

=== APPROACHES ===
Approach 1: Brute Force (Recursion)
- Idea: For each amount, try every coin; recurse on remaining amount.
- Time: O(amount^coins) exponential
- Space: O(amount)

Approach 2: Top-Down DP (Memoization)
- Idea: Cache min coins for each amount.
- Time: O(amount * len(coins))
- Space: O(amount)

Approach 3: Bottom-Up DP (Tabulation)
- Idea: Build dp[0..amount] iteratively.
- Time: O(amount * len(coins))
- Space: O(amount)
'''

# === DRY RUN ===
# coins=[1,2,5], amount=11
# dp=[0,inf,inf,...,inf]  (size 12)
# a=1: dp[1]=min(inf,1+dp[0])=1
# a=2: dp[2]=min(dp[2],1+dp[1])=2, then 1+dp[0]=1 -> dp[2]=1
# a=3: dp[3]=2 (1+dp[2])
# a=4: dp[4]=2 (1+dp[2])
# a=5: dp[5]=1 (1+dp[0])
# a=6: dp[6]=2 (1+dp[5])
# ...continuing...
# a=11: dp[11]=3 (1+dp[10]=1+2=3)
# Answer: 3  (5+5+1)

# === COMPLEXITY ANALYSIS ===
# Time: O(amount * len(coins))
# Space: O(amount)

# === EDGE CASES ===
# amount=0 -> 0; impossible amount -> -1; single coin divides amount

# === INTERVIEW TIPS ===
# - Mention BFS alternative (shortest path in unweighted graph).
# - Follow-up: Coin Change II (count number of combinations).

# === SOLUTION ===

# Approach 1: Brute Force (Recursion) — exponential
def coinChange_brute(coins, amount):
    def helper(a):
        if a == 0:
            return 0
        if a < 0:
            return float('inf')
        best = float('inf')
        for c in coins:
            best = min(best, 1 + helper(a - c))
        return best
    res = helper(amount)
    return res if res != float('inf') else -1


# Approach 2: Top-Down DP (Memoization) — O(amount * coins)
def coinChange_memo(coins, amount):
    memo = {}

    def dp(a):
        if a == 0:
            return 0
        if a < 0:
            return float('inf')
        if a in memo:
            return memo[a]
        best = float('inf')
        for c in coins:
            best = min(best, 1 + dp(a - c))
        memo[a] = best
        return best

    res = dp(amount)
    return res if res != float('inf') else -1


# Approach 3: Bottom-Up DP (Tabulation) — O(amount * coins)
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if a >= c:
                dp[a] = min(dp[a], 1 + dp[a - c])
    return dp[amount] if dp[amount] != float('inf') else -1


# === TEST CASES ===
if __name__ == "__main__":
    assert coinChange([1, 2, 5], 11) == 3
    assert coinChange([2], 3) == -1
    assert coinChange([1], 0) == 0
    assert coinChange([1], 2) == 2
    assert coinChange([1, 3, 4], 6) == 2
    assert coinChange_memo([1, 2, 5], 11) == 3
    print("All test cases passed!")
