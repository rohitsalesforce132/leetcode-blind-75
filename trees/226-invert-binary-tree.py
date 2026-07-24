'''
LEETCODE #226: Invert Binary Tree
DIFFICULTY: Easy
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given the root of a binary tree, invert the tree, and return its root.
Inverting means swapping the left and right children of EVERY node.

=== INTUITION ===
1. This is the classic recursion problem.
2. For every node, we want to swap its left and right subtrees.
3. The base case: if the node is None, return None (nothing to invert).
4. Recursively invert the left subtree, then the right subtree.
5. After both are inverted, swap the pointers of current node.
6. The order of swap vs recursion doesn't matter due to independence.

Key insight: Each node's children get swapped exactly once. The recursion
handles the entire tree because we visit every node.

=== APPROACHES ===
Approach 1: Recursive DFS (Optimal)
- Idea: Recursively invert left and right, then swap pointers at current node.
- Time: O(n) — visit each node once
- Space: O(h) recursion stack where h = tree height (O(log n) balanced, O(n) skewed)

Approach 2: Iterative BFS using Queue
- Idea: Level-order traversal, swap children at each node dequeued.
- Time: O(n)
- Space: O(w) where w = max width of tree (up to n/2 for perfect tree)

Approach 3: Iterative DFS using Stack
- Idea: Use explicit stack instead of recursion.
- Time: O(n)
- Space: O(h)

=== DRY RUN ===
Tree:
        4
       / \
      2   7
     / \ / \
    1  3 6  9

invert(4):
  invert(2):
    invert(1): returns 1 (leaf)
    invert(3): returns 3 (leaf)
    swap: node 2 now has right=1, left=3
  invert(7):
    invert(6): returns 6
    invert(9): returns 9
    swap: node 7 now has right=6, left=9
  swap: node 4 now has right=2, left=7

Final:
        4
       / \
      7   2
     / \ / \
    9  6 3  1

=== COMPLEXITY ANALYSIS ===
Time: O(n)
Space: O(h) for recursion stack

=== EDGE CASES ===
- Empty tree (root is None)
- Single node tree
- Skewed tree (only left children / only right children)
- Large tree (watch recursion depth)

=== INTERVIEW TIPS ===
- Mention that recursion stack space matters for skewed trees (can cause stack overflow).
- Ask if in-place modification is required (it is here).
- Classic Google interview problem — simple but tests recursion fundamentals.
- Follow-up: can you do it iteratively? (Yes, with a queue/stack.)
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def invertTree(root):
    """Recursive DFS approach."""
    if root is None:
        return None
    # Recursively invert subtrees
    left_inverted = invertTree(root.left)
    right_inverted = invertTree(root.right)
    # Swap pointers
    root.left = right_inverted
    root.right = left_inverted
    return root


def invertTree_iterative(root):
    """Iterative BFS approach using a queue."""
    from collections import deque
    if not root:
        return None
    queue = deque([root])
    while queue:
        node = queue.popleft()
        # Swap children
        node.left, node.right = node.right, node.left
        # Enqueue children for processing
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return root


def build_tree(values):
    """Helper to build tree from level-order list [4,2,7,1,3,6,9]."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


def tree_to_list(root):
    """Level-order traversal to list for verification."""
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)
    # Strip trailing None values
    while result and result[-1] is None:
        result.pop()
    return result


# === TEST CASES ===
from collections import deque

if __name__ == "__main__":
    # Test 1: Standard tree
    root = build_tree([4, 2, 7, 1, 3, 6, 9])
    inverted = invertTree(root)
    print(tree_to_list(inverted))  # [4, 7, 2, 9, 6, 3, 1]

    # Test 2: Single node
    root = TreeNode(1)
    print(tree_to_list(invertTree(root)))  # [1]

    # Test 3: Empty tree
    print(tree_to_list(invertTree(None)))  # []

    # Test 4: Left-skewed tree
    root = build_tree([1, 2])
    print(tree_to_list(invertTree(root)))  # [1, None, 2]

    # Test 5: Iterative approach
    root = build_tree([4, 2, 7, 1, 3, 6, 9])
    inverted = invertTree_iterative(root)
    print(tree_to_list(inverted))  # [4, 7, 2, 9, 6, 3, 1]
