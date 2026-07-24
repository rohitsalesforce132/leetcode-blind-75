'''
LEETCODE #100: Same Tree
DIFFICULTY: Easy
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given the roots of two binary trees p and q, write a function to check if they
are the same. Two binary trees are considered the same if they are structurally
identical and the nodes have the same value.

=== INTUITION ===
1. Two trees are the same if their roots match, AND their left subtrees match,
   AND their right subtrees match.
2. Base cases:
   - Both None -> True (same empty trees)
   - One None, one not -> False (structurally different)
3. Recursively compare left and right children.

=== APPROACHES ===
Approach 1: Recursive DFS
- Idea: Check roots equal, recurse on left and right.
- Time: O(n), Space: O(h)

Approach 2: Iterative BFS/DFS with two queues/stacks
- Idea: Traverse both trees in parallel, compare node by node.
- Time: O(n), Space: O(h)

=== DRY RUN ===
Tree P:        Tree Q:
     1              1
    / \            / \
   2   3          2   3

isSameTree(1, 1): vals equal
  isSameTree(2, 2): vals equal
    isSameTree(None, None) -> True
    isSameTree(None, None) -> True
    return True
  isSameTree(3, 3): vals equal -> True
  return True
Result: True

Tree P:        Tree Q:
     1              1
    /                \
   2                  2

isSameTree(1, 1): vals equal
  isSameTree(2, None) -> False (one None, one not)
Result: False

=== COMPLEXITY ANALYSIS ===
Time: O(n) — visit each node once (min of both trees)
Space: O(h)

=== EDGE CASES ===
- Both empty -> True
- One empty, one not -> False
- Same structure, different values -> False
- Different structure, same values -> False
- Very deep trees (recursion depth)

=== INTERVIEW TIPS ===
- Very clean recursion — start here.
- Follow-up: isSubtree (LeetCode 572) builds on this.
- Follow-up: symmetric tree (LeetCode 101) — compare tree to its mirror.
- Clarify whether to compare by value or by reference (it's by value+structure).
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def isSameTree(p, q):
    """Recursive DFS comparison."""
    # Both empty
    if p is None and q is None:
        return True
    # One empty, one not
    if p is None or q is None:
        return False
    # Both non-empty: check value and recurse
    if p.val != q.val:
        return False
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)


def isSameTree_iterative(p, q):
    """Iterative BFS using two queues."""
    from collections import deque
    queue = deque([(p, q)])
    while queue:
        node1, node2 = queue.popleft()
        if node1 is None and node2 is None:
            continue
        if node1 is None or node2 is None:
            return False
        if node1.val != node2.val:
            return False
        queue.append((node1.left, node2.left))
        queue.append((node1.right, node2.right))
    return True


# === TEST CASES ===
if __name__ == "__main__":
    def n(v, l=None, r=None):
        return TreeNode(v, l, r)

    # Test 1: identical trees
    p = n(1, n(2), n(3))
    q = n(1, n(2), n(3))
    print(isSameTree(p, q))  # True

    # Test 2: different structure
    p = n(1, n(2))
    q = n(1, None, n(2))
    print(isSameTree(p, q))  # False

    # Test 3: different values
    p = n(1, n(2), n(1))
    q = n(1, n(1), n(2))
    print(isSameTree(p, q))  # False

    # Test 4: both empty
    print(isSameTree(None, None))  # True

    # Test 5: single node same
    print(isSameTree(TreeNode(5), TreeNode(5)))  # True

    # Test 6: iterative approach
    p = n(1, n(2), n(3))
    q = n(1, n(2), n(3))
    print(isSameTree_iterative(p, q))  # True
