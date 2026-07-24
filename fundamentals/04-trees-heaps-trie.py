'''
CHAPTER 4: TREES, BINARY SEARCH TREES, HEAPS & TRIES
=====================================================

"These four data structures are all based on the same idea: a HIERARCHY.
A tree is like a family tree. A BST is a sorted tree. A heap is a
priority tree. A trie is a word tree."

---

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

         1           ← root
        / \
       2   3         ← children of root
      / \   \
     4   5   6       ← leaves (no children)
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

1. INORDER (Left → Node → Right):
   Visit left child, then current node, then right child.
   For the tree above: 4, 2, 5, 1, 3, 6

2. PREORDER (Node → Left → Right):
   Visit current node first, then left, then right.
   For the tree above: 1, 2, 4, 5, 3, 6

3. POSTORDER (Left → Right → Node):
   Visit left, then right, then current node.
   For the tree above: 4, 5, 2, 6, 3, 1

4. LEVEL ORDER (BFS — top to bottom, left to right):
   Visit row by row using a queue.
   For the tree above: 1, 2, 3, 4, 5, 6

MEMORY HOOK:
    "Pre" = Node first    (N-L-R)
    "In" = Node in middle  (L-N-R)
    "Post" = Node last     (L-R-N)
'''

# --- INORDER TRAVERSAL ---
def inorder(node, result=None):
    """Left → Node → Right"""
    if result is None:
        result = []
    if node:
        inorder(node.left, result)    # Visit left subtree
        result.append(node.val)       # Visit current node
        inorder(node.right, result)   # Visit right subtree
    return result

# --- PREORDER TRAVERSAL ---
def preorder(node, result=None):
    """Node → Left → Right"""
    if result is None:
        result = []
    if node:
        result.append(node.val)       # Visit current node FIRST
        preorder(node.left, result)
        preorder(node.right, result)
    return result

# --- POSTORDER TRAVERSAL ---
def postorder(node, result=None):
    """Left → Right → Node"""
    if result is None:
        result = []
    if node:
        postorder(node.left, result)
        postorder(node.right, result)
        result.append(node.val)       # Visit current node LAST
    return result

print("--- Tree Traversals ---")
print("Inorder:  ", inorder(root))    # [4, 2, 5, 1, 3, 6]
print("Preorder: ", preorder(root))   # [1, 2, 4, 5, 3, 6]
print("Postorder:", postorder(root))  # [4, 5, 2, 6, 3, 1]


# --- LEVEL ORDER (BFS) ---
from collections import deque

def level_order(root):
    """Visit nodes level by level using a queue."""
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        node = queue.popleft()
        result.append(node.val)

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return result

print("Level Order:", level_order(root))  # [1, 2, 3, 4, 5, 6]


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
'''

def max_depth(node):
    """Find the height of a binary tree."""
    if node is None:
        return 0                          # Base case: empty tree has depth 0

    left_depth = max_depth(node.left)     # Ask left subtree for its depth
    right_depth = max_depth(node.right)   # Ask right subtree for its depth

    return 1 + max(left_depth, right_depth)  # Current node + deeper subtree

print("\n--- Max Depth ---")
print(f"Tree depth: {max_depth(root)}")  # 3


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
    At each node, you know whether to go LEFT (value is smaller) or RIGHT (larger).
    You eliminate half the tree at each step.
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
print(bst_search(bst, 7))   # True
print(bst_search(bst, 5))   # False


# --- BST INSERT ---
def bst_insert(node, val):
    """Insert a value into a BST."""
    if node is None:
        return TreeNode(val)

    if val < node.val:
        node.left = bst_insert(node.left, val)    # Go left
    elif val > node.val:
        node.right = bst_insert(node.right, val)  # Go right
    # If val == node.val, do nothing (no duplicates)

    return node

print("\n--- BST Insert ---")
bst_insert(bst, 5)
print(bst_search(bst, 5))   # True now

# --- INORDER OF BST = SORTED ARRAY ---
# Inorder traversal of a BST ALWAYS gives values in sorted order.
print("\nInorder of BST (should be sorted):", inorder(bst))


'''
VALIDATE A BST (Common interview question):
    "Is this binary tree a valid BST?"

    The trick: pass down a VALID RANGE (min, max) for each node.
    - Left child must be less than parent (max = parent's value)
    - Right child must be greater than parent (min = parent's value)
'''

def is_valid_bst(node, min_val=float('-inf'), max_val=float('inf')):
    if node is None:
        return True

    # Current node must be within the valid range
    if node.val <= min_val or node.val >= max_val:
        return False

    # Left subtree: all values must be < node.val (update max)
    # Right subtree: all values must be > node.val (update min)
    return (is_valid_bst(node.left, min_val, node.val) and
            is_valid_bst(node.right, node.val, max_val))

print("\n--- Validate BST ---")
print(is_valid_bst(bst))  # True


'''
PART 3: HEAPS / PRIORITY QUEUES
================================

WHAT IS A HEAP?
---------------
Real-world analogy: A hospital EMERGENCY ROOM.

    Patients are NOT treated in arrival order.
    The MOST CRITICAL patient is treated FIRST, regardless of when they arrived.

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

HEAP OPERATIONS:
    push(x)   — add an element       → O(log n)
    pop()     — remove root (min/max) → O(log n)
    peek()    — look at root          → O(1)
    heapify   — build heap from array → O(n)

IN PYTHON:
    Python's heapq module gives us a MIN-HEAP.
    For a MAX-HEAP, negate all values (push -x, pop -x).
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


PART 4: TRIES (PREFIX TREES)
=============================

WHAT IS A TRIE?
---------------
Real-world analogy: AUTOCOMPLETE on your phone.

    When you type "app", your phone suggests "apple", "apply", "application"...
    A trie is the data structure that makes this instant.

A trie is a TREE where each node represents ONE LETTER.
Words are stored as paths from the root down.

    Root
      ↓
      a
      ↓
      p
      ↓
      p          ← "app" ends here (is_end = True)
      ↓
      l
      ↓
      e          ← "apple" ends here (is_end = True)

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

# --- DEMO ---
trie = Trie()
trie.insert("apple")
trie.insert("app")
trie.insert("application")
trie.insert("banana")

print("\n--- Trie ---")
print(trie.search("apple"))       # True  (exact word exists)
print(trie.search("app"))         # True  (exact word exists)
print(trie.search("appl"))        # False (prefix but not a complete word)
print(trie.starts_with("appl"))   # True  (prefix exists → "apple" starts with "appl")
print(trie.starts_with("ban"))    # True  ("banana" starts with "ban")
print(trie.search("ball"))        # False (not in trie at all)


'''
WHEN TO USE A TRIE?
    1. Autocomplete / prefix search
    2. Spell checker
    3. IP routing tables
    4. Word Search II (LeetCode #212) — find words on a grid

COMPLEXITY:
    - Insert/search: O(m) where m = length of word
    - Does NOT depend on how many words are stored! That's the magic.
    - Compare: searching in a hash map is O(m) for hash computation,
      but a trie also gives you PREFIX search which hash maps cannot.

---

SUMMARY TABLE: ALL FOUR DATA STRUCTURES
=======================================

| Structure | What It Does              | Key Operation | Time  | When to Use                |
|-----------|---------------------------|---------------|-------|----------------------------|
| Tree      | Hierarchical data         | DFS traverse  | O(n)  | Any parent-child structure |
| BST       | Sorted tree               | Search        | O(log n)| Need sorted + fast search|
| Heap      | Always find min/max fast  | Push/Pop      | O(log n)| Top K, priority scheduling|
| Trie      | Prefix tree for strings   | Prefix search | O(m)  | Autocomplete, word search  |
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
   - Most problems: recursion (base case + combine left/right answers)
2. BST: left < node < right. Search/insert in O(log n).
   - Inorder traversal = sorted array.
3. Heap: always gives min/max in O(1). Push/pop in O(log n).
   - Use for Top K problems. Python heapq = min-heap.
4. Trie: prefix tree. Each node = one letter.
   - O(m) insert/search (m = word length).
   - Use for autocomplete, prefix matching.

Next: Chapter 5 — Graphs
""")
