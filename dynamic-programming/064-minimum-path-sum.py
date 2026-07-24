'''
LEETCODE #64: Minimum Path Sum
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
Given a m x n grid filled with non-negative numbers, find a path from
top left corner to the bottom right corner which minimizes the sum of
all numbers along its path. You can only move either down or right.

=== INTUITION ===
At cell (i,j), the minimum path sum = grid[i][j] + min(from above, from left).
Top row can only come from left; left column can only come from above.
Fill DP table row by row.

=== APPROACHES ===
Approach 1: Brute Force (Recursion)
- Idea: Explore all paths down/right.
- Time: O(2^(m+n))
- Space: O(m+n)

Approach 2: Top-Down DP (Memoization)
- Idea: Memoize min path from (i,j) to bottom-right.
- Time: O(m*n)
- Space: O(m*n)

Approach 3: Bottom-Up DP (Tabulation)
- Idea: Fill DP grid in place; dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1]).
- Time: O(m*n)
- Space: O(1) in place, or O(m*n) with separate grid
'''

# === DRY RUN ===
# grid = [[1,3,1],[1,5,1],[4,2,1]]
# Row 0: [1, 1+3=4, 4+1=5]
# Row 1: [1+1=2, min(4,2)+5=7, min(5,7)+1=6]
# Row 2: [2+4=6, min(7,6)+2=8, min(6,8)+1=7]
# Answer: 7

# === COMPLEXITY ANALYSIS ===
# Time: O(m*n)
# Space: O(1) in place

# === EDGE CASES ===
# 1x1 grid -> grid[0][0]; single row/column

# === INTERVIEW TIPS ===
# - In-place modification saves space but ask the interviewer if allowed.
# - Space optimization to O(n) using rolling row is a common follow-up.

# === SOLUTION ===

# Approach 1: Brute Force (Recursion) — O(2^(m+n))
def minPathSum_brute(grid):
    m, n = len(grid), len(grid[0])

    def helper(i, j):
        if i == m - 1 and j == n - 1:
            return grid[i][j]
        if i >= m or j >= n:
            return float('inf')
        return grid[i][j] + min(helper(i + 1, j), helper(i, j + 1))

    return helper(0, 0)


# Approach 2: Top-Down DP (Memoization) — O(m*n)
def minPathSum_memo(grid):
    m, n = len(grid), len(grid[0])
    memo = {}

    def dp(i, j):
        if i == m - 1 and j == n - 1:
            return grid[i][j]
        if i >= m or j >= n:
            return float('inf')
        if (i, j) in memo:
            return memo[(i, j)]
        memo[(i, j)] = grid[i][j] + min(dp(i + 1, j), dp(i, j + 1))
        return memo[(i, j)]

    return dp(0, 0)


# Approach 3: Bottom-Up DP (Tabulation) — O(m*n), in-place
def minPathSum(grid):
    m, n = len(grid), len(grid[0])
    # First row
    for j in range(1, n):
        grid[0][j] += grid[0][j - 1]
    # First column
    for i in range(1, m):
        grid[i][0] += grid[i - 1][0]
    # Rest of grid
    for i in range(1, m):
        for j in range(1, n):
            grid[i][j] += min(grid[i - 1][j], grid[i][j - 1])
    return grid[m - 1][n - 1]


# === TEST CASES ===
if __name__ == "__main__":
    assert minPathSum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    assert minPathSum([[1, 2, 3], [4, 5, 6]]) == 12
    assert minPathSum([[5]]) == 5
    assert minPathSum([[1, 2], [1, 1]]) == 3
    assert minPathSum_memo([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    print("All test cases passed!")
