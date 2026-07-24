'''
LEETCODE #105: Construct Binary Tree from Preorder and Inorder Traversal
DIFFICULTY: Medium
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given two integer arrays preorder and inorder where preorder is the preorder
traversal of a binary tree and inorder is the inorder traversal of the same tree,
construct and return the binary tree.

=== INTUITION ===
1. Preorder = [root, left-subtree..., right-subtree...]
   The first element is ALWAYS the root.
2. Inorder = [left-subtree..., root, right-subtree...]
   The root splits inorder into left and right parts.
3. Algorithm:
   a. Pop the first element from preorder -> that's the root.
   b. Find that root in inorder. Everything left of it = left subtree,
      everything right = right subtree.
   c. Recurse.
4. Optimization: use a hash map to find root index in O(1).

=== APPROACHES ===
Approach 1: Recursive with hash map (Optimal)
- Idea: pre_idx pointer walks preorder; hashmap maps value->index in inorder.
- Time: O(n), Space: O(n)

Approach 2: Recursive without hash map
- Idea: Use .index() to find root in inorder each time.
- Time: O(n^2) worst case, Space: O(n)

=== DRY RUN ===
preorder = [3, 9, 20, 15, 7]
inorder  = [9, 3, 15, 20, 7]

inorder_map: {9:0, 3:1, 15:2, 20:3, 7:4}

build(left=0, right=5) [range in inorder]:
  pre_idx=0, root_val = preorder[0] = 3
  root_index in inorder = 1
  root.left = build(0, 1)  # inorder[0:1] = [9]
    pre_idx=1, root_val = preorder[1] = 9
    root_index = 0
    root.left = build(0, 0) -> None (empty range)
    root.right = build(1, 1) -> None
    returns TreeNode(9)
  root.right = build(2, 5)  # inorder[2:5] = [15, 20, 7]
    pre_idx=2, root_val = preorder[2] = 20
    root_index = 3
    root.left = build(2, 3)  # inorder[2:3] = [15]
      pre_idx=3, root_val = 15
      returns TreeNode(15)
    root.right = build(4, 5)  # inorder[4:5] = [7]
      pre_idx=4, root_val = 7
      returns TreeNode(7)
    returns TreeNode(20, left=15, right=7)
  returns TreeNode(3, left=9, right=20)

Result:
        3
       / \
      9  20
         / \
        15  7

=== COMPLEXITY ANALYSIS ===
Time: O(n) with hash map
Space: O(n) for hash map + O(h) recursion stack

=== EDGE CASES ===
- Empty arrays -> None
- Single node
- Left-skewed tree (preorder and inorder are identical... wait no)
  Actually: left-skewed means preorder=[1,2,3], inorder=[3,2,1]
- Right-skewed tree: preorder=[1,2,3], inorder=[1,2,3]
- Duplicate values: problem guarantees all values are unique

=== INTERVIEW TIPS ===
- The hash map optimization is critical — mention it immediately.
- Draw the two arrays side by side to explain the split.
- The pre_idx pointer must be a nonlocal/global so it advances correctly across
  recursive calls.
- Follow-up: construct from inorder + postorder (#106) — similar idea, root is
  LAST element of postorder.
- Follow-up: serialize/deserialize a tree (#297).
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def buildTree(preorder, inorder):
    """Recursive construction with hash map for O(1) root lookup."""
    inorder_map = {val: idx for idx, val in enumerate(inorder)}
    pre_idx = 0  # pointer into preorder

    def build(left, right):
        """Build subtree whose inorder values are in [left, right)."""
        nonlocal pre_idx
        if left >= right:
            return None
        root_val = preorder[pre_idx]
        pre_idx += 1
        root = TreeNode(root_val)
        root_idx = inorder_map[root_val]
        # Left subtree comes first in preorder, so build it first
        root.left = build(left, root_idx)
        root.right = build(root_idx + 1, right)
        return root

    return build(0, len(inorder))


# === TEST CASES ===
if __name__ == "__main__":
    def tree_to_list(root):
        if not root:
            return []
        from collections import deque
        result = []
        q = deque([root])
        while q:
            node = q.popleft()
            if node:
                result.append(node.val)
                q.append(node.left)
                q.append(node.right)
            else:
                result.append(None)
        while result and result[-1] is None:
            result.pop()
        return result

    # Test 1: standard tree
    root = buildTree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
    print(tree_to_list(root))  # [3, 9, 20, None, None, 15, 7]

    # Test 2: single node
    root = buildTree([1], [1])
    print(tree_to_list(root))  # [1]

    # Test 3: empty
    print(buildTree([], []))  # None

    # Test 4: left-skewed
    root = buildTree([3, 2, 1], [1, 2, 3])
    print(tree_to_list(root))  # [3, 2, None, 1]

    # Test 5: right-skewed
    root = buildTree([1, 2, 3], [1, 2, 3])
    print(tree_to_list(root))  # [1, None, 2, None, 3]
