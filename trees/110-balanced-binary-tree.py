'''
LEETCODE #110: Balanced Binary Tree
DIFFICULTY: Easy
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given a binary tree, determine if it is height-balanced:
- A height-balanced binary tree is a binary tree in which the left and right
  subtrees of every node differ in height by no more than 1.

=== INTUITION ===
1. For each node, check if |height(left) - height(right)| <= 1.
2. AND both subtrees must themselves be balanced.
3. Naive: recursively call isBalanced + height for each node -> O(n^2).
4. Better: combine into single DFS. Return height if balanced, signal if not.
   Use -1 as a sentinel meaning "unbalanced subtree detected".

Key insight: We can detect imbalance early and propagate it upward. If any
subtree is unbalanced, we can short-circuit and return -1 all the way up.

=== APPROACHES ===
Approach 1: Bottom-up DFS with sentinel (Optimal)
- Idea: dfs returns height if balanced, -1 if unbalanced. Parent checks children.
- Time: O(n), Space: O(h)

Approach 2: Top-down (brute force)
- Idea: At each node, compute height(left) and height(right), check |diff|<=1,
  then recursively check both children.
- Time: O(n^2) since height is recomputed at each node, Space: O(h)

=== DRY RUN ===
Balanced tree:
        3
       / \
      9  20
         / \
        15  7

dfs(9): L=0,R=0 -> return 1 (balanced, height 1)
dfs(15): return 1
dfs(7): return 1
dfs(20): L=1, R=1, diff=0 <= 1 -> return 2
dfs(3): L=1, R=2, diff=1 <= 1 -> return 3
isBalanced = True (root returned 3, not -1)

Unbalanced tree:
        1
       /
      2
     /
    3

dfs(3): return 1
dfs(2): L=1, R=0, diff=1 -> return 2
dfs(1): L=2, R=0, diff=2 > 1 -> return -1 (UNBALANCED!)
isBalanced = False (root returned -1)

=== COMPLEXITY ANALYSIS ===
Time: O(n)
Space: O(h)

=== EDGE CASES ===
- Empty tree -> balanced (True)
- Single node -> balanced (True)
- Skewed tree (all left or all right) -> unbalanced
- Only the root's immediate children differ by >1

=== INTERVIEW TIPS ===
- Start with the brute force O(n^2) approach, then optimize to O(n).
- The sentinel (-1) trick is elegant — mention it.
- Clarify: balanced means EVERY node, not just root.
- Follow-up: balance the tree (AVL rotation logic).
- Python: use nonlocal or instance variable instead of sentinel if preferred.
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def isBalanced(root):
    """Bottom-up DFS. Returns height if balanced, -1 if not."""
    def dfs(node):
        if node is None:
            return 0
        left = dfs(node.left)
        if left == -1:
            return -1  # propagate imbalance up
        right = dfs(node.right)
        if right == -1:
            return -1
        if abs(left - right) > 1:
            return -1  # mark this subtree as unbalanced
        return 1 + max(left, right)

    return dfs(root) != -1


def isBalanced_bruteforce(root):
    """Top-down O(n^2) approach for comparison."""
    def height(node):
        if node is None:
            return 0
        return 1 + max(height(node.left), height(node.right))

    if root is None:
        return True
    if abs(height(root.left) - height(root.right)) > 1:
        return False
    return isBalanced_bruteforce(root.left) and isBalanced_bruteforce(root.right)


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

    # Test 1: balanced tree
    print(isBalanced(build([3, 9, 20, None, None, 15, 7])))  # True

    # Test 2: unbalanced tree
    print(isBalanced(build([1, None, 2, None, 3])))  # False

    # Test 3: empty tree
    print(isBalanced(None))  # True

    # Test 4: single node
    print(isBalanced(TreeNode(1)))  # True

    # Test 5: deeply unbalanced
    print(isBalanced(build([1, 2, 2, 3, None, None, 3, 4, None, None, 4])))  # False
