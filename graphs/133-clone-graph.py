'''
LEETCODE #133: Clone Graph
DIFFICULTY: Medium
TOPIC: Graphs

=== PROBLEM STATEMENT ===
Given a reference of a node in a connected undirected graph, return a deep copy
(clone) of the graph. Each node has a value (int) and a list of neighbors (List[Node]).

Node class:
    class Node:
        def __init__(self, val=0, neighbors=None):
            self.val = val
            self.neighbors = neighbors if neighbors is not None else []

=== INTUITION ===
We need to create new nodes that mirror the original graph structure exactly,
but share NO references with the original. The key challenge: when we clone node A
and see its neighbor B, we need to make sure we don't clone B twice (B might be
reachable via multiple paths). So we use a HashMap (old_node -> new_node) as a
"visited" cache. BFS or DFS both work.

=== APPROACHES ===
Approach 1: BFS
- Idea: Start BFS from the input node. For each node dequeued, check each neighbor.
  If neighbor not cloned yet, create clone + add to queue. Always link cloned
  neighbor to cloned current node. Use a dict {original: clone} to avoid duplicates.
- Time: O(V + E) — visit every node and edge once
- Space: O(V) — for the hashmap and queue

Approach 2: DFS (Recursive)
- Idea: Same idea, recursively clone. Base case: if node already cloned, return clone.
  Otherwise create clone, then for each neighbor, recursively clone it and append
  to clone.neighbors.
- Time: O(V + E)
- Space: O(V) — hashmap + recursion stack

=== DRY RUN (BFS) ===
Input graph:  1 -- 2
              |    |
              4 -- 3

Step 1: clone_map = {}, queue = [Node(1)]
Step 2: Pop Node(1). Create clone(1). clone_map = {1: clone1}
        Neighbors of 1: [2, 4]
        - 2 not cloned → create clone(2), add to map + queue
        - 4 not cloned → create clone(4), add to map + queue
        clone1.neighbors = [clone2, clone4]
Step 3: Pop Node(2). clone(2) already exists.
        Neighbors of 2: [1, 3]
        - 1 already cloned → add clone1 to clone2.neighbors
        - 3 not cloned → create clone(3), add to map + queue
        clone2.neighbors = [clone1, clone3]
Step 4: Pop Node(4). Neighbors: [1, 3]
        - 1 already cloned → add clone1
        - 3 already cloned → add clone3
Step 5: Pop Node(3). Neighbors: [2, 4]
        - Both already cloned → add clone2, clone4

Result: Fully cloned graph with identical structure.

=== COMPLEXITY ANALYSIS ===
Time: O(V + E) — each node and edge processed exactly once
Space: O(V) — hashmap stores all V cloned nodes + queue/recursion

=== EDGE CASES ===
- Input node is None → return None
- Single node with no neighbors → return single cloned node
- Self-loop (node is its own neighbor) → handle via map check

=== INTERVIEW TIPS ===
- Always clarify: is the graph guaranteed connected? (Here yes.)
- Mention the HashMap is critical to avoid infinite loops (cycles) and duplicate clones
- Follow-up: How would you handle a disconnected graph? (Iterate over all nodes)
'''

# === SOLUTION (BFS) ===

from collections import deque

class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def cloneGraph(node: 'Node') -> 'Node':
    if not node:
        return None

    # Map from original node to its clone
    old_to_new = {}

    # Clone the starting node
    old_to_new[node] = Node(node.val)

    # BFS
    queue = deque([node])

    while queue:
        current = queue.popleft()

        for neighbor in current.neighbors:
            if neighbor not in old_to_new:
                # Clone this neighbor
                old_to_new[neighbor] = Node(neighbor.val)
                queue.append(neighbor)
            # Link clone of neighbor to clone of current
            old_to_new[current].neighbors.append(old_to_new[neighbor])

    return old_to_new[node]


# === DFS APPROACH (Alternative) ===

def cloneGraphDFS(node: 'Node') -> 'Node':
    if not node:
        return None

    old_to_new = {}

    def dfs(old_node):
        if old_node in old_to_new:
            return old_to_new[old_node]

        # Create clone
        clone = Node(old_node.val)
        old_to_new[old_node] = clone

        for neighbor in old_node.neighbors:
            clone.neighbors.append(dfs(neighbor))

        return clone

    return dfs(node)


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Simple 2-node graph: 1 -- 2
    n1 = Node(1)
    n2 = Node(2)
    n1.neighbors = [n2]
    n2.neighbors = [n1]

    cloned = cloneGraph(n1)
    assert cloned.val == 1
    assert cloned.neighbors[0].val == 2
    assert cloned is not n1  # Different objects (deep copy)
    print("Test 1 passed: 2-node graph cloned correctly")

    # Test 2: Empty graph
    assert cloneGraph(None) is None
    print("Test 2 passed: None input returns None")

    # Test 3: Single node, no neighbors
    single = Node(5)
    cloned_single = cloneGraph(single)
    assert cloned_single.val == 5
    assert len(cloned_single.neighbors) == 0
    assert cloned_single is not single
    print("Test 3 passed: Single node cloned correctly")

    # Test 4: 4-node cycle: 1-2-3-4-1
    a, b, c, d = Node(1), Node(2), Node(3), Node(4)
    a.neighbors = [b, d]
    b.neighbors = [a, c]
    c.neighbors = [b, d]
    d.neighbors = [c, a]

    cloned4 = cloneGraph(a)
    assert cloned4.val == 1
    assert cloned4.neighbors[0].val == 2
    assert cloned4.neighbors[1].val == 4
    assert cloned4.neighbors[0].neighbors[1].val == 3
    print("Test 4 passed: 4-node cycle cloned correctly")

    print("\n✅ All tests passed!")
