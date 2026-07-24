'''
LEETCODE #25: Reverse Nodes in k-Group
DIFFICULTY: Hard
TOPIC: Linked List

=== PROBLEM STATEMENT ===
Given the head of a linked list, reverse the nodes of the list k at a time
and return the modified list.

k is a positive integer and is less than or equal to the length of the linked
list. If the number of nodes is not a multiple of k, the last remaining nodes
should stay as-is.

You may not alter the values in the list's nodes (only nodes themselves may
be changed).

=== INTUITION ===
This is a combination of two skills:
1. Counting k nodes ahead (to check if a full group exists).
2. Reversing a sublist of exactly k nodes.

For each group:
- Check if there are at least k nodes remaining. If not, stop.
- Reverse those k nodes.
- Connect the reversed group to the previous group and the next group.

The key pointers:
- `group_prev`: the node before the current group (starts as a dummy).
- `kth`: the k-th node in the current group (found by advancing k times).
- `group_next`: the node after the current group (kth.next).

After reversing, rewire: group_prev.next -> (reversed head), and the old
group head (now tail of reversed segment) -> group_next.

=== APPROACHES ===
Approach 1: Brute Force — Array Conversion
- Idea: Copy to array, reverse in groups, rebuild.
- Time: O(n)
- Space: O(n)

Approach 2: Optimal — Iterative Group Reversal
- Idea: Reverse each group of k in place using pointer manipulation.
- Time: O(n)
- Space: O(1)

=== DRY RUN ===
List: 1 -> 2 -> 3 -> 4 -> 5, k = 2

dummy -> 1 -> 2 -> 3 -> 4 -> 5
group_prev = dummy

--- Group 1: nodes 1, 2 ---
Check: advance k=2 from group_prev: 1, 2. kth = node(2). Enough nodes.
group_next = kth.next = node(3).

Reverse 1 -> 2:
  Start at node(1) (the actual group head), reverse until reaching group_next.
  curr = node(1)
  curr.next = group_prev(=dummy) ... wait, need careful reversal.

  Better: reverse from group_prev.next to kth.
  Let's say: prev = group_next, curr = group_prev.next = node(1)
  Standard reversal loop until curr reaches group_next:
    tmp = curr.next = node(2)
    curr.next = prev = node(3)
    prev = curr = node(1)
    curr = tmp = node(2)
    tmp = curr.next = node(3)  [= group_next]
    curr.next = prev = node(1)
    prev = curr = node(2)
    curr = tmp = node(3) = group_next -> STOP

  Reversed segment: 2 -> 1 -> 3
  New head of group = prev = node(2)
  New tail of group = old head = node(1)

  Rewire: group_prev.next = prev (dummy -> 2)
          [node(1).next already points to group_next = 3]

  Now: dummy -> 2 -> 1 -> 3 -> 4 -> 5
  group_prev = node(1) (the tail of the just-reversed group)

--- Group 2: nodes 3, 4 ---
kth = node(4). group_next = node(5).
Reverse 3 -> 4 => 4 -> 3.
Rewire: node(1).next = node(4), node(3).next = node(5)

Now: dummy -> 2 -> 1 -> 4 -> 3 -> 5
group_prev = node(3)

--- Group 3: nodes 5 ---
Advance k=2: only 1 node (5) left. Not enough. Stop.

Result: 2 -> 1 -> 4 -> 3 -> 5

=== COMPLEXITY ANALYSIS ===
Time: O(n) — each node is visited a constant number of times.
Space: O(1) — only pointer manipulation.

=== EDGE CASES ===
- k = 1 (no reversal needed)
- k == length (reverse entire list)
- length is a multiple of k (no leftover nodes)
- length is NOT a multiple of k (leftover nodes stay as-is)
- Single node
- Empty list

=== INTERVIEW TIPS ===
- The hardest part is getting the pointer rewiring right. Draw it on paper.
- Using a dummy node before the head is essential — the first group's reversal
  changes the head.
- The helper to find the k-th node keeps the main loop clean.
- Common bug: not connecting group_prev to the new head of the reversed group,
  or forgetting to update group_prev to the tail of the reversed group for
  the next iteration.
- Follow-up (LeetCode 92): Reverse a specific sublist [m, n] — similar
  pointer manipulation.
- The `reverse` helper reverses [start, group_next), i.e., it stops at
  group_next without including it.
'''

# === SOLUTION ===
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reverseKGroup(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    """Reverse nodes in groups of k."""
    dummy = ListNode(0, head)
    group_prev = dummy

    while True:
        # Find the k-th node from group_prev.
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                # Not enough nodes for a full group. We're done.
                return dummy.next

        group_next = kth.next  # Node after this group.

        # Reverse the k nodes: [group_prev.next, kth].
        curr = group_prev.next
        prev = group_next  # After reversal, first node points to group_next.
        while curr != group_next:
            tmp = curr.next
            curr.next = prev
            prev = curr
            curr = tmp

        # Reconnect: group_prev -> new head (kth), old head -> group_next.
        tmp = group_prev.next  # Old head (now tail of reversed group).
        group_prev.next = kth  # kth is the new head of this group.
        group_prev = tmp       # Move group_prev to the tail for next iteration.

    # Unreachable due to return inside loop, but kept for clarity.
    return dummy.next


# === TEST CASES ===
if __name__ == "__main__":
    def make_list(vals):
        dummy = ListNode()
        curr = dummy
        for v in vals:
            curr.next = ListNode(v)
            curr = curr.next
        return dummy.next

    def to_list(head):
        result = []
        while head:
            result.append(head.val)
            head = head.next
        return result

    # Test 1: standard (5 nodes, k=2)
    h = make_list([1, 2, 3, 4, 5])
    assert to_list(reverseKGroup(h, 2)) == [2, 1, 4, 3, 5]
    # Test 2: k=3
    h = make_list([1, 2, 3, 4, 5])
    assert to_list(reverseKGroup(h, 3)) == [3, 2, 1, 4, 5]
    # Test 3: k=1 (no change)
    h = make_list([1, 2, 3, 4, 5])
    assert to_list(reverseKGroup(h, 1)) == [1, 2, 3, 4, 5]
    # Test 4: k == length (reverse all)
    h = make_list([1, 2, 3])
    assert to_list(reverseKGroup(h, 3)) == [3, 2, 1]
    # Test 5: single node
    h = make_list([1])
    assert to_list(reverseKGroup(h, 1)) == [1]
    # Test 6: even length, k=2 (clean groups)
    h = make_list([1, 2, 3, 4])
    assert to_list(reverseKGroup(h, 2)) == [2, 1, 4, 3]
    print("All tests passed!")
