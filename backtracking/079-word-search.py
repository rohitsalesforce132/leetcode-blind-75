'''
LEETCODE #79: Word Search
DIFFICULTY: Medium
TOPIC: Backtracking

=== PROBLEM STATEMENT ===
Given an m x n grid of characters `board` and a string `word`, return true if
word exists in the grid. The word can be constructed from letters of sequentially
adjacent cells, where "adjacent" cells are horizontally or vertically neighboring.
The same letter cell may not be used more than once.

=== INTUITION ===
1. This is a grid-based backtracking / DFS problem.
2. For each cell matching the first letter of `word`, start a DFS.
3. From there, explore 4 directions. Mark the current cell as visited (temporarily).
4. If any path matches the entire word, return true.
5. Backtrack: restore the cell after exploring (so other paths can use it).

=== APPROACHES ===
Approach 1: DFS + Backtracking (Standard)
- Idea: For each starting cell, DFS matching word character by character.
- Time: O(N * 4^L) where N = number of cells, L = word length
- Space: O(L) recursion depth

Approach 2: Trie-based (for searching multiple words — not needed for single word)
- Idea: Build a trie of words, DFS through grid.
- Time: O(N * 4^L), Space: O(W * L) for trie

=== DRY RUN ===
board = [['A','B','C','E'],
         ['S','F','C','S'],
         ['A','D','E','E']]
word = "ABCCED"

Start search from (0,0) = 'A' (matches word[0]):
  dfs(0,0,0): board='A'==word[0], mark visited
    try (0,1)='B'==word[1] -> dfs(0,1,1):
      try (0,2)='C'==word[2] -> dfs(0,2,2):
        try (0,3)='E'!=word[3]='C' -> fail
        try (1,2)='C'==word[3] -> dfs(1,2,3):
          try (2,2)='E'==word[4] -> dfs(2,2,4):
            try (2,1)='D'==word[5] -> dfs(2,1,5):
              index 5 == len(word)-1 -> FOUND!
Return True

=== COMPLEXITY ANALYSIS ===
Time: O(N * 4^L) — N cells, each DFS branches up to 4 directions, depth L
Space: O(L) recursion depth

=== EDGE CASES ===
- Single cell board, single char word
- Word longer than total cells -> impossible
- Repeated characters in word
- Word not present
- Board with all same characters

=== INTERVIEW TIPS ===
- The "mark and restore" technique is key: temporarily change board[r][c] to a
  sentinel (like '#') to mark visited, restore after recursion.
- Avoid using a separate visited set — modifying the board in-place is cleaner.
- Optimization: check character frequency first. If the board has fewer of a
  char than needed, return False immediately.
- Optimization: if the word starts with a rarer character, reverse the word
  to prune faster.
- Follow-up: Word Search II (#212) — search multiple words using a Trie.
'''

# === SOLUTION ===

def exist(board, word):
    """DFS with backtracking on the grid."""
    rows, cols = len(board), len(board[0])

    def dfs(r, c, idx):
        # Base case: matched all characters
        if idx == len(word):
            return True
        # Out of bounds or mismatch or already visited
        if (r < 0 or r >= rows or c < 0 or c >= cols or
                board[r][c] != word[idx]):
            return False
        # Mark as visited (temporarily)
        temp = board[r][c]
        board[r][c] = '#'
        # Explore 4 directions
        found = (dfs(r + 1, c, idx + 1) or
                 dfs(r - 1, c, idx + 1) or
                 dfs(r, c + 1, idx + 1) or
                 dfs(r, c - 1, idx + 1))
        # Restore (backtrack)
        board[r][c] = temp
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False


# === TEST CASES ===
if __name__ == "__main__":
    board = [['A', 'B', 'C', 'E'],
             ['S', 'F', 'C', 'S'],
             ['A', 'D', 'E', 'E']]

    # Test 1: word exists
    print(exist(board, "ABCCED"))  # True

    # Test 2: word exists
    print(exist(board, "SEE"))  # True

    # Test 3: word doesn't exist
    print(exist(board, "ABCB"))  # False

    # Test 4: single char
    print(exist([['A']], "A"))  # True

    # Test 5: word longer than cells
    print(exist([['A']], "AB"))  # False

    # Test 6: repeated characters
    board2 = [['A', 'A'], ['A', 'A']]
    print(exist(board2, "AAAA"))  # True
