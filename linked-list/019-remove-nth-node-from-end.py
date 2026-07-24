'''
LEETCODE #19: Remove Nth Node From End of List
DIFFICULTY: Medium
TOPIC: Linked List

=== PROBLEM STATEMENT ===
Given the head of a linked list, remove the n-th node from the end of the
list and return its head.

=== INTUITION ===
The key trick is the "two-pointer / fast-slow" technique with a gap:
1. Advance the `fast` pointer n steps ahead of `slow`.
2. Then advance both pointers together until `fast` reaches the last node.
3. Now `slow` is right before the node to remove — just skip it.

Using a dummy node before the head handles the edge case where we need to
remove the head itself (when n == length of list).

=== APPROACHES ===
Approach 1: Brute Force — Two Passes
- Idea: First pass counts the length. Second pass moves to (length - n)th
  node and removes the next one.
- Time: O(n)
- Space: O(1)

Approach 2: Optimal — Two-Pointer with N-Step Gap (One Pass)
- Idea: Fast pointer gets n steps head start, then both advance together.
- Time: O(n)
- Space: O(1)

=== DRY RUN ===
List: 1 -> 2 -> 3 -> 4 -> 5, n = 2

dummy -> 1 -> 2 -> 3 -> 4 -> 5
fast = dummy, slow = dummy

Phase 1: Advance fast n=2 steps.
  fast = fast.next = node(1)
  fast = fast.next = node(2)
  Now fast is 2 ahead of slow.

Phase 2: Advance both until fast.next is None.
  fast=node(2), slow=dummy
    -> fast=node(3), slow=node(1)
  fast=node(3), slow=node(1)
    -> fast=node(4), slow=node(2)
  fast=node(4), slow=node(2)
    -> fast=node(5), slow=node(3)
  fast=node(5), fast.next=None => stop. slow=node(3).

Phase 3: Remove slow.next (node 4).
  slow.next = slow.next.next => 3 -> 5

Result: 1 -> 2 -> 3 -> 5 -> None

=== COMPLEXITY ANALYSIS ===
Time: O(n) — single pass through the list.
Space: O(1)

=== EDGE CASES ===
- Remove the head (n == length)
- Remove the last node (n == 1)
- Single-node list (n == 1)
- List with exactly n nodes
- n is valid (problem guarantees this)

=== INTERVIEW TIPS ===
- The dummy node is critical here — without it, removing the head requires
  special handling. Always consider using a dummy when you might modify the
  head.
- Explain why this is "one pass" even though fast technically traverses more:
  each node is still visited a constant number of times.
- Follow-up: Can you do it in one pass if n isn't guaranteed valid? (You'd
  need to check fast for None during the n-step advance.)
- Common bug: advancing fast n+1 times instead of n, or using fast instead
  of fast.next in the loop condition.
'''

# === SOLUTION ===
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def removeNthFromEnd(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    """Remove nth node from end using two pointers with n-step gap."""
    dummy = ListNode(0, head)
    fast = dummy
    slow = dummy

    # Advance fast n steps ahead.
    for _ in range(n):
        fast = fast.next

    # Move both until fast reaches the last node.
    while fast.next:
        fast = fast.next
        slow = slow.next

    # Remove the node after slow.
    slow.next = slow.next.next

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

    # Test 1: remove middle
    assert to_list(removeNthFromEnd(make_list([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
    # Test 2: remove head (n == length)
    assert to_list(removeNthFromEnd(make_list([1, 2, 3]), 3)) == [2, 3]
    # Test 3: remove last (n == 1)
    assert to_list(removeNthFromEnd(make_list([1, 2, 3]), 1)) == [1, 2]
    # Test 4: single node
    assert to_list(removeNthFromEnd(make_list([1]), 1)) == []
    # Test 5: two nodes, remove first
    assert to_list(removeNthFromEnd(make_list([1, 2]), 2)) == [2]
    # Test 6: two nodes, remove last
    assert to_list(removeNthFromEnd(make_list([1, 2]), 1)) == [1]
    print("All tests passed!")
