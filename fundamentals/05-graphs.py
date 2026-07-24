'''
CHAPTER 5: GRAPHS
==================

"Graphs are the most versatile data structure. Social networks, maps,
dependency trees, recommendation engines — all graphs. If you understand
graphs, you understand the structure of the internet."

---

PART 1: WHAT IS A GRAPH?
=========================

Real-world analogy: A MAP OF CITIES AND ROADS.

    Delhi ─── 200km ─── Mumbai
      │                    │
    500km                300km
      │                    │
    Bangalore ─── 150km ── Chennai

Each city is a NODE (also called "vertex").
Each road is an EDGE (connection between nodes).
The distance is a WEIGHT (optional — not all graphs have weights).

A graph is simply:
    - A set of NODES (points / vertices)
    - A set of EDGES (connections between nodes)

GRAPHS vs TREES:
    Tree: Every node has ONE parent. No cycles. One root.
    Graph: Nodes can connect to anything. Cycles allowed. No root.

    ALL trees are graphs, but NOT all graphs are trees.

TYPES OF GRAPHS:
    DIRECTED: Edges have direction (one-way streets)
        A → B  (you can go from A to B, but not B to A)
    UNDIRECTED: Edges go both ways (two-way streets)
        A — B  (can go A to B AND B to A)
    WEIGHTED: Edges have values (distances, costs)
    UNWEIGHTED: All edges are equal

---

PART 2: HOW TO REPRESENT A GRAPH IN CODE
=========================================

There are two common ways to store a graph:

REPRESENTATION 1: ADJACENCY LIST (Most common in interviews)
--------------------------------------------------------------
A dictionary where each node maps to a list of its neighbors.

    Graph:     0 --- 1
               |     |
               2 --- 3

    Adjacency list:
        0: [1, 2]
        1: [0, 3]
        2: [0, 3]
        3: [1, 2]

    This is just a hash map! Node → List of neighbors.
'''

# --- ADJACENCY LIST ---
graph = {
    0: [1, 2],
    1: [0, 3],
    2: [0, 3],
    3: [1, 2],
}

print("--- Adjacency List ---")
for node, neighbors in graph.items():
    print(f"  Node {node} connects to: {neighbors}")


'''
REPRESENTATION 2: ADJACENCY MATRIX
-----------------------------------
A 2D array where matrix[i][j] = 1 if there's an edge from i to j, else 0.

       0  1  2  3
    0 [ 0  1  1  0 ]
    1 [ 1  0  0  1 ]
    2 [ 1  0  0  1 ]
    3 [ 0  1  1  0 ]

    Less common in interviews because it uses O(V²) space.
    Use it when the graph is DENSE (many edges).
'''

# --- ADJACENCY MATRIX ---
matrix = [
    [0, 1, 1, 0],  # Node 0 connects to 1, 2
    [1, 0, 0, 1],  # Node 1 connects to 0, 3
    [1, 0, 0, 1],  # Node 2 connects to 0, 3
    [0, 1, 1, 0],  # Node 3 connects to 1, 2
]


'''
WHICH TO USE?
    | Feature          | Adjacency List    | Adjacency Matrix |
    |------------------|--------------------|-------------------|
    | Space            | O(V + E)           | O(V²)             |
    | Check if edge    | O(degree)          | O(1)              |
    |   exists         |                    |                   |
    | Iterate          | O(degree)          | O(V)              |
    |   neighbors      |                    |                   |
    | Best for         | Sparse graphs      | Dense graphs      |

    In interviews, ALMOST ALWAYS use adjacency list. It's simpler and
    uses less memory for typical problems.
'''

from collections import defaultdict, deque


'''
PART 3: GRAPH TRAVERSAL — THE TWO ALGORITHMS
=============================================

To solve ANY graph problem, you need to visit (traverse) nodes.
There are exactly TWO ways to do this:

1. BFS (Breadth-First Search) — "Ripple in a pond"
2. DFS (Depth-First Search) — "Explore a cave"

BFS: BREADTH-FIRST SEARCH
-------------------------
Real-world analogy: A RIPLE IN A POND.

    Drop a stone in water. The ripples spread outward in concentric circles.
    You visit ALL neighbors first (1 hop away), then THEIR neighbors (2 hops),
    then THEIR neighbors (3 hops), etc.

    Visit order: Level by level.

    Graph:       A
                / \
               B   C        Level 0: A
              / \   \       Level 1: B, C
             D   E   F      Level 2: D, E, F

    BFS visits: A → B → C → D → E → F

HOW BFS WORKS (uses a QUEUE):
    1. Start at a node. Mark it visited. Add to queue.
    2. While queue is not empty:
       a. Dequeue a node.
       b. For each UNVISITED neighbor: mark visited, enqueue.
    3. Done when queue is empty.

WHY A QUEUE? Because we process in FIFO order — the first node we discovered
is the first one we process. This ensures we go level by level.
'''

def bfs(graph, start):
    """Breadth-First Search starting from 'start' node."""
    visited = set()         # Track visited nodes (prevent infinite loops!)
    queue = deque([start])  # Start with the source node
    order = []              # Record visit order

    visited.add(start)

    while queue:
        node = queue.popleft()    # Dequeue (FIFO — oldest first)
        order.append(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order

# Build a graph for demo
graph_bfs = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B'],
    'F': ['C'],
}

print("\n--- BFS ---")
print("Visit order:", bfs(graph_bfs, 'A'))  # ['A', 'B', 'C', 'D', 'E', 'F']


'''
DFS: DEPTH-FIRST SEARCH
-----------------------
Real-world analogy: EXPLORING A CAVE.

    You go as DEEP as possible down one path before turning back.
    At each fork, you pick a direction and keep going until you hit a
    dead end. Then you BACKTRACK to the last fork and try another path.

    Visit order: Follow one path as far as possible, then backtrack.

    Graph:       A
                / \
               B   C
              / \   \
             D   E   F

    DFS visits: A → B → D → E → C → F (one possible order)

HOW DFS WORKS (uses a STACK — either explicitly or via recursion):
    1. Start at a node. Mark it visited.
    2. For each UNVISITED neighbor: recursively DFS it.
    3. When all neighbors visited, backtrack (return from recursion).

WHY RECURSION? Because recursion IS a stack (the call stack).
Each recursive call goes deeper. When it returns, you backtrack.
'''

def dfs(graph, node, visited=None, order=None):
    """Depth-First Search (recursive)."""
    if visited is None:
        visited = set()
    if order is None:
        order = []

    visited.add(node)
    order.append(node)

    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited, order)

    return order

print("\n--- DFS ---")
print("Visit order:", dfs(graph_bfs, 'A'))  # ['A', 'B', 'D', 'E', 'C', 'F']


'''
BFS vs DFS — WHEN TO USE WHICH?
-------------------------------
    | Feature          | BFS                          | DFS                         |
    |------------------|------------------------------|-----------------------------|
    | Data structure   | Queue                        | Stack (or recursion)        |
    | Explores         | Level by level (wide)        | One path fully (deep)       |
    | Finds shortest   | YES (unweighted graphs)      | NO (might take long path)   |
    |   path           |                              |                             |
    | Memory           | O(width of graph)            | O(depth of graph)           |
    | Best for         | Shortest path, nearest node  | Cycle detection, topological|
    |                  |                              | sort, connected components  |

GOLDEN RULE:
    "Need the shortest path?" → BFS (because it explores level by level,
    guaranteeing the first time you reach a node is via the shortest path)
    "Need to explore all possibilities?" → DFS (backtracking, cycle detection)

---

PART 4: THE #1 GRAPH PROBLEM — NUMBER OF ISLANDS
=================================================

This problem appears constantly. It tests whether you understand DFS/BFS
on a GRID (which is just a graph where each cell connects to its neighbors).

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
    4. "Sink" the entire island — DFS/BFS to mark ALL connected land cells
       as visited (or change them to '0' so you don't count them again).
    5. Continue scanning.
'''

def num_islands(grid):
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

        grid[r][c] = '0'  # Sink this cell (mark as visited)

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
PART 5: SHORTEST PATH WITH BFS
===============================

THE PATTERN:
    BFS explores level by level. Each "level" is one step further from start.
    So the FIRST time BFS reaches a node, it's via the shortest path.

    To reconstruct the actual path, store each node's PARENT.
'''

def shortest_path(graph, start, target):
    """Find shortest path between two nodes in an unweighted graph."""
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
print("A to F:", shortest_path(graph_path, 'A', 'F'))  # ['A', 'C', 'F']


'''
PART 6: CYCLE DETECTION IN DIRECTED GRAPHS (TOPOLOGICAL SORT)
==============================================================

PROBLEM: Course Schedule (LeetCode #207)
    "You have N courses. Some have prerequisites. Can you finish all of them?"

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

def can_finish_courses(numCourses, prerequisites):
    """Check if all courses can be finished (no dependency cycle)."""
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
print(can_finish_courses(4, [[1, 0], [2, 1], [3, 2]]))      # True (linear chain, no cycle)
print(can_finish_courses(2, [[0, 1], [1, 0]]))               # False (cycle: 0→1→0)


'''
PART 7: GRAPH PATTERNS SUMMARY
================================

| Problem Type                | Algorithm         | Key Insight                          |
|----------------------------|--------------------|--------------------------------------|
| Count connected components  | DFS or BFS         | Each unvisited start = new component |
| Shortest path (unweighted)  | BFS                | Level-by-level = shortest path       |
| Shortest path (weighted)    | Dijkstra's         | Use a priority queue (min-heap)      |
| Cycle detection (directed)  | DFS colors or Kahn | Gray node in DFS = cycle in path     |
| Topological sort            | Kahn's BFS         | Nodes with 0 in-degree first         |
| Flood fill / islands        | DFS on grid        | Treat grid cells as graph nodes      |
'''

# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 5 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Graph = nodes (vertices) + edges (connections).
   - Represent as adjacency list (dict: node → list of neighbors)
2. BFS (queue): level by level. Finds shortest path in unweighted graphs.
3. DFS (stack/recursion): go deep, then backtrack.
   - Use for: connected components, cycle detection, topological sort
4. Number of Islands: DFS flood fill on a grid. Each '1' starts DFS.
5. Course Schedule: topological sort. If all nodes processed → no cycle.
6. ALWAYS track visited nodes to prevent infinite loops!

🎓 CONGRATULATIONS! You now know ALL the fundamental data structures!
   Next: Read the Patterns Cheat Sheet, then tackle Blind 75.
""")
