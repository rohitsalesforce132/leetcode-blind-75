'''
LEETCODE #36: Valid Sudoku
DIFFICULTY: Medium
TOPIC: Arrays & Hashing

=== PROBLEM STATEMENT ===
Determine if a 9 x 9 Sudoku board is valid. Only the filled cells need to be
validated according to the following rules:
  1. Each row must contain the digits 1-9 without repetition.
  2. Each column must contain the digits 1-9 without repetition.
  3. Each of the nine 3 x 3 sub-boxes must contain the digits 1-9 without repetition.
A partially filled board is valid if it does not violate any rule above.

Note: A Sudoku board (a partially filled) is valid, but not necessarily solvable.
Only filled cells are validated. '.' denotes an empty cell.

Example 1: Valid board -> true
Example 2: Invalid (duplicate 6 in top-left 3x3 box) -> false

=== INTUITION ===
- We only check validity of FILLED cells, not solvability.
- For each filled cell, track what's been seen in its row, column, and 3x3 box.
- If any constraint is violated (a digit repeats in row/col/box), return False.
- Hash sets per row/col/box give O(1) lookups.
- Box index for cell (r, c) = (r // 3) * 3 + (c // 3).

=== APPROACHES ===
Approach 1: Three Separate Hash Sets (Rows, Columns, Boxes)
- Idea: Maintain sets for rows, cols, boxes; one pass over the board.
- Time: O(1) since board is always 9x9 (constant 81 cells). O(n^2) for general n x n.
- Space: O(1) (at most 9*9=81 entries across all sets).

Approach 2: Single Pass with Encoded Tuples as Keys
- Idea: Use a set of tuples ("row", r, digit), ("col", c, digit), ("box", b, digit).
        If any tuple already exists, invalid. One elegant set does everything.
- Time: O(1)
- Space: O(1)

=== DRY RUN ===
Board (abbreviated):
  ["5","3",".",".","7",".",".",".","."]
  ["6",".",".","1","9","5",".",".","."]
  [".","9","8",".",".",".",".","6","."]
  ["8",".",".",".","6",".",".",".","3"]
  ["4",".",".","8",".","3",".",".","1"]
  ["7",".",".",".","2",".",".",".","6"]
  [".","6",".",".",".",".","2","8","."]
  [".",".",".","4","1","9",".",".","5"]
  [".",".",".",".","8",".",".","7","9"]

Processing cell (0,0) = "5":
  row 0: "5" not seen -> add
  col 0: "5" not seen -> add
  box 0 (since 0//3=0, 0//3=0 -> box 0): "5" not seen -> add
  ...continue for all 81 cells...

Any duplicate in a row/col/box -> False. This board -> True.

Invalid example: two "6"s in box 0 (top-left 3x3) -> detected at the 2nd "6".

=== COMPLEXITY ANALYSIS ===
Time: O(1) - exactly 81 cells to check. For general n x n board: O(n^2).
Space: O(1) - at most 81 entries. For general n x n: O(n^2).

=== EDGE CASES ===
- Empty board (all ".") -> valid (True).
- Fully filled valid Sudoku -> True.
- Duplicate in a row but not col/box -> False.
- Duplicate in a 3x3 box spanning different rows/cols -> False.
- Single violation -> False (first violation aborts).
- Board with only one filled cell -> True.

=== INTERVIEW TIPS ===
- Box indexing formula: box_index = (r // 3) * 3 + (c // 3). Memorize this.
- Clarify: we validate FILLED cells only; empty '.' cells are skipped.
- The single-set-with-tuples approach is elegant and often praised in interviews.
- Mention that board size is fixed (9x9), so complexity is technically O(1).
- Follow-up: Solve Sudoku (#37) requires backtracking, much harder.
- Follow-up: How to handle a variable board size (e.g., 16x16)? -> parameterize the box size.
'''

# === SOLUTION ===
from typing import List


def isValidSudoku(board: List[List[str]]) -> bool:
    """Single pass with encoded tuple keys in one hash set."""
    seen = set()
    for r in range(9):
        for c in range(9):
            digit = board[r][c]
            if digit == ".":
                continue
            # Encode three constraint checks as unique tuples
            row_key = (digit, "in row", r)
            col_key = (digit, "in col", c)
            box_key = (digit, "in box", (r // 3) * 3 + (c // 3))
            if (row_key in seen or
                    col_key in seen or
                    box_key in seen):
                return False
            seen.add(row_key)
            seen.add(col_key)
            seen.add(box_key)
    return True


# === TEST CASES ===
if __name__ == "__main__":
    valid_board = [
        ["5", "3", ".", ".", "7", ".", ".", ".", "."],
        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
        [".", "9", "8", ".", ".", ".", ".", "6", "."],
        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
        [".", "6", ".", ".", ".", ".", "2", "8", "."],
        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
        [".", ".", ".", ".", "8", ".", ".", "7", "9"],
    ]
    invalid_board = [
        ["5", "3", ".", ".", "7", ".", ".", ".", "."],
        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
        [".", "9", "8", ".", ".", ".", ".", "6", "."],
        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
        [".", "6", ".", ".", ".", ".", "2", "8", "."],
        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
        [".", ".", ".", ".", "8", ".", ".", "7", "9"],
        # extra row makes it invalid by shape, but let's test a duplicate instead
    ]
    # Test 1: Valid board
    assert isValidSudoku(valid_board) is True
    # Test 2: Duplicate in a row
    bad_row = [row[:] for row in valid_board]
    bad_row[0][1] = "5"  # now row 0 has two "5"s
    assert isValidSudoku(bad_row) is False
    # Test 3: Duplicate in a column
    bad_col = [row[:] for row in valid_board]
    bad_col[1][0] = "5"  # col 0 now has "5" at (0,0) and (1,0)
    assert isValidSudoku(bad_col) is False
    # Test 4: Duplicate in a 3x3 box
    bad_box = [row[:] for row in valid_board]
    bad_box[1][1] = "5"  # box 0 now has two "5"s (0,0) and (1,1)
    assert isValidSudoku(bad_box) is False
    # Test 5: Empty board
    empty_board = [["."] * 9 for _ in range(9)]
    assert isValidSudoku(empty_board) is True
    print("All tests passed!")
