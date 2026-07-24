'''
LEETCODE #572: Subtree of Another Tree
DIFFICULTY: Easy
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given the roots of two binary trees root and subRoot, return true if there is a
subtree of root with the same structure and node values as subRoot.

=== INTUITION ===
1. A subtree is a tree consisting of a node in the main tree and all of its descendants.
2. We need to check if any node in `root` has an identical tree matching `subRoot`.
3. For each node in root, check if the tree rooted there is identical to subRoot.
4. Use the "Same Tree" function (LeetCode 100) as a helper.
5. If root matches subRoot at the current node OR recursively in left or right.

=== APPROACHES ===
Approach 1: DFS + Same Tree check
- Idea: At each node of root, call isSameTree(node, subRoot).
- Time: O(root_nodes * subRoot_nodes) worst case, but often better in practice.
- Space: O(h_root)

Approach 2: Serialize both trees (Merlin) then string search
- Idea: Convert trees to strings via pre-order traversal, check if subRoot string
  is a substring of root string. Use KMP or substring search.
- Time: O(|root| + |subRoot|), Space: O(|root| + |subRoot|)

Approach 3: Merkle hashing
- Idea: Hash each subtree, compare hashes.
- Time: O(n), Space: O(n)

=== DRY RUN ===
root:           subRoot:
      3               4
     / \             / \
    4   5           1   2
   / \
  1   2

Check node(3): isSameTree(3, 4)? No (3 != 4)
Check node(4): isSameTree(4, 4)?
  Compare children: isSameTree(1,1)=T, isSameTree(2,2)=T -> True!
Result: True

=== COMPLEXITY ANALYSIS ===
Time: O(R * S) where R=nodes in root, S=nodes in subRoot
Space: O(h_root + h_subRoot)

=== EDGE CASES ===
- subRoot is empty -> technically True (empty tree is subtree of anything)
- root is empty, subRoot not -> False
- root == subRoot (identical) -> True
- subRoot larger than root -> impossible to be subtree -> False
- subRoot matches at root level
- subRoot matches at a leaf

=== INTERVIEW TIPS ===
- This problem combines tree traversal with isSameTree (LeetCode 100).
- The serialization approach is O(n) and worth mentioning as optimization.
- Clarify: subtree must include ALL descendants (not just a partial match).
- Follow-up: count number of subtrees that match.
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def isSubtree(root, subRoot):
    """DFS at each node, check isSameTree."""
    if root is None:
        return subRoot is None

    def is_same(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return (a.val == b.val and
                is_same(a.left, b.left) and
                is_same(a.right, b.right))

    if is_same(root, subRoot):
        return True
    return isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)


def isSubtree_serialization(root, subRoot):
    """O(n) approach using tree serialization + substring search."""
    def serialize(node):
        if node is None:
            return "#"
        return f"({node.val},{serialize(node.left)},{serialize(node.right)})"

    root_str = serialize(root)
    sub_str = serialize(subRoot)
    return sub_str in root_str


# === TEST CASES ===
if __name__ == "__main__":
    def n(v, l=None, r=None):
        return TreeNode(v, l, r)

    # Test 1: subRoot is a subtree
    root = n(3, n(4, n(1), n(2)), n(5))
    sub = n(4, n(1), n(2))
    print(isSubtree(root, sub))  # True

    # Test 2: subRoot not a subtree (extra node in sub)
    root = n(3, n(4, n(1), n(2, n(0))), n(5))
    sub = n(4, n(1), n(2))
    print(isSubtree(root, sub))  # False

    # Test 3: identical trees
    root = n(1, n(2), n(3))
    sub = n(1, n(2), n(3))
    print(isSubtree(root, sub))  # True

    # Test 4: empty subRoot
    print(isSubtree(TreeNode(1), None))  # True

    # Test 5: serialization approach
    root = n(3, n(4, n(1), n(2)), n(5))
    sub = n(4, n(1), n(2))
    print(isSubtree_serialization(root, sub))  # True
