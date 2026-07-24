'''
LEETCODE #235: Lowest Common Ancestor of a Binary Search Tree
DIFFICULTY: Medium
TOPIC: Trees / BST

=== PROBLEM STATEMENT ===
Given a binary search tree (BST), find the lowest common ancestor (LCA) of two
given nodes p and q in the BST.
The LCA is the lowest node that has both p and q as descendants (a node can be
a descendant of itself).

=== INTUITION ===
1. In a BST, left subtree < node < right subtree.
2. If both p and q are less than current node, LCA is in the left subtree.
3. If both p and q are greater than current node, LCA is in the right subtree.
4. If one is <= and the other is >= (or one equals current), current node IS the LCA.
5. We can do this iteratively without recursion — just walk down.

Key insight: The first node where p and q "split" (go to different sides) is the LCA.

=== APPROACHES ===
Approach 1: Iterative walk (Optimal)
- Idea: Compare node.val with p.val and q.val, walk left or right.
- Time: O(h) = O(log n) balanced, Space: O(1)

Approach 2: Recursive
- Idea: Same logic but recursive calls.
- Time: O(h), Space: O(h) for recursion stack

=== DRY RUN ===
BST:
        6
       / \
      2   8
     / \ / \
    0  4 7  9
      / \
     3   5

Find LCA(2, 8):
node=6: 2 < 6 and 8 > 6 -> split! LCA = 6
Result: 6

Find LCA(2, 4):
node=6: both < 6 -> go left to node=2
node=2: p=2 == current -> LCA = 2 (2 is ancestor of itself)
Result: 2

Find LCA(3, 5):
node=6: both < 6 -> left to 2
node=2: both > 2 -> right to 4
node=4: 3 < 4 and 5 > 4 -> split! LCA = 4
Result: 4

=== COMPLEXITY ANALYSIS ===
Time: O(h) where h is tree height
Space: O(1) iterative, O(h) recursive

=== EDGE CASES ===
- p is ancestor of q (or vice versa) -> LCA is the ancestor
- p == q
- Root is LCA
- One node at a leaf, other deep
- Minimum tree (2 nodes)

=== INTERVIEW TIPS ===
- CRITICAL: Use the BST property! Don't treat it like a generic binary tree.
- Compare with LCA of Binary Tree (#236) which is O(n) since no BST property.
- The iterative approach is preferred (O(1) space).
- Clarify: all node values are unique, p != q, both exist in tree.
- Follow-up: what if nodes might not exist? (Need to verify existence first.)
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def lowestCommonAncestor(root, p, q):
    """Iterative approach using BST property."""
    node = root
    while node:
        if p.val < node.val and q.val < node.val:
            node = node.left   # both on left
        elif p.val > node.val and q.val > node.val:
            node = node.right  # both on right
        else:
            return node  # split point = LCA
    return None  # shouldn't reach here if p, q exist


def lowestCommonAncestor_recursive(root, p, q):
    """Recursive version."""
    if p.val < root.val and q.val < root.val:
        return lowestCommonAncestor_recursive(root.left, p, q)
    elif p.val > root.val and q.val > root.val:
        return lowestCommonAncestor_recursive(root.right, p, q)
    else:
        return root


# === TEST CASES ===
if __name__ == "__main__":
    def n(v, l=None, r=None):
        return TreeNode(v, l, r)

    # Build the BST from example
    #        6
    #       / \
    #      2   8
    #     / \ / \
    #    0  4 7  9
    #      / \
    #     3   5
    bst = n(6,
            n(2, n(0), n(4, n(3), n(5))),
            n(8, n(7), n(9)))

    # Test 1: LCA(2, 8)
    print(lowestCommonAncestor(bst, bst.left, bst.right).val)  # 6

    # Test 2: LCA(2, 4)
    print(lowestCommonAncestor(bst, bst.left, bst.left.right).val)  # 2

    # Test 3: LCA(0, 5) -> should be 2
    print(lowestCommonAncestor(bst, bst.left.left, bst.left.right.right).val)  # 2

    # Test 4: LCA(3, 5) -> should be 4
    print(lowestCommonAncestor(bst, bst.left.right.left, bst.left.right.right).val)  # 4

    # Test 5: recursive
    print(lowestCommonAncestor_recursive(bst, bst.left, bst.right).val)  # 6
