'''
LEETCODE #98: Validate Binary Search Tree
DIFFICULTY: Medium
TOPIC: Trees / BST

=== PROBLEM STATEMENT ===
Given the root of a binary tree, determine if it is a valid binary search tree (BST).
A valid BST is defined as:
- The left subtree of a node contains only nodes with keys less than the node's key.
- The right subtree of a node contains only nodes with keys greater than the node's key.
- Both the left and right subtrees must also be BSTs.

=== INTUITION ===
1. A BST's in-order traversal produces values in strictly increasing order.
   (The classic property.)
2. However, just checking left < root < right is NOT enough!
   Example: root=5, right child=10, right's left child=6. Here 6 > 5 (root),
   but local check (6 < 10) passes. Invalid!
3. We must track valid ranges (min, max) for each node as we recurse down.
4. As we go left: new max = parent's val. As we go right: new min = parent's val.

=== APPROACHES ===
Approach 1: DFS with min/max bounds (Optimal)
- Idea: Pass (low, high) bounds. Node must be in (low, high).
- Time: O(n), Space: O(h)

Approach 2: In-order traversal check
- Idea: Do in-order traversal, verify strictly increasing.
- Time: O(n), Space: O(h)

Approach 3: In-order with O(1) space (Morris traversal) — advanced
- Time: O(n), Space: O(1)

=== DRY RUN ===
Valid BST:
        5
       / \
      1   4
         / \
        3   6

isValid(5, -inf, inf):
  isValid(1, -inf, 5): 1 in range -> True (leaf)
  isValid(4, 5, inf):
    isValid(3, 5, 4): 3 < 5? NO -> False!
Result: False

Wait — but actually we can see: 3 is in the right subtree of 5, so it must be > 5.
But 3 < 5, so this is invalid. Correct!

Valid BST:
        2
       / \
      1   3

isValid(2, -inf, inf):
  isValid(1, -inf, 2): True
  isValid(3, 2, inf): True
Result: True

=== COMPLEXITY ANALYSIS ===
Time: O(n)
Space: O(h)

=== EDGE CASES ===
- Empty tree -> valid
- Single node -> valid
- Tree looks locally valid but globally invalid (see above)
- Integer overflow with bounds (use float('-inf'))
- Duplicate values (invalid in BST — must be STRICTLY less/greater)
- Very large values near INT_MAX/INT_MIN

=== INTERVIEW TIPS ===
- THE classic BST problem. The local check trap is the key point.
- Always use bounds approach or in-order approach, NOT just left<root<right.
- Clarify: strictly increasing (no duplicates allowed).
- Using float('-inf') avoids INT_MIN edge case where root = -2^31.
- Follow-up: is it a balanced BST?
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def isValidBST(root):
    """DFS with min/max bounds."""
    def validate(node, low, high):
        if node is None:
            return True
        if node.val <= low or node.val >= high:
            return False
        return (validate(node.left, low, node.val) and
                validate(node.right, node.val, high))

    return validate(root, float('-inf'), float('inf'))


def isValidBST_inorder(root):
    """In-order traversal must be strictly increasing."""
    prev = None

    def inorder(node):
        nonlocal prev
        if node is None:
            return True
        if not inorder(node.left):
            return False
        if prev is not None and node.val <= prev:
            return False
        prev = node.val
        return inorder(node.right)

    return inorder(root)


# === TEST CASES ===
if __name__ == "__main__":
    def n(v, l=None, r=None):
        return TreeNode(v, l, r)

    # Test 1: valid BST
    print(isValidBST(n(2, n(1), n(3))))  # True

    # Test 2: invalid BST (local check passes but global fails)
    print(isValidBST(n(5, n(1), n(4, n(3), n(6)))))  # False

    # Test 3: single node
    print(isValidBST(TreeNode(1)))  # True

    # Test 4: duplicate values
    print(isValidBST(n(2, n(2), n(2))))  # False

    # Test 5: boundary — root with only right subtree
    print(isValidBST(n(5, None, n(6, n(3), n(7)))))  # False (3 < 5 but in right subtree)

    # Test 6: in-order approach
    print(isValidBST_inorder(n(2, n(1), n(3))))  # True
