'''
LEETCODE #417: Pacific Atlantic Water Flow
DIFFICULTY: Medium
TOPIC: Graphs

=== PROBLEM STATEMENT ===
Given an m x n rectangular island matrix where matrix[r][c] is the height above
sea level of the cell at (r, c). The Pacific Ocean touches the left and top edges.
The Atlantic Ocean touches the right and bottom edges. Water can flow from a cell
to its adjacent (up/down/left/right) neighbor if the neighbor's height is <= the
current cell's height. Return a list of grid coordinates [r, c] from which water
can flow to BOTH oceans.

=== INTUITION ===
The naive approach — for each cell, BFS/DFS to check if it reaches both oceans —
is O(m*n * m*n) in the worst case. Instead, REVERSE THE FLOW:
- Start from the Pacific Ocean borders (top row + left column) and do BFS/DFS
  INLAND, flowing UPWARD (height must be >= previous). Mark all reachable cells.
- Do the same from Atlantic borders (bottom row + right column).
- The answer is cells reachable from BOTH sets.

This is O(m*n) because each cell is visited at most twice.

=== APPROACH ===
Approach: Multi-source BFS/DFS (reverse flow)
- Time: O(m * n) — each cell visited at most twice (once per ocean)
- Space: O(m * n) — two visited sets + recursion/queue

=== DRY RUN ===
matrix = [
  [1, 2, 2, 3, 5],    ← Pacific touches top of row 0
  [3, 2, 3, 4, 4],
  [2, 4, 5, 3, 1],
  [6, 7, 1, 4, 5],
  [5, 1, 1, 2, 4],    ← Atlantic touches bottom of row 4
]
Pacific borders: row 0 (all), col 0 (all)
Atlantic borders: row 4 (all), col 4 (all)

Pacific DFS from (0,0)=1: can go to any neighbor >= 1 → explores inland
  Reachable: (0,0),(0,1),(0,2),(0,3),(0,4),
             (1,0),(1,1),(1,2),(1,3),(1,4),
             (2,0),(2,1),(2,2),
             (3,0),(3,1),
             (4,0)  (and more)

Atlantic DFS from (4,4)=4: can go to neighbor >= 4 → explores inland
  Reachable: (4,4),(4,3),(3,4),(3,3),(2,2),(2,1)...

Intersection (cells in BOTH sets) = answer
Example: (0,3)=3 → reaches Pacific (top row), reaches Atlantic (flow down→right)
         (3,1)=7 → high point, water flows to both oceans

=== COMPLEXITY ANALYSIS ===
Time: O(m * n) — each cell visited at most twice
Space: O(m * n) — two visited matrices + recursion stack

=== EDGE CASES ===
- Single cell matrix [[1]] → answer [[0,0]] (touches both oceans)
- All same height → every cell flows to both oceans
- 1 row or 1 column matrices

=== INTERVIEW TIPS ===
- The key insight is REVERSING the search (start from ocean, go inland)
- This "reverse flow" pattern appears in many problems (e.g., Surrounded Regions)
- Always explain WHY reversing is more efficient than brute force
'''

# === SOLUTION (DFS) ===

def pacificAtlantic(heights: list[list[int]]) -> list[list[int]]:
    if not heights or not heights[0]:
        return []

    ROWS, COLS = len(heights), len(heights[0])
    pacific = set()
    atlantic = set()

    def dfs(r, c, visited, prev_height):
        """
        DFS inland from ocean borders. Water flows UPWARD (reverse flow).
        We can reach (r, c) if its height >= prev_height (water can flow down to ocean).
        """
        if (r < 0 or r >= ROWS or c < 0 or c >= COLS or
                (r, c) in visited or
                heights[r][c] < prev_height):
            return

        visited.add((r, c))

        # Explore all 4 directions
        dfs(r + 1, c, visited, heights[r][c])
        dfs(r - 1, c, visited, heights[r][c])
        dfs(r, c + 1, visited, heights[r][c])
        dfs(r, c - 1, visited, heights[r][c])

    # Start DFS from Pacific borders (top row + left column)
    for c in range(COLS):
        dfs(0, c, pacific, heights[0][c])           # Top row
    for r in range(ROWS):
        dfs(r, 0, pacific, heights[r][0])            # Left column

    # Start DFS from Atlantic borders (bottom row + right column)
    for c in range(COLS):
        dfs(ROWS - 1, c, atlantic, heights[ROWS - 1][c])  # Bottom row
    for r in range(ROWS):
        dfs(r, COLS - 1, atlantic, heights[r][COLS - 1])  # Right column

    # Cells reachable from BOTH oceans
    result = []
    for r in range(ROWS):
        for c in range(COLS):
            if (r, c) in pacific and (r, c) in atlantic:
                result.append([r, c])

    return result


# === BFS APPROACH (Alternative) ===

from collections import deque

def pacificAtlanticBFS(heights: list[list[int]]) -> list[list[int]]:
    if not heights or not heights[0]:
        return []

    ROWS, COLS = len(heights), len(heights[0])

    def bfs(starts):
        visited = set()
        queue = deque(starts)
        for r, c in starts:
            visited.add((r, c))

        while queue:
            r, c = queue.popleft()
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < ROWS and 0 <= nc < COLS and
                        (nr, nc) not in visited and
                        heights[nr][nc] >= heights[r][c]):
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return visited

    pacific_starts = [(0, c) for c in range(COLS)] + [(r, 0) for r in range(ROWS)]
    atlantic_starts = [(ROWS - 1, c) for c in range(COLS)] + [(r, COLS - 1) for r in range(ROWS)]

    pacific = bfs(pacific_starts)
    atlantic = bfs(atlantic_starts)

    return [list(cell) for cell in pacific & atlantic]


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Standard matrix
    matrix = [
        [1, 2, 2, 3, 5],
        [3, 2, 3, 4, 4],
        [2, 4, 5, 3, 1],
        [6, 7, 1, 4, 5],
        [5, 1, 1, 2, 4],
    ]
    result = pacificAtlantic(matrix)
    result_set = set(tuple(r) for r in result)
    assert (0, 4) in result_set  # Top-right corner (5) → reaches both
    assert (4, 0) in result_set  # Bottom-left corner (5) → reaches both
    assert (3, 1) in result_set  # 7 → high point
    print(f"Test 1 passed: {len(result)} cells can reach both oceans")

    # Test 2: Single cell
    assert pacificAtlantic([[1]]) == [[0, 0]]
    print("Test 2 passed: Single cell reaches both oceans")

    # Test 3: All same height → all cells reach both
    same = [[5, 5], [5, 5]]
    result3 = pacificAtlantic(same)
    assert len(result3) == 4
    print("Test 3 passed: All cells reach both oceans when heights are equal")

    print("\n✅ All tests passed!")
