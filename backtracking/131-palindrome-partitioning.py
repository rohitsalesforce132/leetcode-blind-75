'''
LEETCODE #131: Palindrome Partitioning
DIFFICULTY: Medium
TOPIC: Backtracking

=== PROBLEM STATEMENT ===
Given a string s, partition s such that every substring of the partition is a
palindrome. Return all possible palindrome partitionings of s.

=== INTUITION ===
1. We need to split the string into contiguous substrings, each a palindrome.
2. Backtracking: at each position, try all possible "cuts" that produce a palindrome.
3. If the prefix s[start..i] is a palindrome, recurse on the suffix s[i+1..].
4. When we've consumed the entire string, we have a valid partition.

=== APPROACHES ===
Approach 1: Backtracking with palindrome check
- Idea: For each start position, try all end positions. If s[start..i] is palindrome,
  add it to current partition and recurse on the rest.
- Time: O(N * 2^N) — up to 2^N partitions, each palindrome check is O(N)
- Space: O(N) recursion depth

Approach 2: Backtracking with DP palindrome table
- Idea: Precompute is_pal[i][j] in O(N^2). Then backtrack using O(1) palindrome checks.
- Time: O(2^N), Space: O(N^2) for DP table

=== DRY RUN ===
s = "aab"

partition(start=0, current=[]):
  i=0: s[0:1]="a" is palindrome -> current=["a"]
    partition(1, ["a"]):
      i=1: s[1:2]="a" is palindrome -> current=["a","a"]
        partition(2, ["a","a"]):
          i=2: s[2:3]="b" is palindrome -> current=["a","a","b"]
            partition(3): start==len(s) -> add ["a","a","b"] to result
      i=2: s[1:3]="ab" not palindrome -> skip
  i=1: s[0:2]="aa" is palindrome -> current=["aa"]
    partition(2, ["aa"]):
      i=2: s[2:3]="b" is palindrome -> current=["aa","b"]
        partition(3): add ["aa","b"] to result
  i=2: s[0:3]="aab" not palindrome -> skip

Result: [["a","a","b"], ["aa","b"]]

=== COMPLEXITY ANALYSIS ===
Time: O(N * 2^N) — worst case "aaa...a", 2^(N-1) partitions, each O(N) to check
Space: O(N) recursion depth

=== EDGE CASES ===
- Single character -> [[s]]
- Entire string is a palindrome -> includes [s] as a partition
- All characters the same -> maximum number of partitions (2^(n-1))
- All characters different -> only partition is individual chars

=== INTERVIEW TIPS ===
- The palindrome check is the bottleneck — mention DP precomputation as optimization.
- Every single character is a palindrome, so there's always at least one partition.
- Follow-up: min cuts for palindrome partitioning (DP problem, LeetCode #132).
- The backtracking pattern: for-loop trying all split points + recursive call.
'''

# === SOLUTION ===

def partition(s):
    """Backtracking with O(N) palindrome check per substring."""
    result = []

    def is_palindrome(sub):
        return sub == sub[::-1]

    def backtrack(start, current):
        if start == len(s):
            result.append(current[:])
            return
        for end in range(start + 1, len(s) + 1):
            prefix = s[start:end]
            if is_palindrome(prefix):
                current.append(prefix)
                backtrack(end, current)
                current.pop()

    backtrack(0, [])
    return result


def partition_dp(s):
    """Backtracking with precomputed DP palindrome table."""
    n = len(s)
    # is_pal[i][j] = True if s[i:j+1] is a palindrome
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n):
        is_pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                if length == 2 or is_pal[i + 1][j - 1]:
                    is_pal[i][j] = True

    result = []

    def backtrack(start, current):
        if start == n:
            result.append(current[:])
            return
        for end in range(start, n):
            if is_pal[start][end]:
                current.append(s[start:end + 1])
                backtrack(end + 1, current)
                current.pop()

    backtrack(0, [])
    return result


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: standard
    print(partition("aab"))  # [["a","a","b"],["aa","b"]]

    # Test 2: single char
    print(partition("a"))  # [["a"]]

    # Test 3: already palindrome
    print(partition("aa"))  # [["a","a"],["aa"]]

    # Test 4: all different
    print(partition("abc"))  # [["a","b","c"]]

    # Test 5: all same
    print(partition("aaa"))
    # [["a","a","a"],["a","aa"],["aa","a"],["aaa"]]

    # Test 6: DP approach
    print(partition_dp("aab"))  # same as test 1
