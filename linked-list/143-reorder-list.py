'''
LEETCODE #143: Reorder List
DIFFICULTY: Medium
TOPIC: Linked List

=== PROBLEM STATEMENT ===
You are given the head of a singly linked list. The list can be represented as:
  L0 → L1 → … → Ln - 1 → Ln
Reorder the list to be in the following form:
  L0 → Ln → L1 → Ln - 1 → L2 → Ln - 2 → …

You may not modify the values in the list's nodes. Only nodes themselves may
be changed.

=== INTUITION ===
This problem combines three classic linked-list techniques:
1. Find the middle of the list (slow/fast pointer).
2. Reverse the second half of the list.
3. Merge the two halves interleavingly (one from first half, one from reversed
   second half).

Breaking it into these sub-problems makes it much more manageable.

=== APPROACHES ===
Approach 1: Brute Force — Array
- Idea: Copy all nodes into an array, then reorder using two pointers.
- Time: O(n)
- Space: O(n) — the array.

Approach 2: Optimal — Find Middle + Reverse + Interleave Merge
- Idea: Three-phase approach described in intuition.
- Time: O(n)
- Space: O(1)

=== DRY RUN ===
List: 1 -> 2 -> 3 -> 4 -> 5

Phase 1: Find middle.
  slow=1, fast=1
  Step: slow=2, fast=3 -> slow=3, fast=5 -> fast can't advance (5.next=None)
  Middle node = slow = node(3).

Phase 2: Reverse second half [3 -> 4 -> 5].
  After reversing: 5 -> 4 -> 3 -> None
  First half remains: 1 -> 2 -> 3 (but we cut at 2, so: 1 -> 2)

  Actually, let's be precise. After finding middle=3, we reverse from 3 onward:
  second_half = reverse(3) => 5 -> 4 -> 3 -> None
  first_half = 1 -> 2 -> None (we set 2.next = None to separate)

Phase 3: Interleave merge.
  first: 1 -> 2 -> None
  second: 5 -> 4 -> 3 -> None

  Step 1: 1.next = 5, 5.next = 2 => 1 -> 5 -> 2 -> ...
          advance first=2, second=4
  Step 2: 2.next = 4, 4.next = None => 1 -> 5 -> 2 -> 4 -> ...
          advance first=None, second=3
  Loop exits (first is None). 3 is dropped (not needed — there are only 5 nodes).

Result: 1 -> 5 -> 2 -> 4 -> 3 -> None

=== COMPLEXITY ANALYSIS ===
Time: O(n) — find middle O(n), reverse O(n), merge O(n).
Space: O(1) — only pointer manipulation.

=== EDGE CASES ===
- Empty list or single node -> no change
- Two-node list -> no change (already in form)
- Three-node list -> just swap last two
- Even-length list vs odd-length list
- Very long list

=== INTERVIEW TIPS ===
- Break the problem into three well-known sub-problems. This shows you can
  decompose complex problems into simpler, reusable operations.
- Clarify "you may not modify values" — this means you must rewire pointers.
- Follow-up: Can you do it recursively? (Yes, but O(n) space for the stack.)
- Common bug: forgetting to cut the list at the middle before reversing and
  merging, which causes infinite loops or incorrect results.
'''

# === SOLUTION ===
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reorderList(head: Optional[ListNode]) -> None:
    """Reorder in-place: L0->Ln->L1->Ln-1->..."""
    if not head or not head.next:
        return

    # --- Phase 1: Find the middle using slow/fast pointers. ---
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    # `slow` now points to the middle (or end of first half for even length).

    # --- Phase 2: Reverse the second half. ---
    second = slow.next  # Start of second half.
    slow.next = None    # Cut the list into two halves.

    prev = None
    curr = second
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    second = prev  # `prev` is the new head of the reversed second half.

    # --- Phase 3: Interleave merge the two halves. ---
    first = head
    while second:
        tmp1, tmp2 = first.next, second.next
        first.next = second  # Link first -> second
        second.next = tmp1   # Link second -> rest of first
        first = tmp1
        second = tmp2


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

    # Test 1: odd length
    h = make_list([1, 2, 3, 4, 5])
    reorderList(h)
    assert to_list(h) == [1, 5, 2, 4, 3]
    # Test 2: even length
    h = make_list([1, 2, 3, 4])
    reorderList(h)
    assert to_list(h) == [1, 4, 2, 3]
    # Test 3: single node
    h = make_list([1])
    reorderList(h)
    assert to_list(h) == [1]
    # Test 4: two nodes
    h = make_list([1, 2])
    reorderList(h)
    assert to_list(h) == [1, 2]
    # Test 5: three nodes
    h = make_list([1, 2, 3])
    reorderList(h)
    assert to_list(h) == [1, 3, 2]
    # Test 6: empty
    h = make_list([])
    reorderList(h)
    assert to_list(h) == []
    print("All tests passed!")
