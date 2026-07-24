'''
LEETCODE #543: Diameter of Binary Tree
DIFFICULTY: Easy
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given the root of a binary tree, return the length of the diameter of the tree.
The diameter of a binary tree is the length of the longest path between any two
nodes in the tree. This path may or may not pass through the root.
The length of a path between two nodes is measured by the number of edges.

=== INTUITION ===
1. The longest path at any node = (depth of left subtree) + (depth of right subtree).
2. This is because the deepest path going through a node uses one edge to go down-left
   and one edge to go down-right.
3. We need to compute this for EVERY node, not just the root.
4. Use a post-order traversal: compute depths bottom-up, track max diameter seen.

Critical insight: The diameter does NOT always pass through the root!
Example: a tree shaped like a 'V' with two long arms — the diameter is the sum
of the two arms' depths.

=== APPROACHES ===
Approach 1: Recursive DFS with global max variable
- Idea: For each node, compute its depth (1 + max(L, R)). While computing,
  update diameter = max(diameter, L + R).
- Time: O(n), Space: O(h)

Approach 2: Brute force — for every node, compute depth of its subtrees
- Idea: For each node, diameter through it = depth(left) + depth(right).
  Recompute depths each time.
- Time: O(n^2), Space: O(h)

=== DRY RUN ===
Tree:
        1
       / \
      2   3
     / \
    4   5

dfs(4): L=0, R=0, diameter = max(0, 0+0)=0, return 1
dfs(5): L=0, R=0, diameter = max(0, 0+0)=0, return 1
dfs(2): L=1 (from 4), R=1 (from 5), diameter = max(0, 1+1)=2, return 1+max(1,1)=2
dfs(3): L=0, R=0, diameter stays 2, return 1
dfs(1): L=2 (from 2), R=1 (from 3), diameter = max(2, 2+1)=3, return 3

Result: 3
(Path: 4 -> 2 -> 1 -> 3, or 4 -> 2 -> 5... wait let me recheck.
 Actually the path is 3 edges: 4->2->1->3 has 3 edges? No: 4->2, 2->1, 1->3 = 3 edges. Yes!)

=== COMPLEXITY ANALYSIS ===
Time: O(n)
Space: O(h)

=== EDGE CASES ===
- Empty tree -> diameter 0
- Single node -> diameter 0 (no edges)
- Two nodes -> diameter 1
- Skewed tree -> diameter = n - 1
- Diameter passes through root vs not through root

=== INTERVIEW TIPS ===
- Clarify: diameter measured in edges (LeetCode) vs nodes.
- The key is updating a global/nonlocal variable during the DFS.
- Common follow-up: find the actual PATH (not just length).
- Mention that the diameter path doesn't have to go through the root.
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def diameterOfBinaryTree(root):
    """Optimal DFS with nonlocal diameter tracker."""
    diameter = 0

    def dfs(node):
        nonlocal diameter
        if node is None:
            return 0
        left = dfs(node.left)   # depth of left subtree
        right = dfs(node.right)  # depth of right subtree
        # The longest path through this node = left + right edges
        diameter = max(diameter, left + right)
        # Return depth of this subtree: 1 + max of children depths
        return 1 + max(left, right)

    dfs(root)
    return diameter


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

    # Test 1: diameter doesn't pass through root
    t1 = build([1, 2, 3, 4, 5])
    print(diameterOfBinaryTree(t1))  # 3

    # Test 2: single node
    print(diameterOfBinaryTree(TreeNode(1)))  # 0

    # Test 3: two nodes
    t3 = build([1, 2])
    print(diameterOfBinaryTree(t3))  # 1

    # Test 4: skewed tree (linked list shape)
    t4 = build([1, 2, None, 3, None, 4])
    print(diameterOfBinaryTree(t4))  # 3

    # Test 5: diameter through root
    t5 = build([1, 2, 3, 4, None, None, 5])
    print(diameterOfBinaryTree(t5))  # 4 (4->2->1->3->5)
