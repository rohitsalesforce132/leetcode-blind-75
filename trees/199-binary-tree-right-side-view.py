'''
LEETCODE #199: Binary Tree Right Side View
DIFFICULTY: Medium
TOPIC: Trees

=== PROBLEM STATEMENT ===
Given the root of a binary tree, imagine yourself standing on the right side of it,
return the values of the nodes you can see ordered from top to bottom.

=== INTUITION ===
1. The right side view consists of the rightmost node at each level.
2. Do a level-order traversal (BFS) and take the last node of each level.
3. Alternatively: DFS prioritizing the right child first, recording the first
   node encountered at each new depth.

=== APPROACHES ===
Approach 1: BFS — last node of each level
- Idea: Level-order traversal, append last element of each level to result.
- Time: O(n), Space: O(w)

Approach 2: DFS — right-first traversal
- Idea: Recurse right child first. When we reach a new depth (len(result)==depth),
  add node. Since we go right first, first node at each depth is rightmost.
- Time: O(n), Space: O(h)

=== DRY RUN ===
Tree:
        1
       / \
      2   3
       \   \
        5   4

BFS:
Level 0: [1] -> rightmost = 1
Level 1: [2, 3] -> rightmost = 3
Level 2: [5, 4] -> rightmost = 4
Result: [1, 3, 4]

DFS (right-first):
dfs(1, 0): depth 0 == len(result)=0 -> add 1. result=[1]
  dfs(3, 1): depth 1 == len(result)=1 -> add 3. result=[1,3]
    dfs(4, 2): depth 2 == len(result)=2 -> add 4. result=[1,3,4]
  dfs(2, 1): depth 1 < len(result)=3 -> skip (already have rightmost)
    dfs(5, 2): depth 2 < 3 -> skip
Result: [1, 3, 4]

=== COMPLEXITY ANALYSIS ===
Time: O(n)
Space: O(w) for BFS, O(h) for DFS

=== EDGE CASES ===
- Empty tree -> []
- Single node -> [root.val]
- Tree only has left children -> leftmost nodes visible from right side (just root)
- Complete vs skewed trees

=== INTERVIEW TIPS ===
- BFS is most intuitive — "last node per level".
- DFS right-first is elegant and O(h) space.
- Follow-up: left side view (reverse logic).
- Follow-up: zigzag view / all border nodes.
'''

# === SOLUTION ===

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def rightSideView(root):
    """BFS approach — take last node of each level."""
    from collections import deque
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:  # last node in level
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result


def rightSideView_dfs(root):
    """DFS right-first approach."""
    result = []

    def dfs(node, depth):
        if node is None:
            return
        if depth == len(result):  # first time reaching this depth
            result.append(node.val)
        dfs(node.right, depth + 1)  # right first!
        dfs(node.left, depth + 1)

    dfs(root, 0)
    return result


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
    print(rightSideView(build([1, 2, 3, None, 5, None, 4])))  # [1, 3, 4]

    # Test 2: single node
    print(rightSideView(TreeNode(1)))  # [1]

    # Test 3: empty
    print(rightSideView(None))  # []

    # Test 4: only left children
    print(rightSideView(build([1, 2, None, 3])))  # [1, 2, 3]

    # Test 5: DFS approach
    print(rightSideView_dfs(build([1, 2, 3, None, 5, None, 4])))  # [1, 3, 4]

    # Test 6: deeper tree
    print(rightSideView(build([1, 2, 3, 4, None, None, 5, None, 6])))  # [1,3,5,6]
