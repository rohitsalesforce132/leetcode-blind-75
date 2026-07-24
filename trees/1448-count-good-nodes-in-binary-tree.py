'''
LEETCODE #1448: Count Good Nodes in Binary Tree
DIFFICULTY: Medium
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given a binary tree root, a node X in the tree is named "good" if in the path
from root to X there are no nodes with a value greater than X.
Return the number of good nodes in the binary tree.

=== INTUITION ===
1. A node is "good" if its value >= every value on the root-to-node path.
2. As we traverse, track the maximum value seen so far on the path.
3. At each node: if node.val >= max_so_far, it's good. Update max_so_far for children.
4. Pre-order DFS (or BFS) works.

=== APPROACHES ===
Approach 1: DFS tracking max-so-far
- Idea: Recurse, passing the running maximum down the path.
- Time: O(n), Space: O(h)

Approach 2: BFS with (node, max_so_far) pairs
- Idea: Level-order, track max per path.
- Time: O(n), Space: O(w)

=== DRY RUN ===
Tree:
        3
       / \
      1   4
     /   / \
    3   1   5

DFS(root=3, max_so_far=-inf):
  3 >= -inf -> good! count=1, max_so_far=3
  dfs(1, max=3):
    1 < 3 -> not good. count stays 1
    dfs(3, max=3):
      3 >= 3 -> good! count=2
  dfs(4, max=3):
    4 >= 3 -> good! count=3, max=4
    dfs(1, max=4):
      1 < 4 -> not good
    dfs(5, max=4):
      5 >= 4 -> good! count=4

Result: 4

=== COMPLEXITY ANALYSIS ===
Time: O(n)
Space: O(h)

=== EDGE CASES ===
- Empty tree -> 0
- Single node -> 1 (root is always good)
- All nodes increasing down path -> all good
- All nodes decreasing down path -> only root is good
- Negative values

=== INTERVIEW TIPS ===
- Clarify: "greater" means strictly greater, so equal values are good.
- The key is passing state (max so far) down the recursion.
- Follow-up: count bad nodes, find path with most good nodes.
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def goodNodes(root):
    """DFS tracking the max value seen on the path."""
    def dfs(node, max_so_far):
        if node is None:
            return 0
        count = 0
        if node.val >= max_so_far:
            count = 1
            max_so_far = node.val
        count += dfs(node.left, max_so_far)
        count += dfs(node.right, max_so_far)
        return count

    return dfs(root, float('-inf'))


def goodNodes_bfs(root):
    """BFS approach with (node, max_so_far) pairs."""
    from collections import deque
    if not root:
        return 0
    count = 0
    queue = deque([(root, float('-inf'))])
    while queue:
        node, max_so_far = queue.popleft()
        if node.val >= max_so_far:
            count += 1
            max_so_far = node.val
        if node.left:
            queue.append((node.left, max_so_far))
        if node.right:
            queue.append((node.right, max_so_far))
    return count


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
    print(goodNodes(build([3, 1, 4, 3, None, 1, 5])))  # 4

    # Test 2: single node
    print(goodNodes(TreeNode(3)))  # 1

    # Test 3: decreasing values
    print(goodNodes(build([3, 2, 1])))  # 1 (only root)

    # Test 4: increasing path
    print(goodNodes(build([1, 2, 3])))  # 3

    # Test 5: negative values
    print(goodNodes(build([-1, -2, -3])))  # 1

    # Test 6: BFS approach
    print(goodNodes_bfs(build([3, 1, 4, 3, None, 1, 5])))  # 4
