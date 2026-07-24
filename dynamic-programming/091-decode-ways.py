'''
LEETCODE #91: Decode Ways
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
A message containing letters from A-Z can be encoded into numbers using
the mapping 'A'->1, 'B'->2, ..., 'Z'->26. Given a string s containing
only digits, return the number of ways to decode it.

=== INTUITION ===
At position i, we can decode:
  1. A single digit s[i] (valid if '1'..'9')
  2. A two-digit number s[i-1:i+1] (valid if '10'..'26')
dp[i] = number of ways to decode s[0:i].
Transition: dp[i] = (valid single ? dp[i-1] : 0) + (valid pair ? dp[i-2] : 0)

=== APPROACHES ===
Approach 1: Brute Force (Recursion)
- Idea: At each index, try 1-digit and 2-digit decodings.
- Time: O(2^n)
- Space: O(n)

Approach 2: Top-Down DP (Memoization)
- Idea: Cache number of decodings from each index.
- Time: O(n)
- Space: O(n)

Approach 3: Bottom-Up DP (Tabulation)
- Idea: dp[i] = ways to decode s[:i]; O(1) space with two variables.
- Time: O(n)
- Space: O(1)
'''

# === DRY RUN ===
# s = "226"
# dp[0]=1 (empty), dp[1]=1 ('2' valid)
# i=2: single='2' valid -> +dp[1]=1; pair="22" valid -> +dp[0]=1; dp[2]=2
# i=3: single='6' valid -> +dp[2]=2; pair="26" valid -> +dp[1]=1; dp[3]=3
# Answer: 3  ("BBF","BZ","VF")
#
# s = "06"
# i=1: single='0' INVALID; pair="06" invalid (leading 0); dp[1]=0
# Answer: 0

# === COMPLEXITY ANALYSIS ===
# Time: O(n)
# Space: O(1)

# === EDGE CASES ===
# Leading zero -> 0 ways; empty string -> 1 (convention); '10','20' valid

# === INTERVIEW TIPS ===
# - Off-by-one: be careful with indices for two-digit check.
# - Common follow-up: decode with '*' wildcard (LC #639).

# === SOLUTION ===

# Approach 1: Brute Force (Recursion) — O(2^n)
def numDecodings_brute(s):
    def helper(i):
        if i == len(s):
            return 1
        if s[i] == '0':
            return 0
        ways = helper(i + 1)  # single digit
        if i + 1 < len(s) and 10 <= int(s[i:i + 2]) <= 26:
            ways += helper(i + 2)  # two digits
        return ways
    return helper(0)


# Approach 2: Top-Down DP (Memoization) — O(n)
def numDecodings_memo(s):
    memo = {}
    n = len(s)

    def dp(i):
        if i == n:
            return 1
        if s[i] == '0':
            return 0
        if i in memo:
            return memo[i]
        ways = dp(i + 1)
        if i + 1 < n and 10 <= int(s[i:i + 2]) <= 26:
            ways += dp(i + 2)
        memo[i] = ways
        return ways

    return dp(0)


# Approach 3: Bottom-Up DP (Tabulation) — O(n), O(1)
def numDecodings(s):
    n = len(s)
    if n == 0 or s[0] == '0':
        return 0
    prev2, prev1 = 1, 1  # dp[i-2], dp[i-1]; dp[0]=1
    for i in range(1, n):
        curr = 0
        # Single digit decode
        if s[i] != '0':
            curr += prev1
        # Two digit decode
        two_digit = int(s[i - 1:i + 1])
        if 10 <= two_digit <= 26:
            curr += prev2
        prev2, prev1 = prev1, curr
    return prev1


# === TEST CASES ===
if __name__ == "__main__":
    assert numDecodings("12") == 2
    assert numDecodings("226") == 3
    assert numDecodings("06") == 0
    assert numDecodings("0") == 0
    assert numDecodings("11106") == 2
    assert numDecodings("10") == 1
    assert numDecodings_memo("226") == 3
    print("All test cases passed!")
