'''
LEETCODE #206: Reverse Linked List
DIFFICULTY: Easy
TOPIC: Linked List

=== PROBLEM STATEMENT ===
Given the head of a singly linked list, reverse the list, and return the
reversed list's head.

=== INTUITION ===
To reverse a linked list, we need to "flip" every node's next pointer to
point to the previous node instead of the next node. We maintain three
pointers:
- `prev`: starts as None (will become the new tail's next).
- `curr`: the node we're currently processing.
- `nxt`: temporarily holds curr.next so we don't lose the rest of the list.

At each step, we redirect curr.next to prev, then advance all three pointers
forward.

=== APPROACHES ===
Approach 1: Brute Force — Use a Stack
- Idea: Push all nodes onto a stack, then pop and rebuild.
- Time: O(n)
- Space: O(n)

Approach 2: Optimal — Iterative Three-Pointer
- Idea: Flip pointers one node at a time.
- Time: O(n)
- Space: O(1)

Approach 3: Recursive
- Idea: Recurse to the end, then flip pointers on the way back.
- Time: O(n)
- Space: O(n) for the call stack

=== DRY RUN ===
List: 1 -> 2 -> 3 -> None

Initial: prev=None, curr=node(1)

Step 1: nxt = curr.next = node(2)
        curr.next = prev = None      # 1 -> None
        prev = curr = node(1)
        curr = nxt = node(2)
        State: 1->None, prev->1, curr->2

Step 2: nxt = curr.next = node(3)
        curr.next = prev = node(1)   # 2 -> 1
        prev = curr = node(2)
        curr = nxt = node(3)
        State: 2->1->None, prev->2, curr->3

Step 3: nxt = curr.next = None
        curr.next = prev = node(2)   # 3 -> 2
        prev = curr = node(3)
        curr = nxt = None
        State: 3->2->1->None, prev->3, curr=None

Loop exits (curr is None). Return prev = node(3).
Result: 3 -> 2 -> 1 -> None

=== COMPLEXITY ANALYSIS ===
Time: O(n) — visit each node once.
Space: O(1) — only three pointers used.

=== EDGE CASES ===
- Empty list (head = None)
- Single-node list
- Two-node list
- Long list

=== INTERVIEW TIPS ===
- This is a must-know fundamental. Practice until you can write it from
  memory without hesitation.
- The recursive version is elegant but uses O(n) stack space. Interviewers
  often ask for both and compare trade-offs.
- Common bug: forgetting to save curr.next before overwriting it.
- Follow-up: reverse a sublist between indices m and n (LeetCode 92).
'''

# === SOLUTION ===
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reverseList(head: Optional[ListNode]) -> Optional[ListNode]:
    """Iterative reversal using three pointers."""
    prev = None
    curr = head

    while curr:
        nxt = curr.next    # Save the next node.
        curr.next = prev   # Reverse the pointer.
        prev = curr        # Advance prev.
        curr = nxt         # Advance curr.

    return prev


def reverseListRecursive(head: Optional[ListNode]) -> Optional[ListNode]:
    """Recursive reversal. The new head is the last node."""
    # Base case: empty or single-node list is already reversed.
    if not head or not head.next:
        return head

    # Recurse: reverse the rest of the list.
    new_head = reverseListRecursive(head.next)

    # On the way back: head.next still points to the old next node.
    # Make that node point back to us.
    head.next.next = head
    head.next = None  # Avoid cycles.

    return new_head


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

    # Test 1: standard
    assert to_list(reverseList(make_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    # Test 2: single element
    assert to_list(reverseList(make_list([1]))) == [1]
    # Test 3: empty
    assert to_list(reverseList(make_list([]))) == []
    # Test 4: two elements
    assert to_list(reverseList(make_list([1, 2]))) == [2, 1]
    # Test 5: recursive version
    assert to_list(reverseListRecursive(make_list([1, 2, 3]))) == [3, 2, 1]
    print("All tests passed!")
