'''
LEETCODE #138: Copy List with Random Pointer
DIFFICULTY: Medium
TOPIC: Linked List

=== PROBLEM STATEMENT ===
A linked list of length n is given such that each node contains an additional
random pointer, which could point to any node in the list, or null.

Construct a deep copy of the list. The deep copy should consist of exactly n
brand new nodes, each including the original value and the next and random
pointer of the corresponding node. None of the pointers in the new list
should point to nodes in the original list.

Return the head of the copied linked list.

=== INTUITION ===
The challenge is the random pointer: when we create a copy of a node, the
node its random pointer references may not exist yet. Two elegant solutions:

1. Hash Map approach: First pass creates all copy nodes and stores a mapping
   from original -> copy. Second pass wires up next and random pointers using
   the map.

2. In-place interleaving (O(1) space): Insert each copy node right after its
   original. Then random pointers are trivially: copy.random = orig.random.next.
   Finally, separate the two lists.

=== APPROACHES ===
Approach 1: Brute Force — Hash Map (Two Pass)
- Idea: Map original nodes to copies. Wire up pointers in a second pass.
- Time: O(n)
- Space: O(n) for the hash map.

Approach 2: Optimal — Interleaving (O(1) Space)
- Idea: Weave copies between originals, wire randoms, then split.
- Time: O(n)
- Space: O(1)

=== DRY RUN ===
List: A(random=C) -> B(random=A) -> C(random=None)
Shorthand: A->B->C, A.r=C, B.r=A, C.r=None

--- Interleaving Approach ---

Phase 1: Insert copies after each original.
  A -> A' -> B -> B' -> C -> C' -> None

Phase 2: Set random pointers.
  A'.random = A.random.next = C.next = C'  (if A.random != None)
  B'.random = B.random.next = A.next = A'
  C'.random = None (since C.random is None)

Phase 3: Separate (unweave) the lists.
  Original: A -> B -> C
  Copy:     A' -> B' -> C'

=== COMPLEXITY ANALYSIS ===
Time: O(n) — three passes.
Space: O(1) — no extra data structures (excluding recursion).

=== EDGE CASES ===
- Empty list
- Single node with random pointing to itself
- Single node with random = None
- Random pointers forming cycles
- All random pointers are None

=== INTERVIEW TIPS ===
- The hash map solution is easier to explain and less error-prone. Start with
  it, then mention the O(1) space interleaving trick as an optimization.
- For the interleaving approach, don't forget the third phase (separating the
  lists) — it's easy to overlook.
- Deep copy means new memory; verify no pointers reference original nodes.
- Follow-up: What if nodes had additional arbitrary pointers (beyond random)?
  (Same hash map approach scales; interleaving gets complex.)
'''

# === SOLUTION ===
from typing import Optional


class Node:
    def __init__(self, x: int, next: 'Node' = None, random: 'Node' = None):
        self.val = int(x)
        self.next = next
        self.random = random


def copyRandomList(head: Optional['Node']) -> Optional['Node']:
    """Deep copy using interleaving — O(1) extra space."""
    if not head:
        return None

    # --- Phase 1: Insert copy nodes after each original. ---
    curr = head
    while curr:
        copy = Node(curr.val)
        copy.next = curr.next
        curr.next = copy
        curr = copy.next

    # --- Phase 2: Set random pointers for copies. ---
    curr = head
    while curr:
        if curr.random:
            curr.next.random = curr.random.next
        curr = curr.next.next  # Skip the copy.

    # --- Phase 3: Separate the two lists. ---
    curr = head
    copy_head = head.next
    while curr:
        copy = curr.next
        curr.next = copy.next        # Restore original's next.
        copy.next = copy.next.next if copy.next else None
        curr = curr.next

    return copy_head


def copyRandomListHashMap(head: Optional['Node']) -> Optional['Node']:
    """Deep copy using a hash map — O(n) space, simpler logic."""
    if not head:
        return None

    # First pass: create all copy nodes.
    old_to_new = {}
    curr = head
    while curr:
        old_to_new[curr] = Node(curr.val)
        curr = curr.next

    # Second pass: wire up next and random pointers.
    curr = head
    while curr:
        if curr.next:
            old_to_new[curr].next = old_to_new[curr.next]
        if curr.random:
            old_to_new[curr].random = old_to_new[curr.random]
        curr = curr.next

    return old_to_new[head]


# === TEST CASES ===
if __name__ == "__main__":
    def build(vals):
        """vals = [(val, random_index_or_None), ...]"""
        if not vals:
            return None
        nodes = [Node(v[0]) for v in vals]
        for i, (v, r) in enumerate(vals):
            if i < len(vals) - 1:
                nodes[i].next = nodes[i + 1]
            if r is not None:
                nodes[i].random = nodes[r]
        return nodes[0]

    def serialize(head):
        """Returns list of (val, random_index_or_None)."""
        if not head:
            return []
        nodes = []
        curr = head
        while curr:
            nodes.append(curr)
            curr = curr.next
        index = {id(n): i for i, n in enumerate(nodes)}
        result = []
        curr = head
        while curr:
            ri = index.get(id(curr.random)) if curr.random else None
            result.append((curr.val, ri))
            curr = curr.next
        return result

    # Test 1: standard
    orig = build([(7, None), (13, 0), (11, 4), (10, 2), (1, 0)])
    copy = copyRandomList(orig)
    assert serialize(copy) == [(7, None), (13, 0), (11, 4), (10, 2), (1, 0)]
    # Test 2: empty
    assert copyRandomList(None) is None
    # Test 3: single node, random to self
    orig = build([(1, 0)])
    copy = copyRandomList(orig)
    assert serialize(copy) == [(1, 0)]
    # Test 4: single node, no random
    orig = build([(1, None)])
    copy = copyRandomList(orig)
    assert serialize(copy) == [(1, None)]
    # Test 5: hash map version
    orig = build([(7, None), (13, 0), (11, 4), (10, 2), (1, 0)])
    copy = copyRandomListHashMap(orig)
    assert serialize(copy) == [(7, None), (13, 0), (11, 4), (10, 2), (1, 0)]
    print("All tests passed!")
