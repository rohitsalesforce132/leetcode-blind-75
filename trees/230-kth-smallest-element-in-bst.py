'''
LEETCODE #230: Kth Smallest Element in a BST
DIFFICULTY: Medium
TOPIC: Trees / BST

=== PROBLEM STATEMENT ===
Given the root of a binary search tree and an integer k, return the kth smallest
element (1-indexed) in the tree.

=== INTUITION ===
1. In-order traversal of a BST visits nodes in ascending order.
2. So the kth node visited in in-order is the kth smallest.
3. We can stop early once we've visited k nodes.

=== APPROACHES ===
Approach 1: Iterative in-order traversal (Optimal)
- Idea: Standard iterative in-order with stack. Pop the kth node.
- Time: O(H + k), Space: O(H)

Approach 2: Recursive in-order with counter
- Idea: Traverse in-order, count nodes. Return when count == k.
- Time: O(H + k), Space: O(H)

Approach 3: Full in-order to list, then index
- Idea: Traverse entire tree, collect values, return list[k-1].
- Time: O(n), Space: O(n)

=== DRY RUN ===
BST:
        5
       / \
      3   6
     / \
    2   4
   /
  1

k = 3
In-order: 1, 2, 3, 4, 5, 6
The 3rd element is 3.

Iterative:
stack=[5,3,2,1]
pop 1 -> count=1
pop 2 -> count=2
pop 3 -> count=3 == k -> return 3

=== COMPLEXITY ANALYSIS ===
Time: O(H + k) — go down to smallest (H steps), then k pops
Space: O(H) for the stack

=== EDGE CASES ===
- k = 1 (smallest element = leftmost node)
- k = n (largest element = rightmost node)
- Single node tree
- Skewed tree (all left / all right)
- k out of range (problem guarantees 1 <= k <= total nodes)

=== INTERVIEW TIPS ===
- In-order traversal of BST = sorted order. Memorize this.
- The iterative approach allows early termination after k nodes.
- Follow-up: If the tree is modified often (insert/delete) and we query kth
  often, augment the BST to store subtree sizes (Order Statistics Tree).
- Follow-up: kth LARGEST (reverse in-order: right, root, left).
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def kthSmallest(root, k):
    """Iterative in-order traversal."""
    stack = []
    node = root
    while stack or node:
        # Go as far left as possible
        while node:
            stack.append(node)
            node = node.left
        # Pop the next smallest
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        # Move to right subtree
        node = node.right


def kthSmallest_recursive(root, k):
    """Recursive in-order with early termination."""
    result = None
    count = 0

    def inorder(node):
        nonlocal result, count
        if node is None or result is not None:
            return
        inorder(node.left)
        count += 1
        if count == k:
            result = node.val
            return
        inorder(node.right)

    inorder(root)
    return result


# === TEST CASES ===
if __name__ == "__main__":
    def n(v, l=None, r=None):
        return TreeNode(v, l, r)

    # BST:
    #         5
    #        / \
    #       3   6
    #      / \
    #     2   4
    #    /
    #   1
    bst = n(5, n(3, n(2, n(1)), n(4)), n(6))

    # Test 1: k=3
    print(kthSmallest(bst, 3))  # 3

    # Test 2: k=1 (smallest)
    print(kthSmallest(bst, 1))  # 1

    # Test 3: k=6 (largest)
    print(kthSmallest(bst, 6))  # 6

    # Test 4: single node
    print(kthSmallest(TreeNode(1), 1))  # 1

    # Test 5: recursive
    print(kthSmallest_recursive(bst, 4))  # 4
