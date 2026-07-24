'''
LEETCODE #200: Number of Islands
DIFFICULTY: Medium
TOPIC: Graphs (BFS / DFS / Union-Find)

=== PROBLEM STATEMENT ===
Given an m x n 2D binary grid which represents a map of '1's (land) and '0's
(water), return the number of islands. An island is surrounded by water and is
formed by connecting adjacent lands horizontally or vertically. You may assume
all four edges of the grid are surrounded by water.

=== INTUITION ===
1. An "island" is a connected component of '1's (4-directional adjacency).
2. Iterate every cell. When we find an unvisited '1', we've found a NEW island:
   increment the count and FLOOD-FILL (DFS/BFS) to mark every connected land cell
   as visited so we don't recount it.
3. We can mutate the grid in place ('1' -> '0') to avoid an extra visited matrix.

=== APPROACHES ===
Approach 1: DFS flood fill (Optimal in practice)
- Iterate cells; on a '1', increment count and DFS to sink all connected land.
- Time: O(m*n), Space: O(m*n) recursion in worst case (a spiral-shaped island).

Approach 2: BFS flood fill
- Same, but use a queue. Avoids recursion-depth issues on huge grids.
- Time: O(m*n), Space: O(min(m,n)) queue.

Approach 3: Union-Find
- Treat each '1' as a node; union 4-directional neighbors; count distinct roots.
- Time: O(m*n * alpha(m*n)), Space: O(m*n).

=== DRY RUN ===
grid = [
  ['1','1','0','0','0'],
  ['1','1','0','0','0'],
  ['0','0','1','0','0'],
  ['0','0','0','1','1']
]

Scan:
 (0,0) '1' -> islands=1. DFS sinks (0,0),(0,1),(1,0),(1,1). They become '0'.
 (0,2)..(0,4) '0' -> skip.
 (1,*) all '0' now -> skip.
 (2,2) '1' -> islands=2. DFS sinks (2,2).
 (3,3) '1' -> islands=3. DFS sinks (3,3),(3,4).
Answer: 3

=== COMPLEXITY ANALYSIS ===
Time: O(m*n) — each cell visited a constant number of times.
Space: O(m*n) worst case for DFS recursion stack (snake-shaped island); O(min(m,n))
  for BFS queue.

=== EDGE CASES ===
- Empty grid or grid with no cells -> 0.
- All water -> 0.
- All land -> 1.
- Single cell '1' -> 1; '0' -> 0.
- Diagonal-only adjacency does NOT connect (4-directional, not 8).

=== INTERVIEW TIPS ===
- In-place mutation ('1'->'0') is the cleanest visited-tracking; confirm with the
  interviewer that mutating the input is allowed.
- State the 4-directional moves explicitly: [(1,0),(-1,0),(0,1),(0,-1)].
- DFS recursion can blow the stack on a 300x300 grid; mention BFS or an explicit
  stack as alternatives.
- Follow-ups: count islands, max island area, number of distinct islands (shapes),
  or islands after adding land one at a time (union-find).
'''

# === SOLUTION ===
def numIslands(grid: list[list[str]]) -> int:
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    islands = 0

    def dfs(r: int, c: int) -> None:
        # Out of bounds or water -> stop flooding.
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == '0':
            return
        grid[r][c] = '0'  # sink this land (mark visited)
        # Flood-fill all 4 neighbors.
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':   # new island discovered
                islands += 1
                dfs(r, c)            # sink the whole island

    return islands


# === TEST CASES ===
if __name__ == "__main__":
    g1 = [
      ["1","1","1","1","0"],
      ["1","1","0","1","0"],
      ["1","1","0","0","0"],
      ["0","0","0","0","0"]
    ]
    assert numIslands(g1) == 1

    g2 = [
      ["1","1","0","0","0"],
      ["1","1","0","0","0"],
      ["0","0","1","0","0"],
      ["0","0","0","1","1"]
    ]
    assert numIslands(g2) == 3

    assert numIslands([["1"]]) == 1
    assert numIslands([["0"]]) == 0
    assert numIslands([["1","0"],["0","1"]]) == 2   # diagonal does not connect
    print("All test cases passed.")
