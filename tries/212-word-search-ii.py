'''
LEETCODE #212: Word Search II
DIFFICULTY: Hard
TOPIC: Tries / Backtracking

=== PROBLEM STATEMENT ===
Given an m x n board of characters and a list of words, find all words on the
board.

Each word must be constructed from letters of sequentially adjacent cells,
where "adjacent" cells are horizontally or vertically neighboring. The same
letter cell may not be used more than once in a word.

=== INTUITION ===
Naive approach: for each word, run DFS on the board. This repeats work across
words that share prefixes.

Better approach: build a trie of ALL words, then do a SINGLE DFS from each
cell on the board, walking the trie simultaneously. This way, shared prefixes
are explored only once. When we hit a word-end node during DFS, we record it.

Optimization: remove/prune trie nodes after a word is found to avoid
redundant searches. Also, mark cells as visited (e.g., with '#') to avoid
reuse during the current path.

=== APPROACHES ===
Approach 1: Brute Force — DFS per Word
- Idea: For each word, run DFS from every cell.
- Time: O(W * M * N * 4^L) where W = number of words, L = max word length.
- Space: O(L) for recursion stack.

Approach 2: Optimal — Trie + DFS Backtracking
- Idea: Build trie from all words, run DFS from each cell following trie paths.
- Time: O(M * N * 4^L) in the worst case, but trie pruning makes it much
  faster in practice.
- Space: O(W * L) for the trie + O(L) for recursion stack.

=== DRY RUN ===
board = [['o','a','a','n'],
         ['e','t','a','e'],
         ['i','h','k','r'],
         ['i','f','l','v']]
words = ["oath", "pea", "eat", "rain"]

Build trie:
  root -> 'o' -> 'a' -> 't' -> 'h'(end)
       -> 'p' -> 'e' -> 'a'(end)
       -> 'e' -> 'a' -> 't'(end)
       -> 'r' -> 'a' -> 'i' -> 'n'(end)

DFS from (0,0)='o':
  'o' in trie -> go to node 'o'
  neighbors: (0,1)='a' -> 'a' in node.children -> go to 'a'
    neighbors: (1,1)='t' -> 't' in children -> go to 't'
      neighbors: (2,1)='h' -> 'h' in children -> is_end! Found "oath"
      Mark cell (2,1), continue exploring... no more matches.
  Backtrack, try other cells...

DFS from (1,0)='e':
  'e' in trie -> go to node 'e'
  neighbors: (1,1)='t' -> 't' not in 'e'.children (only 'a' is)
  neighbors: (0,0)='o' -> not in children
  neighbors: (2,0)='i' -> not in children
  neighbor (0,1)='a' -> 'a' in 'e'.children -> go to 'a'
    neighbors: (0,2)='a' -> 'a' in 'a'.children? No, only 't'.
    neighbors: (1,2)='a' -> same.
    neighbors: (0,0)='o' -> not in children.
    neighbor (0,0)='o' already visited? No, but 'o' not in children.
    neighbor (1,1)='t' -> 't' in 'a'.children -> go to 't'
      is_end! Found "eat"

Result: ["oath", "eat"]

=== COMPLEXITY ANALYSIS ===
Time: O(M * N * 4^L) worst case, but trie pruning dramatically reduces this.
      M*N starting cells, each DFS explores up to 4^L paths.
Space: O(W * L) for the trie + O(L) recursion stack.

=== EDGE CASES ===
- Empty board or empty words list
- Single-cell board
- Words that are prefixes of other words (both should be found)
- Duplicate words in the list
- No words found
- Very long words (deep recursion)

=== INTERVIEW TIPS ===
- The trie is what makes this efficient: instead of searching for each word
  independently, we search for all words simultaneously via shared prefixes.
- Pruning the trie (removing found words' leaf nodes) avoids reporting
  duplicates and speeds up remaining searches.
- Marking the board cell as visited can be done by temporarily changing the
  character (e.g., to '#') and restoring it after the recursive calls. This
  avoids allocating a separate visited matrix.
- Clarify: can words overlap on the board? (Yes, but each cell can only be
  used once per word.)
- The order of directions in DFS doesn't matter for correctness.
- Follow-up: What if the board is huge? (The trie approach still works, but
  consider parallelizing searches or using iterative DFS to avoid stack
  overflow.)
'''

# === SOLUTION ===
from typing import List


class TrieNode:
    """Trie node for Word Search II."""
    def __init__(self):
        self.children = {}
        self.word = None  # Store the complete word at the end node.


class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        """Find all words from the list that exist in the board."""
        # --- Build a trie from all words. ---
        root = TrieNode()
        for word in words:
            node = root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.word = word  # Mark the end node with the complete word.

        ROWS, COLS = len(board), len(board[0])
        result = []

        def dfs(r: int, c: int, node: TrieNode) -> None:
            """Backtracking DFS from board cell (r, c) following trie node."""
            # Bounds check.
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                return

            char = board[r][c]

            # If this character isn't in the trie path, dead end.
            if char not in node.children:
                return

            child = node.children[char]

            # Found a word?
            if child.word:
                result.append(child.word)
                child.word = None  # Avoid duplicate reporting.

            # Mark cell as visited.
            board[r][c] = '#'

            # Explore all 4 directions.
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                dfs(r + dr, c + dc, child)

            # Restore cell.
            board[r][c] = char

            # Pruning: if this child has no children and no word, remove it.
            if not child.children and not child.word:
                del node.children[char]

        # Run DFS from every cell.
        for r in range(ROWS):
            for c in range(COLS):
                dfs(r, c, root)

        return result


# === TEST CASES ===
if __name__ == "__main__":
    sol = Solution()

    # Test 1: standard
    board = [['o', 'a', 'a', 'n'],
             ['e', 't', 'a', 'e'],
             ['i', 'h', 'k', 'r'],
             ['i', 'f', 'l', 'v']]
    words = ["oath", "pea", "eat", "rain"]
    result = sol.findWords(board, words)
    assert sorted(result) == ["eat", "oath"]

    # Test 2: single cell
    board = [['a']]
    words = ["a"]
    assert sol.findWords(board, words) == ["a"]

    # Test 3: no matches
    board = [['a', 'b'], ['c', 'd']]
    words = ["xyz"]
    assert sol.findWords(board, words) == []

    # Test 4: overlapping words
    board = [['o', 'a', 'a', 'n'],
             ['e', 't', 'a', 'e'],
             ['i', 'h', 'k', 'r'],
             ['i', 'f', 'l', 'v']]
    words = ["oath", "oaths"]
    assert sol.findWords(board, words) == ["oath"]  # "oaths" too long

    # Test 5: duplicate words in input
    board = [['a', 'b'], ['c', 'd']]
    words = ["ab", "ab"]
    result = sol.findWords(board, words)
    assert result == ["ab"]  # Should not duplicate

    print("All tests passed!")
