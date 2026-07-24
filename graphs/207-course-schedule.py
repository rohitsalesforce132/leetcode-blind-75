'''
LEETCODE #207: Course Schedule
DIFFICULTY: Medium
TOPIC: Graphs

=== PROBLEM STATEMENT ===
There are numCourses courses labeled 0 to numCourses-1. You are given an array
prerequisites where prerequisites[i] = [a, b] means you must take course b before
course a (b → a). Return True if you can finish all courses (no cyclic dependency).
Otherwise return False.

=== INTUITION ===
This is a classic CYCLE DETECTION problem in a directed graph.
- Courses = nodes
- Prerequisites = directed edges (b → a means "b must come before a")
- If there's a cycle, you can never complete all courses (deadlock).
- So: detect if the directed graph has a cycle.

Two approaches: Kahn's Algorithm (BFS topological sort) or DFS cycle detection.

=== APPROACHES ===
Approach 1: BFS — Kahn's Algorithm (Topological Sort)
- Idea: Compute in-degree of every node. Add all nodes with in-degree 0 to queue.
  Process queue: for each node, reduce in-degree of neighbors. If neighbor
  in-degree becomes 0, add to queue. If we process ALL nodes → no cycle (True).
  If some nodes remain unprocessed → cycle exists (False).
- Time: O(V + E)
- Space: O(V + E)

Approach 2: DFS with 3-color marking
- Idea: Use WHITE (unvisited), GRAY (visiting/in current DFS path), BLACK (done).
  If DFS encounters a GRAY node → cycle detected.
- Time: O(V + E)
- Space: O(V + E)

=== DRY RUN (Kahn's BFS) ===
numCourses = 4, prerequisites = [[1,0], [2,1], [3,2], [1,3]]

Graph (adjacency list): 0 → [1], 1 → [2], 2 → [3], 3 → [1]
In-degrees: 0:0, 1:2, 2:1, 3:1

Step 1: In-degree 0 nodes: [0]. Queue = [0]
Step 2: Process 0. Neighbor 1: in-degree 2→1. Queue = []
        No nodes with in-degree 0 → STUCK.
        Processed count = 1 ≠ 4 → CYCLE → return False!

Dry run 2 (no cycle):
numCourses = 4, prerequisites = [[1,0], [2,0], [3,1], [3,2]]

Graph: 0 → [1, 2], 1 → [3], 2 → [3]
In-degrees: 0:0, 1:1, 2:1, 3:2

Step 1: In-degree 0: [0]. Queue = [0]
Step 2: Process 0. Neighbors 1,2: in-degree → 0,0. Queue = [1, 2]
Step 3: Process 1. Neighbor 3: in-degree → 1. Queue = [2]
Step 4: Process 2. Neighbor 3: in-degree → 0. Queue = [3]
Step 5: Process 3. No neighbors. Queue = []
Process count = 4 = numCourses → No cycle → return True!

=== COMPLEXITY ANALYSIS ===
Time: O(V + E) — each node enters queue once, each edge traversed once
Space: O(V + E) — adjacency list + in-degree array + queue

=== EDGE CASES ===
- No prerequisites → return True (no dependencies)
- Single course → True
- Self-dependency [a, a] → cycle → False
- Multiple edges between same pair → handle via adjacency list

=== INTERVIEW TIPS ===
- Recognize immediately: "Can I complete all courses?" = "Does the dependency graph have a cycle?"
- Kahn's algorithm is often preferred because it also gives you the topological ORDER
- Follow-up (LeetCode 210): Return the actual ordering of courses
'''

# === SOLUTION (BFS — Kahn's Algorithm) ===

from collections import deque, defaultdict

def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    # Build adjacency list and in-degree array
    adj = defaultdict(list)
    in_degree = [0] * numCourses

    for course, prereq in prerequisites:
        adj[prereq].append(course)
        in_degree[course] += 1

    # Start with all courses that have no prerequisites
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])

    completed = 0

    while queue:
        current = queue.popleft()
        completed += 1

        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return completed == numCourses


# === DFS APPROACH (3-color cycle detection) ===

def canFinishDFS(numCourses: int, prerequisites: list[list[int]]) -> bool:
    adj = defaultdict(list)
    for course, prereq in prerequisites:
        adj[prereq].append(course)

    # 0 = WHITE (unvisited), 1 = GRAY (visiting), 2 = BLACK (done)
    color = [0] * numCourses

    def dfs(node):
        if color[node] == 1:  # Cycle detected
            return False
        if color[node] == 2:  # Already fully processed
            return True

        color[node] = 1  # Mark as visiting

        for neighbor in adj[node]:
            if not dfs(neighbor):
                return False

        color[node] = 2  # Mark as done
        return True

    for i in range(numCourses):
        if color[i] == 0:
            if not dfs(i):
                return False

    return True


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: No cycle — can finish
    assert canFinish(2, [[1, 0]]) == True
    print("Test 1 passed: 2 courses, 1→0, no cycle")

    # Test 2: Cycle — cannot finish
    assert canFinish(2, [[1, 0], [0, 1]]) == False
    print("Test 2 passed: 2 courses with cycle → False")

    # Test 3: No prerequisites
    assert canFinish(5, []) == True
    print("Test 3 passed: 5 courses, no prereqs → True")

    # Test 4: Linear chain 0→1→2→3
    assert canFinish(4, [[1, 0], [2, 1], [3, 2]]) == True
    print("Test 4 passed: Linear chain, no cycle")

    # Test 5: Complex cycle
    assert canFinish(4, [[1, 0], [2, 1], [3, 2], [1, 3]]) == False
    print("Test 5 passed: Cycle 1→2→3→1 → False")

    # Test 6: Single course
    assert canFinish(1, []) == True
    print("Test 6 passed: Single course → True")

    print("\n✅ All tests passed!")
