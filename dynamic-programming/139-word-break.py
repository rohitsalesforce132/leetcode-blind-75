'''
LEETCODE #139: Word Break
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
Given a string s and a dictionary of strings wordDict, return true if s
can be segmented into a space-separated sequence of one or more
dictionary words. The same word may be reused multiple times.

=== INTUITION ===
Define dp[i] = True if s[0:i] can be segmented.
dp[0] = True (empty string).
For each i from 1..n, check every word w: if dp[i-len(w)] and s[i-len(w):i]==w,
then dp[i]=True. Answer = dp[n].

=== APPROACHES ===
Approach 1: Brute Force (Recursion)
- Idea: Try every prefix that's in dict; recurse on suffix.
- Time: O(2^n)
- Space: O(n)

Approach 2: Top-Down DP (Memoization)
- Idea: Cache reachability for each starting index.
- Time: O(n^3) (substring comparisons)
- Space: O(n)

Approach 3: Bottom-Up DP (Tabulation)
- Idea: dp[i] = can s[0:i] be segmented? Build left to right.
- Time: O(n^3)
- Space: O(n)
'''

# === DRY RUN ===
# s = "leetcode", wordDict = ["leet","code"]
# dp = [T,F,F,F,F,F,F,F,F]  (size 9)
# i=4: word "leet" -> dp[0] and s[0:4]=="leet" -> dp[4]=T
# i=8: word "code" -> dp[4] and s[4:8]=="code" -> dp[8]=T
# Answer: True
#
# s = "applepenapple", wordDict=["apple","pen"]
# dp[5]=T (apple), dp[8]=T (apple+pen), dp[13]=T (apple+pen+apple)
# Answer: True

# === COMPLEXITY ANALYSIS ===
# Time: O(n^3) — n positions, n words, each compare O(n)
# Space: O(n)

# === EDGE CASES ===
# s empty -> True; word not covering full string -> False

# === INTERVIEW TIPS ===
# - Convert wordDict to a set for O(1) lookups.
# - Follow-up: Word Break II (return all sentences); Trie optimization.

# === SOLUTION ===

# Approach 1: Brute Force (Recursion) — O(2^n)
def wordBreak_brute(s, wordDict):
    word_set = set(wordDict)

    def helper(start):
        if start == len(s):
            return True
        for end in range(start + 1, len(s) + 1):
            if s[start:end] in word_set and helper(end):
                return True
        return False

    return helper(0)


# Approach 2: Top-Down DP (Memoization) — O(n^3)
def wordBreak_memo(s, wordDict):
    word_set = set(wordDict)
    memo = {}

    def dp(start):
        if start == len(s):
            return True
        if start in memo:
            return memo[start]
        for end in range(start + 1, len(s) + 1):
            if s[start:end] in word_set and dp(end):
                memo[start] = True
                return True
        memo[start] = False
        return False

    return dp(0)


# Approach 3: Bottom-Up DP (Tabulation) — O(n^3)
def wordBreak(s, wordDict):
    word_set = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(1, n + 1):
        for w in wordDict:
            wlen = len(w)
            if i >= wlen and dp[i - wlen] and s[i - wlen:i] == w:
                dp[i] = True
                break
    return dp[n]


# === TEST CASES ===
if __name__ == "__main__":
    assert wordBreak("leetcode", ["leet", "code"]) is True
    assert wordBreak("applepenapple", ["apple", "pen"]) is True
    assert wordBreak("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False
    assert wordBreak("", ["a"]) is True
    assert wordBreak("a", ["a"]) is True
    assert wordBreak_memo("leetcode", ["leet", "code"]) is True
    print("All test cases passed!")
