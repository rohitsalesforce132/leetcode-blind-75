'''
LEETCODE #102: Binary Tree Level Order Traversal
DIFFICULTY: Medium
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given the root of a binary tree, return the level order traversal of its nodes'
values (i.e., from left to right, level by level).

=== INTUITION ===
1. Level order = Breadth-First Search (BFS) using a queue.
2. Process nodes level by level: for each level, dequeue all current-level nodes,
   collect their values, enqueue their children.
3. The trick: capture the queue size at the start of each level, then process
   exactly that many nodes (this isolates one level).

=== APPROACHES ===
Approach 1: BFS with queue (Optimal)
- Idea: Standard BFS, track level size.
- Time: O(n), Space: O(w) where w = max width

Approach 2: Recursive DFS with level index
- Idea: Pre-order traversal, append node to result[level].
- Time: O(n), Space: O(h)

=== DRY RUN ===
Tree:
        3
       / \
      9  20
         / \
        15  7

Initial queue: [3], result = []
Level 1: size=1
  pop 3, append 3 to current level, enqueue 9 and 20
  queue now: [9, 20]
  result = [[3]]
Level 2: size=2
  pop 9 (leaf), enqueue nothing
  pop 20, enqueue 15 and 7
  queue now: [15, 7]
  result = [[3], [9, 20]]
Level 3: size=2
  pop 15 (leaf)
  pop 7 (leaf)
  result = [[3], [9, 20], [15, 7]]

Result: [[3], [9, 20], [15, 7]]

=== COMPLEXITY ANALYSIS ===
Time: O(n)
Space: O(w) — width of widest level

=== EDGE CASES ===
- Empty tree -> []
- Single node -> [[val]]
- Skewed tree (each level has 1 node)
- Perfect binary tree (last level has n/2 nodes)

=== INTERVIEW TIPS ===
- This is THE fundamental BFS pattern for trees.
- Know the "level size" trick: snapshot len(queue) before processing a level.
- Follow-up: zigzag level order (#103), right side view (#199).
- Follow-up: average of levels (#617).
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def levelOrder(root):
    """BFS with level-size tracking."""
    from collections import deque
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        level_vals = []
        for _ in range(level_size):
            node = queue.popleft()
            level_vals.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level_vals)
    return result


def levelOrder_dfs(root):
    """DFS approach: track level via recursion depth."""
    result = []

    def dfs(node, level):
        if node is None:
            return
        if len(result) == level:
            result.append([])  # first time reaching this level
        result[level].append(node.val)
        dfs(node.left, level + 1)
        dfs(node.right, level + 1)

    dfs(root, 0)
    return result


# === TEST CASES ===
if __name__ == "__main__":
    def build(values):
        if not values:
            return None
        from collections import deque
        root = TreeNode(values[0])
        q = deque([root])
        i = 1
        while q and i < len(values):
            node = q.popleft()
            if i < len(values) and values[i] is not None:
                node.left = TreeNode(values[i])
                q.append(node.left)
            i += 1
            if i < len(values) and values[i] is not None:
                node.right = TreeNode(values[i])
                q.append(node.right)
            i += 1
        return root

    # Test 1: standard tree
    print(levelOrder(build([3, 9, 20, None, None, 15, 7])))
    # [[3], [9, 20], [15, 7]]

    # Test 2: single node
    print(levelOrder(TreeNode(1)))  # [[1]]

    # Test 3: empty
    print(levelOrder(None))  # []

    # Test 4: complete tree
    print(levelOrder(build([1, 2, 3, 4, 5, 6, 7])))
    # [[1], [2, 3], [4, 5, 6, 7]]

    # Test 5: DFS approach
    print(levelOrder_dfs(build([3, 9, 20, None, None, 15, 7])))
    # [[3], [9, 20], [15, 7]]
