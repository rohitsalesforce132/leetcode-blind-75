'''
CHAPTER 4: TREES, BINARY SEARCH TREES, HEAPS & TRIES
=====================================================

"These four data structures are all based on the same idea: a HIERARCHY.
A tree is like a family tree. A BST is a sorted tree. A heap is a
priority tree. A trie is a word tree."

CHAPTER ROADMAP
---------------
PART 1: Binary Trees        — structure, traversals, the recursion pattern
PART 2: Binary Search Trees — the sorted tree, search/insert/validate
PART 3: Heaps               — priority queues, Top-K problems
PART 4: Tries               — prefix trees, autocomplete, word search


PART 1: TREES (BINARY TREES)
=============================

WHAT IS A TREE?
---------------
Real-world analogy: A FAMILY TREE or a COMPANY ORG CHART.

                CEO
               /   \
            VP Eng  VP Sales
           /   \      |
       Lead1  Lead2  Rep1

- The top node is called the ROOT.
- Each node has 0, 1, or 2 CHILDREN (in a binary tree).
- Nodes with no children are called LEAVES.
- The ROOT has no parent; all other nodes have exactly one parent.

A BINARY TREE is a tree where each node has at most 2 children:
LEFT child and RIGHT child.

         1           ← root (level 0)
        / \
       2   3         ← children of root (level 1)
      / \   \
     4   5   6       ← leaves (level 2)

TREE VOCABULARY (memorize these — interviewers use them constantly):
    NODE       — one element holding a value + child pointers
    ROOT       — the topmost node (the only node with no parent)
    LEAF       — a node with no children
    HEIGHT     — number of edges on the longest path from root to a leaf
    DEPTH      — number of edges from the root down to a node
    LEVEL      — all nodes at the same depth (root is level 0)
    SUBTREE    — a node and all of its descendants
    ANCESTOR   — any node on the path from root to a given node
    DESCENDANT — any node reachable going downward from a given node

THREE SPECIAL BINARY TREES (worth knowing by name):
    FULL binary tree        — every node has 0 or 2 children (no single-child nodes)
    COMPLETE binary tree    — every level is full except possibly the last,
                              which is filled left to right
    PERFECT binary tree     — all leaves are at the same level and every
                              non-leaf has exactly 2 children
                              (a perfect tree of height h has 2^(h+1)-1 nodes)

    FULL:            COMPLETE:           PERFECT:
        1                1                   1
       / \              / \                 / \
      2   3            2   3               2   3
     /                / \                    / \
    4                4   5                  4   5
'''

# --- DEFINING A TREE NODE ---
class TreeNode:
    """A single node in a binary tree."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val        # The data
        self.left = left      # Left child (or None)
        self.right = right    # Right child (or None)


# --- BUILDING A TREE ---
#         1
#        / \
#       2   3
#      / \   \
#     4   5   6

leaf4 = TreeNode(4)
leaf5 = TreeNode(5)
leaf6 = TreeNode(6)
node2 = TreeNode(2, leaf4, leaf5)
node3 = TreeNode(3, None, leaf6)
root = TreeNode(1, node2, node3)


'''
TREE TRAVERSALS — HOW TO VISIT EVERY NODE
-----------------------------------------
Unlike an array (left to right), there are MULTIPLE ways to visit all nodes
in a tree. These are called TRAVERSALS. Memorize these four:

    PREORDER  (Node → Left → Right)   — "pre"  = Node first
    INORDER   (Left → Node → Right)   — "in"   = Node in middle
    POSTORDER (Left → Right → Node)   — "post" = Node last
    LEVEL ORDER (BFS, row by row)     — uses a queue

The word "pre/in/post" tells you WHEN the node itself is visited relative
to its left and right children. All three below run on the SAME tree:

         1
        / \
       2   3
      / \   \
     4   5   6

  PREORDER:  1 → 2 → 4 → 5 → 3 → 6     INORDER:   4 → 2 → 5 → 1 → 3 → 6
  POSTORDER: 4 → 5 → 2 → 6 → 3 → 1     LEVEL ORDER: 1 → 2 → 3 → 4 → 5 → 6

  Notice the LEAVES (4, 5, 6) always appear in left-to-right order —
  only the position of the INTERNAL nodes changes.

WHEN TO USE WHICH?
  - INORDER  : on a BST it yields sorted order; also for "kth smallest in BST"
  - PREORDER : good for copying/serializing a tree (root before children)
  - POSTORDER: good for deleting a tree (children before parent)
  - LEVEL ORDER : problems that care about rows (right-side view, zig-zag,
                  "cousins" problems)
'''

# --- INORDER TRAVERSAL (recursive) ---
def inorder(node, result=None):
    """Left → Node → Right (recursive)."""
    if result is None:
        result = []
    if node:
        inorder(node.left, result)    # Visit left subtree
        result.append(node.val)       # Visit current node
        inorder(node.right, result)   # Visit right subtree
    return result


# --- INORDER TRAVERSAL (iterative) ---
# Why a stack? DFS goes DEEP before going WIDE. A stack's LIFO behavior
# matches "go as deep as you can, then backtrack." We push all left
# children, then pop/process, then go right.
def inorder_iterative(root):
    """Left → Node → Right using an explicit stack."""
    result = []
    stack = []
    current = root

    while current is not None or stack:
        while current is not None:       # walk down the left spine
            stack.append(current)
            current = current.left
        current = stack.pop()            # bottom of the left spine
        result.append(current.val)
        current = current.right          # explore right subtree

    return result


# --- PREORDER TRAVERSAL (recursive) ---
def preorder(node, result=None):
    """Node → Left → Right (recursive)."""
    if result is None:
        result = []
    if node:
        result.append(node.val)       # Visit current node FIRST
        preorder(node.left, result)
        preorder(node.right, result)
    return result


# --- PREORDER TRAVERSAL (iterative) ---
# Preorder is the easiest to iterate: process node, then push RIGHT child
# before LEFT child so the LEFT child is popped first (stack = LIFO).
def preorder_iterative(root):
    """Node → Left → Right using an explicit stack."""
    if root is None:
        return []
    result = []
    stack = [root]

    while stack:
        node = stack.pop()
        result.append(node.val)
        # Push RIGHT first so LEFT is processed first (LIFO).
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)

    return result


# --- POSTORDER TRAVERSAL (recursive) ---
def postorder(node, result=None):
    """Left → Right → Node (recursive)."""
    if result is None:
        result = []
    if node:
        postorder(node.left, result)
        postorder(node.right, result)
        result.append(node.val)       # Visit current node LAST
    return result


# --- POSTORDER TRAVERSAL (iterative) ---
# Trick: postorder (L-R-N) is the reverse of a modified preorder (N-R-L).
# So do "Node, Right, Left" preorder, then reverse the result.
def postorder_iterative(root):
    """Left → Right → Node using an explicit stack."""
    if root is None:
        return []
    result = []
    stack = [root]

    while stack:
        node = stack.pop()
        result.append(node.val)
        # Push LEFT first so RIGHT is processed first → gives us N-R-L.
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)

    result.reverse()  # reverse N-R-L → L-R-N
    return result


print("--- Tree Traversals (recursive) ---")
print("Inorder:  ", inorder(root))    # [4, 2, 5, 1, 3, 6]
print("Preorder: ", preorder(root))   # [1, 2, 4, 5, 3, 6]
print("Postorder:", postorder(root))  # [4, 5, 2, 6, 3, 1]

print("\n--- Tree Traversals (iterative) ---")
print("Inorder:  ", inorder_iterative(root))    # [4, 2, 5, 1, 3, 6]
print("Preorder: ", preorder_iterative(root))   # [1, 2, 4, 5, 3, 6]
print("Postorder:", postorder_iterative(root))  # [4, 5, 2, 6, 3, 1]


'''
WHY DOES BFS USE A QUEUE AND DFS USE A STACK?
---------------------------------------------
This is one of the most important intuitions in tree/graph algorithms.

  BFS (Breadth-First Search) explores level by level (row by row).
  You want to visit a node's children AFTER all nodes on the current level.
  → Use a QUEUE (FIFO — first in, first out). Nodes are added at the back
    and removed from the front, so they're processed in insertion order.

  DFS (Depth-First Search) goes as deep as possible before backtracking.
  You want to dive into a child immediately, before visiting siblings.
  → Use a STACK (LIFO — last in, first out). The most recently added
    node is processed next, which is exactly the "dive deeper" behavior.

  RECURSION IS A STACK. Every recursive call is pushed onto the call stack.
  That's why the recursive DFS implementations above "just work" — the
  call stack gives you LIFO behavior for free.

  Rule of thumb:
    - Need level-by-level info? BFS + queue.   (e.g. level order, shortest
      path in an unweighted tree/graph)
    - Need depth info or want to explore branches fully? DFS + stack/recursion.
      (e.g. max depth, path sums, "does a path exist")
'''

# --- LEVEL ORDER (BFS) ---
from collections import deque

def level_order(root):
    """Visit nodes level by level using a queue."""
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        node = queue.popleft()    # FIFO — oldest node first
        result.append(node.val)

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return result


# --- LEVEL ORDER (grouped by level) ---
# A tiny variation that returns a list of lists: [[1], [2, 3], [4, 5, 6]].
# This is the backbone of MANY problems: right side view, zigzag, average
# of levels, etc.
def level_order_grouped(root):
    """Return nodes grouped by level: [[level0], [level1], ...]."""
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)        # Number of nodes at this level
        level = []
        for _ in range(level_size):    # Process exactly this level
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)

    return result

print("\n--- Level Order (BFS) ---")
print("Level Order:           ", level_order(root))           # [1, 2, 3, 4, 5, 6]
print("Level Order (grouped): ", level_order_grouped(root))   # [[1], [2, 3], [4, 5, 6]]


'''
THE #1 TREE PATTERN: RECURSION (DFS)
------------------------------------
Almost every tree problem is solved with RECURSION.

The mental model for tree recursion:
    1. BASE CASE: What happens at a leaf (None node)? Usually return 0 or True.
    2. RECURSIVE CASE: Ask the LEFT subtree for an answer,
       ask the RIGHT subtree for an answer, then COMBINE them.

Example: Find the MAXIMUM DEPTH (height) of a tree.

    "What is the depth of this tree?"

    max_depth(root) = 1 + max(max_depth(left), max_depth(right))

    If root is None → depth is 0 (base case)
    Otherwise → 1 (for current node) + the deeper of left or right subtree.

TRACING max_depth on our tree:

         1
        / \
       2   3
      / \   \
     4   5   6

  max_depth(1)
   ├─ max_depth(2): max(1, 1) + 1 = 2      [from leaves 4, 5]
   ├─ max_depth(3): max(0, 1) + 1 = 2      [left None, right leaf 6]
   └─ return 1 + max(2, 2) = 3   ← final answer
'''

def max_depth(node):
    """Find the height of a binary tree (recursive)."""
    if node is None:
        return 0                          # Base case: empty tree has depth 0

    left_depth = max_depth(node.left)     # Ask left subtree for its depth
    right_depth = max_depth(node.right)   # Ask right subtree for its depth

    return 1 + max(left_depth, right_depth)  # Current node + deeper subtree


# --- MAX DEPTH (iterative, BFS) ---
# The number of BFS levels IS the depth. We count how many times we process
# a full level.
def max_depth_iterative(root):
    """Find the height of a binary tree using BFS (level counting)."""
    if root is None:
        return 0
    queue = deque([root])
    depth = 0
    while queue:
        depth += 1
        for _ in range(len(queue)):       # Process one whole level
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return depth


print("\n--- Max Depth ---")
print(f"Tree depth (recursive):  {max_depth(root)}")         # 3
print(f"Tree depth (iterative):  {max_depth_iterative(root)}")  # 3


# ====================================================================
# SOLVED PROBLEM: INVERT A BINARY TREE (LeetCode #226)
# ====================================================================
# "Invert a binary tree" is the famous "Google home-screen interview"
# problem that went viral. Conceptually it's simple: swap every node's
# left and right children.
#
#         4                   4
#        / \                 / \
#       2   7      →        7   2
#      / \ / \             / \ / \
#     1  3 6  9           9  6 3  1
#
# Recursive insight: to invert a tree, invert its left subtree, invert its
# right subtree, then swap them. That's it — a one-liner.

def invert_tree(node):
    """Invert a binary tree (mirror image). Recursive."""
    if node is None:
        return None
    # Swap happens here — note the parallel assignment.
    node.left, node.right = node.right, node.left
    invert_tree(node.left)
    invert_tree(node.right)
    return node


def invert_tree_iterative(root):
    """Invert a binary tree using BFS + a queue (swap at each node)."""
    if root is None:
        return None
    queue = deque([root])
    while queue:
        node = queue.popleft()
        node.left, node.right = node.right, node.left   # swap
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return root

# Build a sample tree to invert:
#         4
#        / \
#       2   7
#      / \ / \
#     1  3 6  9
inv_root = TreeNode(4,
    TreeNode(2, TreeNode(1), TreeNode(3)),
    TreeNode(7, TreeNode(6), TreeNode(9)))
print("\n--- Invert Binary Tree ---")
print("Before invert (BFS): ", level_order(inv_root))           # [4,2,7,1,3,6,9]
invert_tree(inv_root)
print("After invert  (BFS): ", level_order(inv_root))           # [4,7,2,9,6,3,1]


# ====================================================================
# SOLVED PROBLEM: SAME TREE (LeetCode #100)
# ====================================================================
# Are two binary trees structurally identical AND do corresponding nodes
# have the same values?
#
# Recursion: two trees are the same if their roots are equal, their left
# subtrees are the same, and their right subtrees are the same.

def is_same_tree(p, q):
    """Check if two trees are identical (recursive)."""
    # Base case 1: both empty → same.
    if p is None and q is None:
        return True
    # Base case 2: only one empty → different.
    if p is None or q is None:
        return False
    # Base case 3: values differ → different.
    if p.val != q.val:
        return False
    # Recursive case: both subtrees must match.
    return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)


def is_same_tree_iterative(p, q):
    """Check if two trees are identical using BFS (pair-by-pair)."""
    queue = deque([(p, q)])
    while queue:
        n1, n2 = queue.popleft()
        if n1 is None and n2 is None:
            continue
        if n1 is None or n2 is None or n1.val != n2.val:
            return False
        queue.append((n1.left, n2.left))
        queue.append((n1.right, n2.right))
    return True

# Two identical trees:
tree_a = TreeNode(1, TreeNode(2), TreeNode(3))
tree_b = TreeNode(1, TreeNode(2), TreeNode(3))
# A different tree:
tree_c = TreeNode(1, TreeNode(2), None)
print("\n--- Same Tree ---")
print(is_same_tree(tree_a, tree_b))      # True
print(is_same_tree(tree_a, tree_c))      # False
print(is_same_tree_iterative(tree_a, tree_b))  # True


'''
COMMON MISTAKES WITH TREE RECURSION
-----------------------------------
1. WRONG BASE CASE. Beginners sometimes write `if not node.left and not node.right:`
   as the base case (handling leaves directly). This WORKS but is fragile —
   it leaves you unable to handle None gracefully when trees are unbalanced.
   ✅ Best practice: base case is `if node is None: return ...`

2. FORGETTING TO CHECK FOR None BEFORE ACCESSING .left / .right.
   `if node.left.val == ...` crashes with AttributeError when node.left is None.
   ✅ Always check `if node.left:` (or handle None in the recursive call).

3. CONFUSING DEPTH AND HEIGHT.
   - DEPTH of a node  = distance (edges) from the ROOT down to that node.
   - HEIGHT of a node = distance (edges) from that node down to its deepest leaf.
   - HEIGHT of a tree = height of the root = max depth of any node.

4. MUTABLE DEFAULT ARGUMENTS. `def f(node, result=[]):` shares ONE list across
   all calls. ✅ Use `result=None` and create the list inside (as we do above).

5. SWAPPING LEFT/RIGHT WITHOUT TEMP VARIABLE.
   In languages without parallel assignment you need a temp var.
   In Python: `node.left, node.right = node.right, node.left` is safe.
'''


'''
PART 2: BINARY SEARCH TREES (BST)
==================================

WHAT IS A BST?
--------------
A Binary Search Tree is a binary tree with ONE SPECIAL RULE:

    For every node:
    - ALL values in the LEFT subtree are SMALLER than the node
    - ALL values in the RIGHT subtree are LARGER than the node

                8
               / \
              3   10
             / \    \
            1   6    14
               / \   /
              4   7 13

    Check: 8's left subtree {1,3,4,6,7} — all < 8 ✓
           8's right subtree {10,13,14} — all > 8 ✓
           3's left subtree {1} — all < 3 ✓
           3's right subtree {4,6,7} — all > 3 ✓

WHY IS THIS AMAZING?
    Searching for a value is O(log n) — like binary search on a tree!
    At each node, you know whether to go LEFT (smaller) or RIGHT (larger),
    eliminating half the tree at each step.

BST vs SORTED ARRAY:
    Sorted array: O(log n) search, O(n) insert/delete (shifting elements).
    BST:          O(log n) search AND O(log n) insert/delete.
    Tradeoff: BST uses more memory (pointers) and has no O(1) random access.

WORST CASE — DEGENERATE / "SPAGHETTI" BST:
    If you insert already-sorted data, the BST becomes a linked list and
    search/insert degrade to O(n):
        1 → 2 → 3 → 4
    Self-balancing BSTs (AVL, Red-Black) fix this by rotating to stay balanced.
'''

# --- BST SEARCH ---
def bst_search(node, target):
    """Find a value in a BST. O(log n) average."""
    if node is None:
        return False

    if target == node.val:
        return True                    # Found it
    elif target < node.val:
        return bst_search(node.left, target)   # Go left (smaller values)
    else:
        return bst_search(node.right, target)  # Go right (larger values)


# --- BST SEARCH (iterative) ---
# Iterative is nice here: no recursion overhead, O(1) extra space.
def bst_search_iterative(root, target):
    """Find a value in a BST iteratively."""
    node = root
    while node is not None:
        if target == node.val:
            return True
        elif target < node.val:
            node = node.left
        else:
            node = node.right
    return False

# Build a BST
#          8
#         / \
#        3   10
#       / \    \
#      1   6    14
#         / \   /
#        4   7 13
bst = TreeNode(8,
    TreeNode(3,
        TreeNode(1),
        TreeNode(6, TreeNode(4), TreeNode(7))
    ),
    TreeNode(10, None, TreeNode(14, TreeNode(13)))
)

print("\n--- BST Search ---")
print(bst_search(bst, 7))              # True
print(bst_search(bst, 5))              # False
print(bst_search_iterative(bst, 13))   # True
print(bst_search_iterative(bst, 99))   # False


# --- BST INSERT ---
def bst_insert(node, val):
    """Insert a value into a BST (recursive)."""
    if node is None:
        return TreeNode(val)

    if val < node.val:
        node.left = bst_insert(node.left, val)    # Go left
    elif val > node.val:
        node.right = bst_insert(node.right, val)  # Go right
    # If val == node.val, do nothing (no duplicates)

    return node


# --- BST INSERT (iterative) ---
def bst_insert_iterative(root, val):
    """Insert a value into a BST iteratively."""
    if root is None:
        return TreeNode(val)
    node = root
    while True:
        if val < node.val:
            if node.left is None:
                node.left = TreeNode(val)
                break
            node = node.left
        elif val > node.val:
            if node.right is None:
                node.right = TreeNode(val)
                break
            node = node.right
        else:
            break  # duplicate, ignore
    return root

print("\n--- BST Insert ---")
bst_insert(bst, 5)
print(bst_search(bst, 5))              # True now
print(bst_search_iterative(bst, 5))    # True

# --- INORDER OF BST = SORTED ARRAY ---
# Inorder traversal of a BST ALWAYS gives values in sorted order.
# This is the #1 useful property of BSTs for interviews.
print("\nInorder of BST (should be sorted):", inorder(bst))


'''
VALIDATE A BST (Common interview question):
    "Is this binary tree a valid BST?"

    The trick: pass down a VALID RANGE (min, max) for each node.
    As you descend, the range NARROWS:
         going LEFT  → new max = node.val   (everything must be smaller)
         going RIGHT → new min = node.val   (everything must be larger)

    Trace on this INVALID tree:

            8
           / \
          3   10
             /  \
            6   14     ← 6 is in 8's right subtree but 6 < 8 → INVALID

    At node 10: range is (8, +inf). OK.
    Going left to 6: range becomes (8, 10). 6 < 8 → FAIL. ✅ caught.

COMMON MISTAKE — only comparing a node to its DIRECT parent:
    Many people check only `node.left.val < node.val < node.right.val`.
    That passes the invalid tree above (6 < 10 locally) — but it's NOT a
    valid BST because 6 is in 8's right subtree. You MUST track the full
    (min, max) range inherited from all ancestors.
'''

def is_valid_bst(node, min_val=float('-inf'), max_val=float('inf')):
    """Recursive: check BST validity using an inherited (min, max) range."""
    if node is None:
        return True

    # Current node must be within the valid range
    if node.val <= min_val or node.val >= max_val:
        return False

    # Left subtree: all values must be < node.val (update max)
    # Right subtree: all values must be > node.val (update min)
    return (is_valid_bst(node.left, min_val, node.val) and
            is_valid_bst(node.right, node.val, max_val))


# --- VALIDATE BST (iterative, with explicit stack of (node, min, max)) ---
def is_valid_bst_iterative(root):
    """Iterative: check BST validity using an explicit stack."""
    if root is None:
        return True
    stack = [(root, float('-inf'), float('inf'))]
    while stack:
        node, low, high = stack.pop()
        if node.val <= low or node.val >= high:
            return False
        if node.left:
            stack.append((node.left, low, node.val))
        if node.right:
            stack.append((node.right, node.val, high))
    return True

print("\n--- Validate BST ---")
print(is_valid_bst(bst))               # True
print(is_valid_bst_iterative(bst))     # True

# An invalid BST: 6 is in 8's right subtree.
bad_bst = TreeNode(8,
    TreeNode(3),
    TreeNode(10, TreeNode(6), TreeNode(14)))
print(is_valid_bst(bad_bst))           # False
print(is_valid_bst_iterative(bad_bst)) # False


# ====================================================================
# SOLVED PROBLEM: LOWEST COMMON ANCESTOR (LeetCode #236)
# ====================================================================
# Given two nodes p and q in a binary tree, find their LOWEST COMMON
# ANCESTOR (LCA) — the deepest node that has both p and q as descendants.
#
#          3
#        /   \
#       5     1
#      / \   / \
#     6   2 0   8
#        / \
#       7   4
#
#   LCA(5, 1)  = 3   (the root — 5 is in left subtree, 1 in right)
#   LCA(5, 4)  = 5   (4 is a descendant of 5, so 5 itself is the LCA)
#   LCA(6, 4)  = 5
#
# Recursive insight: ask each subtree "did you find p or q?" If p and q
# are found on DIFFERENT sides of a node, that node is the LCA. If a node
# IS p or q, it's a candidate (the other may be below it).

def lowest_common_ancestor(root, p, q):
    """Return the LCA of nodes p and q in a binary tree."""
    # Base case: fell off the tree, or found one of the targets.
    if root is None or root == p or root == q:
        return root

    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    # If both sides returned a node, root is the LCA (p and q split here).
    if left and right:
        return root
    # Otherwise, both targets are on the same side — bubble that up.
    return left if left else right

# Build the tree above.
n6  = TreeNode(6)
n7  = TreeNode(7)
n4  = TreeNode(4)
n2  = TreeNode(2, n7, n4)
n5  = TreeNode(5, n6, n2)
n0  = TreeNode(0)
n8  = TreeNode(8)
n1  = TreeNode(1, n0, n8)
lca_root = TreeNode(3, n5, n1)

print("\n--- Lowest Common Ancestor ---")
print(f"LCA(5, 1).val = {lowest_common_ancestor(lca_root, n5, n1).val}")  # 3
print(f"LCA(5, 4).val = {lowest_common_ancestor(lca_root, n5, n4).val}")  # 5
print(f"LCA(6, 4).val = {lowest_common_ancestor(lca_root, n6, n4).val}")  # 5


'''
PART 3: HEAPS / PRIORITY QUEUES
================================

WHAT IS A HEAP?
---------------
Real-world analogy: A hospital EMERGENCY ROOM (ER triage).

    Patients are NOT treated in arrival order.
    The MOST CRITICAL patient is treated FIRST, regardless of arrival time.
    Treatment order is by SEVERITY, not by check-in time.

A heap is a tree-based structure that always gives you the MINIMUM
(or MAXIMUM) element in O(1) time.

There are two types:
    MIN-HEAP: The smallest element is always at the top (root).
    MAX-HEAP: The largest element is always at the top (root).

              MIN-HEAP                    MAX-HEAP
                1                           10
               / \                         /  \
              3   4                       8    9
             / \                         / \  / \
            5   7                       3  4 5  2

IMPORTANT: A heap is NOT fully sorted! The only guarantee is:
    - The root is the min (or max)
    - Every parent is smaller (min-heap) or larger (max-heap) than its children

    This is the HEAP PROPERTY. It is weaker than "fully sorted" but strong
    enough to find the min/max in O(1) and add/remove in O(log n).

HOW A HEAP IS ACTUALLY STORED — THE ARRAY TRICK:
    A complete binary heap is stored in a plain ARRAY, not with pointers.
    For a node at index i (0-based):
        parent   = (i - 1) // 2
        left     = 2*i + 1
        right    = 2*i + 2

    Tree:           Array: [1, 3, 4, 5, 7]
       1  (idx 0)
      / \
     3   4           index:  0  1  2  3  4
    / \              value: [1, 3, 4, 5, 7]
   5   7

    Why an array? Because a COMPLETE tree has no "gaps," so the positions
    are predictable. No pointers = cache-friendly + compact.

HEAP OPERATIONS AND COMPLEXITY:
    push(x)   — add an element       → O(log n)  ("sift up")
    pop()     — remove root (min/max) → O(log n)  ("sift down")
    peek()    — look at root          → O(1)
    heapify   — build heap from array → O(n)      (amortized, faster than n pushes)

IN PYTHON:
    Python's heapq module gives us a MIN-HEAP.
    For a MAX-HEAP, negate all values (push -x, pop -x).

    heapq.heappush(heap, x)   # add
    heapq.heappop(heap)       # remove + return smallest
    heap[0]                   # peek (smallest), without removing
    heapq.heapify(list)       # turn a list into a heap in-place, O(n)
    heapq.nsmallest(k, iter)  # k smallest   — uses a max-heap internally
    heapq.nlargest(k, iter)   # k largest    — uses a min-heap internally
'''

import heapq

# --- MIN-HEAP ---
print("\n--- Min-Heap ---")
min_heap = []
heapq.heappush(min_heap, 5)
heapq.heappush(min_heap, 1)
heapq.heappush(min_heap, 3)
heapq.heappush(min_heap, 7)

print("Heap internal array:", min_heap)  # [1, 5, 3, 7] (root is smallest)
print("Peek (smallest):", min_heap[0])   # 1

# Pop always returns the SMALLEST
print("Pop:", heapq.heappop(min_heap))   # 1
print("Pop:", heapq.heappop(min_heap))   # 3
print("Pop:", heapq.heappop(min_heap))   # 5

# --- MAX-HEAP (by negating values) ---
print("\n--- Max-Heap (via negation) ---")
max_heap = []
for val in [5, 1, 3, 7]:
    heapq.heappush(max_heap, -val)  # Store negative

# Pop returns the MOST NEGATIVE = originally the LARGEST
print("Pop largest:", -heapq.heappop(max_heap))   # 7
print("Pop next:   ", -heapq.heappop(max_heap))   # 5

# --- HEAPIFY (build a heap in O(n)) ---
print("\n--- Heapify ---")
data = [9, 4, 2, 7, 1, 5]
heapq.heapify(data)
print("After heapify:", data)            # [1, 4, 2, 7, 9, 5]
print("Pop:", heapq.heappop(data))       # 1


# --- THE #1 HEAP PATTERN: "TOP K" PROBLEMS ---
# "Find the K largest/smallest/most frequent elements"
#
# TRICK: Use a heap of size K.
# For "K largest": maintain a MIN-HEAP of size K.
#   - Push elements one by one.
#   - If heap size > K, pop the smallest.
#   - At the end, the heap contains the K largest elements.

def top_k_largest(nums, k):
    """Find the K largest elements in an array."""
    min_heap = []
    for num in nums:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)  # Remove smallest, keep top K
    return sorted(min_heap, reverse=True)

print("\n--- Top K Largest ---")
print(top_k_largest([3, 1, 5, 7, 2, 8, 6, 4], 3))  # [8, 7, 6]

'''
WHY USE A HEAP FOR TOP-K INSTEAD OF SORTING?
    Sorting: O(n log n) — sort everything
    Heap:    O(n log k) — only maintain k elements
    When k << n (e.g., top 3 out of 1,000,000), the heap is much faster.

    Even simpler: heapq.nlargest(k, nums) does exactly this for you.
'''


# ====================================================================
# SOLVED PROBLEM: KTH LARGEST ELEMENT IN A STREAM (LeetCode #703)
# ====================================================================
# Design a class that, given an initial list of numbers and an integer k,
# can repeatedly .add(num) and return the kth largest element seen so far.
#
# Key insight: keep a MIN-HEAP of size k. The smallest element in that heap
# IS the kth largest overall. Every .add either pushes (and possibly pops)
# or does nothing meaningful.

class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = nums
        heapq.heapify(self.heap)          # O(n) build
        # Shrink the heap down to size k by popping extras.
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]               # smallest in size-k heap = kth largest

print("\n--- Kth Largest in a Stream ---")
kth = KthLargest(3, [4, 5, 8, 2])
print(kth.add(3))    # 4   (heap [2,3,4], kth largest = 4)
print(kth.add(5))    # 5   (heap [3,4,5,5]→[4,5,5], kth largest = 5)
print(kth.add(10))   # 5   (heap [4,5,5,10]→[5,5,10], kth largest = 5)
print(kth.add(9))    # 8   (heap [5,5,10,9]→[5,8,10,9]... kth largest = 8)


# ====================================================================
# SOLVED PROBLEM: LAST STONE WEIGHT (LeetCode #1046)
# ====================================================================
# We have stones with positive weights. Each turn, smash the two HEAVIEST:
#   - if equal weights, both are destroyed
#   - if unequal, the lighter is destroyed and the heavier becomes the diff
# Repeat until 0 or 1 stone remains. Return its weight (or 0).
#
# This is a textbook MAX-HEAP use case: always pull the two largest.
# Python has no max-heap, so we negate weights.

def last_stone_weight(stones):
    """Simulate smashing the two heaviest stones each turn."""
    # Max-heap via negation.
    heap = [-s for s in stones]
    heapq.heapify(heap)

    while len(heap) > 1:
        heaviest = -heapq.heappop(heap)      # largest
        second   = -heapq.heappop(heap)      # 2nd largest
        if heaviest != second:
            heapq.heappush(heap, -(heaviest - second))

    return -heap[0] if heap else 0

print("\n--- Last Stone Weight ---")
print(last_stone_weight([2, 7, 4, 1, 8, 1]))  # 1
# Trace: smash 8,7 → 1; stones [4,2,1,1,1]; smash 4,2 → 2; stones [2,1,1,1];
#        smash 2,1 → 1; stones [1,1,1]; smash 1,1 → 0; stones [1] → return 1.
print(last_stone_weight([1]))                 # 1


# ====================================================================
# SOLVED PROBLEM: MERGE K SORTED LISTS WITH A HEAP (LeetCode #23)
# ====================================================================
# You have k sorted linked lists (here represented as plain sorted lists).
# Merge them into one sorted list.
#
# Brute force: concatenate everything, sort → O(N log N) where N = total elems.
# Heap approach: put the SMALLEST current element from each list into a heap.
#   Pop the global smallest, advance that list, push its next element.
#   This is O(N log k) — much better when k is small relative to N.
#
# We store tuples (value, list_index, element_index) so heapq can break ties
# deterministically (it can't compare lists).

def merge_sorted_lists(lists):
    """Merge k sorted lists into one sorted list using a min-heap."""
    heap = []
    for i, lst in enumerate(lists):
        if lst:                                  # non-empty list
            heapq.heappush(heap, (lst[0], i, 0)) # (value, list_idx, elem_idx)

    result = []
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        # Advance in the list we just drew from.
        if elem_idx + 1 < len(lists[list_idx]):
            next_val = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, elem_idx + 1))

    return result

print("\n--- Merge K Sorted Lists (heap) ---")
print(merge_sorted_lists([[1, 4, 5], [1, 3, 4], [2, 6]]))  # [1,1,2,3,4,4,5,6]


'''
COMMON MISTAKES WITH HEAPS
--------------------------
1. ASSUMING THE INTERNAL ARRAY IS SORTED.
   `heap = [3,1,2]; heapq.heapify(heap)` → [1, 3, 2] (NOT [1,2,3]).
   Only the ROOT is guaranteed to be the min. To get sorted output you must
   pop repeatedly. ✅ Use sorted(heap) only if you actually need full order.

2. FORGETTING TO NEGATE FOR A MAX-HEAP.
   Python's heapq is min-only. For "K largest" with a min-heap of size K
   that's fine (you WANT the smallest of the K to bubble out). But for
   "K smallest" you need a MAX-HEAP of size K — negate everything.

3. COMPARING UNCOMPARABLE OBJECTS IN THE HEAP.
   If you push tuples (obj, ...) where obj isn't orderable, heapq will crash
   when values tie. ✅ Always include a tiebreaker (e.g., an index) before
   the object, as we do in merge_sorted_lists.

4. USING A HEAP WHEN A SORT WOULD DO.
   If k ≈ n, sorting (O(n log n)) is simpler and often faster in practice
   than heap bookkeeping. The heap shines when k << n.
'''


'''
PART 4: TRIES (PREFIX TREES)
=============================

WHAT IS A TRIE?
---------------
Real-world analogy: AUTOCOMPLETE on your phone.

    When you type "app", your phone suggests "apple", "apply", "application"...
    A trie is the data structure that makes this instant.

A trie is a TREE where each node represents ONE LETTER.
Words are stored as paths from the root down:

    Root → a → p → p* → l → e*    ("app", "apple" — * marks word endings)

SHARING PREFIXES — the key efficiency win:
    Insert "app", "apple", "apply", "application" and they SHARE the
    "app" prefix. You store "app" once, not four times.

    Root → a → p → p*           (* = end of "app")
                     ├─ l → e*   ("apple")
                     ├─ l → y*   ("apply")
                     └─ l → i → c → a → t → i → o → n*  ("application")

Each node has:
    - A dictionary of children (next letter → child node)
    - A boolean flag: is this the end of a word?
'''

# --- DEFINING A TRIE NODE ---
class TrieNode:
    def __init__(self):
        self.children = {}    # Maps single char → TrieNode
        self.is_end = False   # True if this node completes a word


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """Add a word to the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()  # Create new letter node
            node = node.children[char]             # Move to next letter
        node.is_end = True  # Mark the last letter as end of word

    def search(self, word):
        """Check if a COMPLETE word exists in the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                return False  # Letter not found → word doesn't exist
            node = node.children[char]
        return node.is_end  # Must be end of a word (not just a prefix)

    def starts_with(self, prefix):
        """Check if any word STARTS WITH this prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True  # Prefix exists (word may or may not end here)

    def _find_node(self, prefix):
        """Walk to the node representing `prefix`, or None if absent."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def autocomplete(self, prefix):
        """Return all words in the trie that start with `prefix`.

        This is the classic AUTOCOMPLETE use case: type a prefix, get every
        completion. We walk to the prefix node, then DFS to collect all
        words that descend from it.
        """
        start = self._find_node(prefix)
        if start is None:
            return []  # prefix itself isn't in the trie

        results = []

        def dfs(node, path):
            if node.is_end:
                results.append(prefix + path)
            for char, child in node.children.items():
                dfs(child, path + char)

        dfs(start, "")
        return results


# --- DEMO ---
trie = Trie()
trie.insert("apple")
trie.insert("app")
trie.insert("application")
trie.insert("apply")
trie.insert("banana")

print("\n--- Trie ---")
print(trie.search("apple"))       # True  (exact word exists)
print(trie.search("app"))         # True  (exact word exists)
print(trie.search("appl"))        # False (prefix but not a complete word)
print(trie.starts_with("appl"))   # True  (prefix exists → "apple" starts with "appl")
print(trie.starts_with("ban"))    # True  ("banana" starts with "ban")
print(trie.search("ball"))        # False (not in trie at all)

print("\n--- Autocomplete ---")
print("Type 'app' →", sorted(trie.autocomplete("app")))
# ['app', 'apple', 'application', 'apply']
print("Type 'ban' →", sorted(trie.autocomplete("ban")))
# ['banana']
print("Type 'xyz' →", trie.autocomplete("xyz"))
# [] (no words start with xyz)


'''
WORD SEARCH II (LeetCode #212) — the classic trie interview problem
-------------------------------------------------------------------
Given a 2D board of letters and a list of words, find every word that can
be formed by a path on the board (moving to adjacent cells, no reuse).

BRUTE FORCE: for each word, run DFS on the board from every cell.
If there are W words and the board has N cells with branching ~3^L
(L = word length), that's O(W·N·3^L).

BETTER: insert ALL words into a TRIE. Run ONE DFS from every cell, walking
the trie as you go. Prune immediately when the current path isn't a prefix
of ANY word — this collapses W independent searches into one shared search.

    def find_words(board, words):
        trie = Trie()
        for w in words:
            trie.insert(w)
        root = trie.root
        found = set()
        rows, cols = len(board), len(board[0])

        def dfs(r, c, node, path):
            char = board[r][c]
            if char not in node.children:
                return                      # prune: not a prefix of any word
            node = node.children[char]
            if node.is_end:
                found.add(path + char)
            board[r][c] = "#"               # mark visited
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                    dfs(nr, nc, node, path + char)
            board[r][c] = char              # restore (backtrack)

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, root, "")
        return list(found)

Key tricks:
  - Temporarily overwrite a cell with "#" to mark it visited, then RESTORE
    it after the recursive calls (backtracking).
  - Collect into a set to dedupe. Prune the instant the path leaves the trie.
'''


'''
WHEN TO USE A TRIE?
    1. Autocomplete / prefix search
    2. Spell checker
    3. IP routing tables (longest-prefix match)
    4. Word Search II (LeetCode #212) — find words on a grid
    5. T9 / predictive text on old phone keypads

COMPLEXITY & TRIE vs HASH SET:
    - Insert/search: O(m) where m = word length — INDEPENDENT of how many
      words are stored. That's the magic.
    - A hash set is also O(m) for an EXACT-word lookup, but a trie also gives
      you prefix queries in O(m + output), which a hash set cannot (it would
      have to scan every stored word — O(total_chars)).

COMMON MISTAKES WITH TRIES
--------------------------
1. FORGETTING is_end. A trie path "appl" exists because "apple" was inserted,
   but search("appl") must return False unless "appl" itself was inserted.
   ✅ Always check node.is_end at the end of search().

2. NOT DISTINGUISHING search vs starts_with.
   search("app") → True only if "app" was inserted as a word.
   starts_with("app") → True if ANY word starts with "app".

3. USING A LIST INSTEAD OF A DICT FOR children (when chars are unconstrained).
   For lowercase a–z only, a fixed 26-element list is faster. For arbitrary
   characters (uppercase, digits, unicode), a dict is correct.

4. NOT BACKTRACKING IN WORD SEARCH II. If you forget to restore board[r][c]
   after the recursive DFS, every subsequent search starts from a corrupted
   board. ✅ Always pair "mark visited" with "restore on the way out."
'''

# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 4 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Binary Tree: each node has left + right child.
   - Traversals: Inorder (L-N-R), Preorder (N-L-R), Postorder (L-R-N), BFS
   - BOTH recursive and iterative versions exist for every traversal.
   - BFS uses a QUEUE (FIFO, level by level); DFS uses a STACK/recursion
     (LIFO, dive deep then backtrack).
   - Most problems: recursion (base case + combine left/right answers).
2. BST: left < node < right. Search/insert in O(log n).
   - Inorder traversal = sorted array.
   - Validate by passing an inherited (min, max) range — NOT just parent.
3. Heap: always gives min/max in O(1). Push/pop in O(log n).
   - Use for Top K problems. Python heapq = min-heap.
   - Max-heap via negation. Stored internally as an array.
4. Trie: prefix tree. Each node = one letter.
   - O(m) insert/search (m = word length).
   - Use for autocomplete, prefix matching, Word Search II.
   - search() checks is_end; starts_with() does not.

Next: Chapter 5 — Graphs
""")
