'''
CHAPTER 5: GRAPHS — THE MOST VERSATILE DATA STRUCTURE
=====================================================

"Graphs model the real world. Social networks, maps, dependencies,
the internet itself. If you understand graphs, you understand the
structure of connected systems."

---

PART 1: WHAT IS A GRAPH?
=========================

Real-world analogy: A MAP OF CITIES AND ROADS.

    Delhi ─── 200km ─── Mumbai
      │                    │
    500km                300km
      │                    │
    Bangalore ─── 150km ── Chennai

    Each city is a NODE (vertex).
    Each road is an EDGE (connection).
    The distance is a WEIGHT (optional).

A graph is simply:
    - A set of NODES (also called vertices)
    - A set of EDGES (connections between nodes)

GRAPHS vs TREES (Important distinction!):

    Tree: Every node has ONE parent. No cycles. One root.
          A tree is a SPECIAL CASE of a graph.

    Graph: Nodes can connect to ANYTHING. Cycles allowed. No root.
          All trees are graphs, but NOT all graphs are trees.

    Tree:                              Graph:
        1                                 A ── B
       / \\                                │    │
      2   3                               C ── D
     /                                    │
    4                                     E (cycle: A→B→D→C→A)

TYPES OF GRAPHS:
    UNDIRECTED: Edges go both ways (two-way street)
        A ── B  (can travel A→B and B→A)
    DIRECTED: Edges have direction (one-way street)
        A → B  (can travel A→B, but NOT B→A)
    WEIGHTED: Edges have values (distance, cost, time)
        A ──100── B
    UNWEIGHTED: All edges are equal
        A ── B
    CYCLIC: Has at least one cycle (path that returns to start)
        A → B → C → A  (cycle!)
    ACYCLIC: No cycles (DAG = Directed Acyclic Graph)
        A → B → C (no way to get back to A)

---

PART 2: HOW TO REPRESENT A GRAPH IN CODE
=========================================

REPRESENTATION 1: ADJACENCY LIST (Most Common in Interviews)
-------------------------------------------------------------
A dictionary where each node maps to a list of its neighbors.

    Graph:     0 --- 1
               |     |
               2 --- 3 --- 4

    Adjacency list:
        0: [1, 2]
        1: [0, 3]
        2: [0, 3]
        3: [1, 2, 4]
        4: [3]

    This is just a hash map! Node → List of neighbors.
    Space: O(V + E) where V = vertices, E = edges
'''

from collections import defaultdict, deque

# --- ADJACENCY LIST ---
graph = {
    0: [1, 2],
    1: [0, 3],
    2: [0, 3],
    3: [1, 2, 4],
    4: [3],
}

print("--- Adjacency List ---")
for node, neighbors in graph.items():
    print(f"  Node {node} connects to: {neighbors}")


# --- BUILDING A GRAPH FROM EDGE LIST ---
edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
graph_from_edges = defaultdict(list)
for u, v in edges:
    graph_from_edges[u].append(v)
    graph_from_edges[v].append(u)  # For undirected graph (both directions)

# For DIRECTED graph, only add one direction:
# graph_directed[u].append(v)  # Can go u→v, but NOT v→u


'''
REPRESENTATION 2: ADJACENCY MATRIX
-----------------------------------
A 2D array where matrix[i][j] = 1 if there's an edge from i to j.

       0  1  2  3  4
    0 [ 0  1  1  0  0 ]   ← Node 0 connects to 1, 2
    1 [ 1  0  0  1  0 ]   ← Node 1 connects to 0, 3
    2 [ 1  0  0  1  0 ]   ← Node 2 connects to 0, 3
    3 [ 0  1  1  0  1 ]   ← Node 3 connects to 1, 2, 4
    4 [ 0  0  0  1  0 ]   ← Node 4 connects to 3

    For weighted graphs: matrix[i][j] = weight (not just 1/0)

    Space: O(V²) — always V×V, regardless of how many edges
'''

# --- ADJACENCY MATRIX ---
V = 5  # 5 nodes
matrix = [[0] * V for _ in range(V)]

# Add edges (undirected)
def add_edge_matrix(mat, u, v):
    mat[u][v] = 1
    mat[v][u] = 1  # For undirected

for u, v in edges:
    add_edge_matrix(matrix, u, v)

print("\n--- Adjacency Matrix ---")
for row in matrix:
    print(f"  {row}")


'''
WHICH TO USE?
┌──────────────────┬──────────────────┬──────────────────┐
│ Feature          │ Adjacency List   │ Adjacency Matrix │
├──────────────────┼──────────────────┼──────────────────┤
│ Space            │ O(V + E)         │ O(V²)            │
│ Check edge exist │ O(degree) scan   │ O(1) direct      │
│ Iterate neighbors│ O(degree)        │ O(V) per node    │
│ Best for         │ Sparse graphs    │ Dense graphs     │
│ Add edge         │ O(1) append      │ O(1) set cell    │
│ Common in        │ Interviews       │ Theory/Floyd's   │
└──────────────────┴──────────────────┴──────────────────┘

In interviews, ALMOST ALWAYS use adjacency list. It's simpler and
uses less memory for typical problems (graphs are usually sparse).
'''


'''
PART 3: GRAPH TRAVERSAL — THE TWO ALGORITHMS
=============================================

To solve ANY graph problem, you need to VISIT (traverse) nodes.
There are exactly TWO ways:

1. BFS (Breadth-First Search) — "Ripple in a pond"
2. DFS (Depth-First Search) — "Explore a cave"

These are the MOST IMPORTANT algorithms in all of graph theory.
Master them and you can solve 80% of graph problems.

BFS: BREADTH-FIRST SEARCH
-------------------------
Real-world analogy: A RIPPLE IN A POND.

    Drop a stone in water. Ripples spread outward in concentric circles.
    You visit ALL neighbors first (1 hop), then THEIR neighbors (2 hops),
    then THEIR neighbors (3 hops), etc.

    Graph:       A
                / \
               B   C        Level 0: A
              / \   \       Level 1: B, C
             D   E   F      Level 2: D, E, F

    BFS visits: A → B → C → D → E → F (level by level)

HOW BFS WORKS (uses a QUEUE):
    1. Start at source. Mark visited. Add to queue.
    2. While queue not empty:
       a. Dequeue a node.
       b. For each UNVISITED neighbor: mark visited, enqueue.
    3. Done when queue is empty.

WHY A QUEUE? Because FIFO (First-In-First-Out) ensures we process
nodes in the order they were discovered. The first node discovered
(added to queue) is the first one processed (removed from queue).
This guarantees level-by-level processing.
'''

def bfs(graph, start):
    """
    Breadth-First Search starting from 'start' node.

    Returns the list of nodes in BFS order.

    Time: O(V + E) — each vertex and edge visited once
    Space: O(V) — for visited set and queue
    """
    visited = set()          # Track visited nodes (CRITICAL — prevents infinite loops!)
    queue = deque([start])   # Start with the source node
    order = []               # Record visit order

    visited.add(start)       # Mark start as visited BEFORE enqueueing

    while queue:
        node = queue.popleft()   # Dequeue (FIFO — oldest first)
        order.append(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)      # Mark visited immediately
                queue.append(neighbor)      # Enqueue

    return order

# Build a graph for demos
graph_bfs = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E'],
}

print("\n--- BFS ---")
print(f"Visit order: {bfs(graph_bfs, 'A')}")  # ['A', 'B', 'C', 'D', 'E', 'F']


'''
DFS: DEPTH-FIRST SEARCH
-----------------------
Real-world analogy: EXPLORING A CAVE / WALKING A MAZE.

    You go as DEEP as possible down one path before turning back.
    At each fork, pick a direction and keep going until you hit a
    dead end. Then BACKTRACK to the last fork and try another path.

    Graph:       A
                / \
               B   C
              / \   \
             D   E   F

    DFS visits: A → B → D → E → C → F (one possible order)

HOW DFS WORKS (uses a STACK — either explicitly or via recursion):
    1. Start at source. Mark visited.
    2. For each UNVISITED neighbor: recursively DFS it.
    3. When all neighbors visited, backtrack (return from recursion).

WHY RECURSION? Because recursion IS a stack (the call stack).
Each recursive call goes deeper. When it returns, you backtrack.

    Call stack for DFS(A):
    dfs(A) → dfs(B) → dfs(D) → return → dfs(E) → return → return
           → dfs(C) → dfs(F) → return → return → return
'''


def dfs_recursive(graph, node, visited=None, order=None):
    """
    Depth-First Search (recursive version).

    Time: O(V + E)
    Space: O(V) — recursion stack depth (up to V in worst case)
    """
    if visited is None:
        visited = set()
    if order is None:
        order = []

    visited.add(node)
    order.append(node)

    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited, order)

    return order


def dfs_iterative(graph, start):
    """
    Depth-First Search (iterative version using explicit stack).

    Same logic as recursive, but uses an explicit stack instead
    of the call stack. Useful when the graph is deep (avoids
    stack overflow from recursion).

    Time: O(V + E)
    Space: O(V)
    """
    visited = set()
    stack = [start]
    order = []

    while stack:
        node = stack.pop()  # LIFO — last pushed is first processed

        if node not in visited:
            visited.add(node)
            order.append(node)

            # Push neighbors in REVERSE order so they're processed
            # left-to-right (matches recursive DFS order)
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)

    return order


print("\n--- DFS ---")
print(f"Recursive: {dfs_recursive(graph_bfs, 'A')}")  # A → B → D → E → F → C
print(f"Iterative: {dfs_iterative(graph_bfs, 'A')}")


'''
BFS vs DFS — WHEN TO USE WHICH?
┌──────────────────┬──────────────────────────┬─────────────────────────┐
│ Feature          │ BFS                       │ DFS                     │
├──────────────────┼──────────────────────────┼─────────────────────────┤
│ Data structure   │ Queue (FIFO)              │ Stack (LIFO) or recurs. │
│ Explores         │ Level by level (wide)     │ One path fully (deep)   │
│ Shortest path?   │ YES (unweighted graphs)   │ NO (might take long way)│
│ Memory           │ O(width of graph)         │ O(depth of graph)       │
│ Best for         │ Shortest path, nearest    │ Cycle detect, topological│
│                  │ node, level order         │ sort, connected compon. │
│ Implementation   │ Iterative (queue)         │ Recursive or iterative  │
└──────────────────┴──────────────────────────┴─────────────────────────┘

THE GOLDEN RULE:
    "Need the SHORTEST PATH?" → BFS (because it explores level by level,
     guaranteeing the first time you reach a node is via the shortest path)
    "Need to explore ALL POSSIBILITIES?" → DFS (backtracking, cycle detection)
'''


'''
PART 4: THE #1 GRAPH PROBLEM — NUMBER OF ISLANDS (LeetCode #200)
=================================================================

This problem appears constantly. It tests whether you understand DFS/BFS
on a GRID (which is just a graph where each cell connects to up to 4 neighbors).

PROBLEM:
    Given a 2D grid of '1' (land) and '0' (water), count the number of
    islands. An island is a group of connected '1's (connected horizontally
    or vertically).

    Grid:
        ['1','1','0','0','0']
        ['1','1','0','0','0']
        ['0','0','1','0','0']
        ['0','0','0','1','1']

    Islands: 3  (top-left blob, middle single, bottom-right pair)

MENTAL MODEL:
    Each land cell is a NODE. Adjacent land cells are connected by EDGES.
    An "island" is a CONNECTED COMPONENT — a group of nodes reachable
    from each other.

ALGORITHM:
    1. Scan every cell in the grid.
    2. When you find an unvisited '1' (land), you found a new island!
    3. Increment island count.
    4. "Sink" the entire island — DFS/BFS to mark ALL connected land
       cells as visited (or change them to '0').
    5. Continue scanning.
'''

def num_islands(grid):
    """
    Count the number of islands in a 2D grid.

    Time: O(rows × cols) — each cell visited once
    Space: O(rows × cols) — recursion stack in worst case (all land)
    """
    if not grid:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        """Mark all connected land starting at (r, c) as visited."""
        # Check bounds and whether this is land
        if (r < 0 or r >= rows or c < 0 or c >= cols
                or grid[r][c] == '0'):
            return

        grid[r][c] = '0'  # Sink this cell (mark as visited/water)

        # Recursively sink all 4 neighbors
        dfs(r + 1, c)  # Down
        dfs(r - 1, c)  # Up
        dfs(r, c + 1)  # Right
        dfs(r, c - 1)  # Left

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':  # Found unvisited land
                count += 1          # New island!
                dfs(r, c)           # Sink the whole island

    return count

print("\n--- Number of Islands ---")
grid = [
    ['1', '1', '0', '0', '0'],
    ['1', '1', '0', '0', '0'],
    ['0', '0', '1', '0', '0'],
    ['0', '0', '0', '1', '1'],
]
print(f"Number of islands: {num_islands(grid)}")  # 3


'''
DRY RUN:
  Grid:                             Islands found: 0

  Scan row 0:
    (0,0) = '1' → ISLAND #1! Sink it with DFS.
      DFS sinks: (0,0), (0,1), (1,0), (1,1)  → all become '0'
    (0,1) = '0' (already sunk)
    (0,2-4) = '0'

  Scan row 1: All '0' now

  Scan row 2:
    (2,0-1) = '0'
    (2,2) = '1' → ISLAND #2! Sink it.
      DFS sinks: (2,2) only (no neighbors are '1')
    (2,3-4) = '0'

  Scan row 3:
    (3,0-2) = '0'
    (3,3) = '1' → ISLAND #3! Sink it.
      DFS sinks: (3,3), (3,4) → both become '0'

  Total islands: 3
'''


'''
PART 5: SHORTEST PATH WITH BFS
================================

THE KEY INSIGHT:
    BFS explores level by level. Each "level" is one step further from start.
    So the FIRST time BFS reaches a node, it's via the shortest path.

    To reconstruct the actual path, store each node's PARENT.
'''

def shortest_path_bfs(graph, start, target):
    """
    Find shortest path between two nodes in an unweighted graph.

    Time: O(V + E)
    Space: O(V)

    Returns the path as a list of nodes, or empty list if no path.
    """
    if start == target:
        return [start]

    visited = {start}
    queue = deque([(start, [start])])  # (current_node, path_so_far)

    while queue:
        node, path = queue.popleft()

        for neighbor in graph[node]:
            if neighbor == target:
                return path + [neighbor]  # Found shortest path!

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return []  # No path found

# Graph for shortest path demo
graph_path = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E'],
}

print("\n--- Shortest Path (BFS) ---")
print(f"A to F: {shortest_path_bfs(graph_path, 'A', 'F')}")  # ['A', 'C', 'F']
print(f"A to D: {shortest_path_bfs(graph_path, 'A', 'D')}")  # ['A', 'B', 'D']
print(f"A to A: {shortest_path_bfs(graph_path, 'A', 'A')}")  # ['A']


'''
WHY BFS FINDS THE SHORTEST PATH:

    Level 0:    A                    ← distance 0 from A
    Level 1:    B, C                 ← distance 1 from A
    Level 2:    D, E, F              ← distance 2 from A

    BFS visits ALL nodes at distance 1 before ANY node at distance 2.
    So when BFS first reaches F at level 2, it MUST have come via the
    shortest path (2 hops). No shorter path exists.

    DFS might reach F via A→B→E→F (3 hops) instead of A→C→F (2 hops).
    That's why DFS doesn't guarantee shortest path.
'''


'''
PART 6: CYCLE DETECTION IN DIRECTED GRAPHS (TOPOLOGICAL SORT)
================================================================

PROBLEM: Course Schedule (LeetCode #207)
    "You have N courses. Some have prerequisites. Can you finish all?"

    prerequisites = [[1,0], [2,1]] means:
      Course 0 has no prerequisites
      Course 1 requires Course 0 first
      Course 2 requires Course 1 first

    This is asking: does the dependency graph have a CYCLE?
    If A requires B, B requires C, C requires A → impossible (cycle)!

TOPOLOGICAL SORT:
    An ordering of nodes where for every edge A→B, A comes before B.
    Only possible if there's NO cycle.
    Algorithm: Kahn's Algorithm (BFS-based)

    1. Count IN-DEGREE of each node (how many edges point TO it).
    2. Start with nodes that have in-degree 0 (no prerequisites).
    3. Process each: remove it, reduce neighbors' in-degree.
    4. If a neighbor's in-degree becomes 0, add it to queue.
    5. If we process ALL nodes → no cycle → possible.
       If some nodes remain → cycle → impossible.
'''

def can_finish(numCourses, prerequisites):
    """
    Check if all courses can be finished (no dependency cycle).

    Time: O(V + E)
    Space: O(V + E)
    """
    # Build adjacency list and in-degree array
    adj = defaultdict(list)
    in_degree = [0] * numCourses

    for course, prereq in prerequisites:
        adj[prereq].append(course)     # prereq → course
        in_degree[course] += 1

    # Start with courses that have NO prerequisites
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    completed = 0

    while queue:
        course = queue.popleft()
        completed += 1

        for next_course in adj[course]:
            in_degree[next_course] -= 1  # One fewer prerequisite
            if in_degree[next_course] == 0:
                queue.append(next_course)

    return completed == numCourses  # All courses completed?

print("\n--- Course Schedule (Topological Sort) ---")
print(f"Linear chain 0→1→2→3: {can_finish(4, [[1,0], [2,1], [3,2]])}")  # True
print(f"Cycle 0→1→0: {can_finish(2, [[0,1], [1,0]])}")  # False


'''
DRY RUN — COURSE SCHEDULE:

  Case 1: prerequisites = [[1,0], [2,1], [3,2]]
  Graph: 0 → 1 → 2 → 3  (linear chain, no cycle)

  In-degrees:  0:0, 1:1, 2:1, 3:1
  Queue starts: [0]  (only node with in-degree 0)

  Process 0: completed=1. Reduce 1's in-degree: 0. Queue: [1]
  Process 1: completed=2. Reduce 2's in-degree: 0. Queue: [2]
  Process 2: completed=3. Reduce 3's in-degree: 0. Queue: [3]
  Process 3: completed=4. Queue empty.
  completed(4) == numCourses(4) → True!

  Case 2: prerequisites = [[0,1], [1,0]]
  Graph: 0 → 1 → 0  (cycle!)

  In-degrees:  0:1, 1:1
  Queue starts: []  (no node has in-degree 0!)

  Queue empty immediately. completed=0.
  completed(0) != numCourses(2) → False! (cycle detected)
'''


'''
PART 7: GRAPH PROBLEMS SUMMARY
================================

┌────────────────────────────┬──────────────┬──────────────────────────────┐
│ Problem Type               │ Algorithm    │ Key Insight                  │
├────────────────────────────┼──────────────┼──────────────────────────────┤
│ Count connected components │ DFS or BFS   │ Each unvisited start = new   │
│ (Number of Islands)        │              │ component                    │
├────────────────────────────┼──────────────┼──────────────────────────────┤
│ Shortest path (unweighted) │ BFS          │ Level-by-level = shortest    │
├────────────────────────────┼──────────────┼──────────────────────────────┤
│ Shortest path (weighted)   │ Dijkstra's   │ Priority queue (min-heap)    │
├────────────────────────────┼──────────────┼──────────────────────────────┤
│ Cycle detection (directed) │ DFS 3-color  │ Gray node in path = cycle    │
│                            │ or Kahn's    │                              │
├────────────────────────────┼──────────────┼──────────────────────────────┤
│ Topological sort           │ Kahn's BFS   │ Nodes with 0 in-degree first │
├────────────────────────────┼──────────────┼──────────────────────────────┤
│ Flood fill / paint bucket  │ DFS on grid  │ Treat grid cells as graph    │
├────────────────────────────┼──────────────┼──────────────────────────────┤
│ Clone a graph              │ DFS + HashMap│ Map old node → new node      │
├────────────────────────────┼──────────────┼──────────────────────────────┤
│ Pacific Atlantic Water Flow│ DFS from     │ Reverse: start from oceans,  │
│                            │ borders      │ flow inward (uphill)         │
└────────────────────────────┴──────────────┴──────────────────────────────┘
'''


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 5 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Graph = nodes (vertices) + edges (connections).
2. Represent as adjacency list (dict: node → list of neighbors).
3. BFS (queue): level by level. Finds shortest path in unweighted graphs.
4. DFS (stack/recursion): go deep, then backtrack.
   - Use for: connected components, cycle detection, topological sort
5. Number of Islands: DFS flood fill on a grid. Each '1' starts DFS.
6. Course Schedule: topological sort. If all nodes processed → no cycle.
7. ALWAYS track visited nodes to prevent infinite loops!
8. BFS = shortest path. DFS = explore everything.
9. Time: O(V + E) for both BFS and DFS.
10. Space: O(V) for visited set + queue/stack.

🎓 CONGRATULATIONS! You now know ALL the fundamental data structures!
   Next: Read the Patterns Cheat Sheet, then tackle Blind 75.
""")
