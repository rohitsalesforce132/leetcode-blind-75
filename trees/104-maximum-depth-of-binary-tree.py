'''
LEETCODE #104: Maximum Depth of Binary Tree
DIFFICULTY: Easy
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given the root of a binary tree, return its maximum depth.
The maximum depth is the number of nodes along the longest path from the root
node down to the farthest leaf node.

=== INTUITION ===
1. Depth of a node = 1 (itself) + max(depth(left), depth(right)).
2. If node is None, depth is 0.
3. Apply this recursively to get the tree's depth.

=== APPROACHES ===
Approach 1: Recursive DFS (most natural)
- Idea: return 1 + max(maxDepth(left), maxDepth(right))
- Time: O(n), Space: O(h) recursion stack

Approach 2: Iterative BFS (level counting)
- Idea: Count number of levels via BFS. Each level = one depth unit.
- Time: O(n), Space: O(w)

Approach 3: Iterative DFS with explicit stack
- Idea: Push (node, depth) tuples onto stack, track max.
- Time: O(n), Space: O(h)

=== DRY RUN ===
Tree:
        3
       / \
      9  20
         / \
        15  7

maxDepth(3):
  maxDepth(9): both children None -> return 1
  maxDepth(20):
    maxDepth(15) -> 1
    maxDepth(7) -> 1
    return 1 + max(1,1) = 2
  return 1 + max(1, 2) = 3

Result: 3

=== COMPLEXITY ANALYSIS ===
Time: O(n)
Space: O(h)

=== EDGE CASES ===
- Empty tree (root is None) -> depth 0
- Single node -> depth 1
- Skewed tree -> depth equals number of nodes
- Very deep tree (stack overflow risk in some languages, not Python)

=== INTERVIEW TIPS ===
- Start with recursive solution, it's the most intuitive.
- Be ready to write the iterative BFS version if asked.
- Clarify: is depth counted in nodes or edges? (LeetCode uses nodes.)
- Common follow-up: minimum depth (LeetCode 111).
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def maxDepth(root):
    """Recursive DFS."""
    if root is None:
        return 0
    left_depth = maxDepth(root.left)
    right_depth = maxDepth(root.right)
    return 1 + max(left_depth, right_depth)


def maxDepth_bfs(root):
    """Iterative BFS — count levels."""
    from collections import deque
    if not root:
        return 0
    depth = 0
    queue = deque([root])
    while queue:
        level_size = len(queue)
        for _ in range(level_size):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        depth += 1
    return depth


def maxDepth_dfs_iterative(root):
    """Iterative DFS with (node, depth) stack."""
    if not root:
        return 0
    stack = [(root, 1)]
    max_d = 0
    while stack:
        node, depth = stack.pop()
        max_d = max(max_d, depth)
        if node.left:
            stack.append((node.left, depth + 1))
        if node.right:
            stack.append((node.right, depth + 1))
    return max_d


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
    print(maxDepth(build([3, 9, 20, None, None, 15, 7])))  # 3

    # Test 2: single node
    print(maxDepth(TreeNode(1)))  # 1

    # Test 3: empty
    print(maxDepth(None))  # 0

    # Test 4: skewed left
    print(maxDepth(build([1, 2, None, 3])))  # 3

    # Test 5: BFS approach
    print(maxDepth_bfs(build([3, 9, 20, None, None, 15, 7])))  # 3

    # Test 6: DFS iterative
    print(maxDepth_dfs_iterative(build([3, 9, 20, None, None, 15, 7])))  # 3
