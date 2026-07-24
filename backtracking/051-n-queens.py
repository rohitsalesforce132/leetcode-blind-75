'''
LEETCODE #51: N-Queens
DIFFICULTY: Hard
TOPIC: Backtracking

=== PROBLEM STATEMENT ===
Place n queens on an n×n chessboard such that no two queens attack each other.
Return ALL distinct solutions. Each solution is a board configuration where 'Q'
marks a queen and '.' marks an empty cell. Queens attack along rows, columns,
and diagonals.

=== INTUITION ===
This is the quintessential backtracking problem. We place queens one row at a time
(row by row). For each row, we try placing the queen in each column and check if
it's valid (not attacked by any previously placed queen). If valid, we place it
and recurse to the next row. If we reach row == n, we have a complete solution.

The key optimization: since we place one queen per row, we never need to check
row conflicts. We track:
- Columns used (set)
- Positive diagonals (r + c = constant) — set
- Negative diagonals (r - c = constant) — set

=== APPROACHES ===
Approach 1: Backtracking with Sets
- Idea: Place queen row by row. Use sets to track attacked columns and diagonals
  in O(1) lookup. When row == n, record the board.
- Time: O(N!) — at row 0: N choices, row 1: ≤ N-1, row 2: ≤ N-2, ...
- Space: O(N) — recursion depth + 3 sets

Approach 2: Backtracking with Boolean Arrays
- Same idea but use boolean arrays instead of sets for O(1) lookups
- Slightly faster in practice due to no hashing overhead

=== DRY RUN (n=4) ===
Board: 4×4. Place queens row by row.

Row 0: Try col 0
  col=0 not in cols/diagonals → place Q at (0,0)
  cols={0}, posDiag={0}, negDiag={0}

  Row 1: Try col 0 → in cols ✗
         Try col 1 → (1+1=2) in posDiag? No. (1-1=0) in negDiag? Yes ✗
         Try col 2 → (1+2=3) in posDiag? No. (1-2=-1) in negDiag? No → place Q at (1,2)
         cols={0,2}, posDiag={0,3}, negDiag={0,-1}

    Row 2: Try col 0 → in cols ✗
           Try col 1 → (2+1=3) in posDiag? Yes ✗
           Try col 2 → in cols ✗
           Try col 3 → (2-3=-1) in negDiag? Yes ✗
           ALL FAILED → backtrack!

  Backtrack row 1, remove (1,2)

  Row 1: Try col 3 → (1+3=4), (1-3=-2) → all clear → place Q at (1,3)
         cols={0,3}, posDiag={0,4}, negDiag={0,-2}

    Row 2: Try col 1 → all clear → place Q at (2,1)
           cols={0,3,1}, posDiag={0,4,3}, negDiag={0,-2,1}

      Row 3: Try col 0 → in cols ✗
             Try col 1 → in cols ✗
             Try col 2 → (3+2=5),(3-2=1) → negDiag has 1 ✗
             Try col 3 → in cols ✗
             ALL FAILED → backtrack!

... (continues until finding valid placement)

FINAL SOLUTION 1:
  . Q . .
  . . . Q
  Q . . .
  . . Q .

FINAL SOLUTION 2:
  . . Q .
  Q . . .
  . . . Q
  . Q . .

For n=4: exactly 2 solutions.

=== COMPLEXITY ANALYSIS ===
Time: O(N!) — queen placement permutations. Exact bound is complex (≤ N!)
Space: O(N) — recursion stack + tracking sets. Output space: O(N! * N²) for solutions

=== EDGE CASES ===
- n=1 → one solution: [["Q"]]
- n=2, n=3 → no solutions exist (return [])
- Large n (8+) → many solutions (n=8 has 92 solutions)

=== INTERVIEW TIPS ===
- Explain the diagonal trick clearly: r+c identifies "/" diagonals, r-c identifies "\" diagonals
- Walk through n=4 by hand before coding to show understanding
- Ask: should we return board strings or coordinates? (Clarify output format)
- Common follow-up: return just the COUNT of solutions (N-Queens II, LC #52)
- Mention that the time complexity is O(N!) and explain why (pruning via constraint sets)
'''

# === SOLUTION ===

def solveNQueens(n: int) -> list[list[str]]:
    result = []

    cols = set()          # Columns with a queen
    pos_diagonal = set()  # "/" diagonals (r + c)
    neg_diagonal = set()  # "\" diagonals (r - c)

    def backtrack(row, board):
        # Base case: all queens placed
        if row == n:
            result.append(board[:])  # Found a valid solution
            return

        for col in range(n):
            # Check if placement is valid
            if (col in cols or
                    (row + col) in pos_diagonal or
                    (row - col) in neg_diagonal):
                continue

            # Place queen
            cols.add(col)
            pos_diagonal.add(row + col)
            neg_diagonal.add(row - col)
            board_row = '.' * col + 'Q' + '.' * (n - col - 1)
            board.append(board_row)

            # Recurse to next row
            backtrack(row + 1, board)

            # Backtrack (undo placement)
            board.pop()
            cols.remove(col)
            pos_diagonal.remove(row + col)
            neg_diagonal.remove(row - col)

    backtrack(0, [])
    return result


# === COUNT-ONLY VERSION (N-Queens II, LC #52) ===

def totalNQueens(n: int) -> int:
    cols = set()
    pos_diag = set()
    neg_diag = set()
    count = 0

    def backtrack(row):
        nonlocal count
        if row == n:
            count += 1
            return

        for col in range(n):
            if (col in cols or (row + col) in pos_diag or (row - col) in neg_diag):
                continue

            cols.add(col)
            pos_diag.add(row + col)
            neg_diag.add(row - col)

            backtrack(row + 1)

            cols.remove(col)
            pos_diag.remove(row + col)
            neg_diag.remove(row - col)

    backtrack(0)
    return count


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: n=4 → 2 solutions
    sols4 = solveNQueens(4)
    assert len(sols4) == 2
    print(f"Test 1 passed: n=4 has {len(sols4)} solutions")
    for i, sol in enumerate(sols4):
        print(f"  Solution {i+1}:")
        for row in sol:
            print(f"    {row}")

    # Test 2: n=1 → 1 solution
    sols1 = solveNQueens(1)
    assert len(sols1) == 1
    assert sols1[0] == ["Q"]
    print(f"\nTest 2 passed: n=1 has 1 solution: {sols1[0]}")

    # Test 3: n=2 → 0 solutions
    assert len(solveNQueens(2)) == 0
    print("Test 3 passed: n=2 has 0 solutions")

    # Test 4: n=3 → 0 solutions
    assert len(solveNQueens(3)) == 0
    print("Test 4 passed: n=3 has 0 solutions")

    # Test 5: n=8 → 92 solutions (classic 8-queens)
    sols8 = solveNQueens(8)
    assert len(sols8) == 92
    print(f"Test 5 passed: n=8 has {len(sols8)} solutions")

    # Test 6: count function matches
    assert totalNQueens(4) == 2
    assert totalNQueens(8) == 92
    print("Test 6 passed: totalNQueens matches solveNQueens count")

    print("\n✅ All tests passed!")
