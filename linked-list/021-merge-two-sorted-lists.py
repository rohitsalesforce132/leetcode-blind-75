'''
LEETCODE #21: Merge Two Sorted Lists
DIFFICULTY: Easy
TOPIC: Linked List

=== PROBLEM STATEMENT ===
You are given the heads of two sorted linked lists list1 and list2.

Merge the two lists into one sorted list. The list should be made by
splicing together the nodes of the first two lists.

Return the head of the merged linked list.

=== INTUITION ===
Both lists are sorted, so we use a two-pointer technique:
- Compare the current nodes of both lists.
- Attach the smaller one to the merged list.
- Advance the pointer in the list from which we took the node.
- When one list is exhausted, append the remainder of the other.

A dummy/sentinel node simplifies edge cases (like building the result from
scratch) — we never need to handle the first node specially.

=== APPROACHES ===
Approach 1: Brute Force — Collect and Sort
- Idea: Collect all values, sort them, rebuild the list.
- Time: O((n+m) log(n+m))
- Space: O(n+m)

Approach 2: Optimal — Iterative Two-Pointer with Dummy Node
- Idea: Compare heads, attach smaller, advance.
- Time: O(n + m)
- Space: O(1) — we reuse existing nodes, only adding a dummy.

Approach 3: Recursive
- Idea: Recursively pick the smaller head and link it.
- Time: O(n + m)
- Space: O(n + m) for the call stack

=== DRY RUN ===
list1 = 1 -> 2 -> 4
list2 = 1 -> 3 -> 4

dummy -> None, tail = dummy

Step 1: list1(1) <= list2(1) => tail.next = list1, list1 = list1.next = node(2)
        tail = tail.next = node(1)
Step 2: list1(2) > list2(1)  => tail.next = list2, list2 = list2.next = node(3)
        tail = tail.next = node(1)
Step 3: list1(2) <= list2(3) => tail.next = list1, list1 = list1.next = node(4)
        tail = tail.next = node(2)
Step 4: list1(4) > list2(3)  => tail.next = list2, list2 = list2.next = node(4)
        tail = tail.next = node(3)
Step 5: list1(4) <= list2(4) => tail.next = list1, list1 = list1.next = None
        tail = tail.next = node(4)
Loop exits (list1 is None). Append list2: tail.next = list2 (node 4).

Result: dummy.next -> 1 -> 1 -> 2 -> 3 -> 4 -> 4 -> None

=== COMPLEXITY ANALYSIS ===
Time: O(n + m) — each node visited once.
Space: O(1) — only pointer manipulation.

=== EDGE CASES ===
- Both lists empty
- One list empty
- Lists of very different lengths
- Lists with duplicate values
- All elements of one list smaller than the other

=== INTERVIEW TIPS ===
- The dummy/sentinel node pattern is essential for linked list problems where
  you're building a new list — it eliminates special-casing the head.
- "Splicing" means reusing the original nodes (no new allocations) — clarify
  this with the interviewer.
- The recursive version is concise but risks stack overflow for very long
  lists; the iterative version is preferred in production.
- Follow-up: merge k sorted lists (LeetCode 23) uses this as a subroutine.
'''

# === SOLUTION ===
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def mergeTwoLists(list1: Optional[ListNode],
                  list2: Optional[ListNode]) -> Optional[ListNode]:
    """Iterative merge using a dummy node for simplicity."""
    dummy = ListNode()
    tail = dummy

    while list1 and list2:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next

    # Attach any remaining nodes (only one of these is non-None).
    tail.next = list1 if list1 else list2

    return dummy.next


def mergeTwoListsRecursive(l1: Optional[ListNode],
                           l2: Optional[ListNode]) -> Optional[ListNode]:
    """Recursive merge — pick smaller head, recurse on the rest."""
    if not l1:
        return l2
    if not l2:
        return l1

    if l1.val <= l2.val:
        l1.next = mergeTwoListsRecursive(l1.next, l2)
        return l1
    else:
        l2.next = mergeTwoListsRecursive(l1, l2.next)
        return l2


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

    # Test 1: standard merge
    assert to_list(mergeTwoLists(make_list([1, 2, 4]), make_list([1, 3, 4]))) == [1, 1, 2, 3, 4, 4]
    # Test 2: both empty
    assert to_list(mergeTwoLists(None, None)) == []
    # Test 3: one empty
    assert to_list(mergeTwoLists(None, make_list([0]))) == [0]
    # Test 4: one much longer
    assert to_list(mergeTwoLists(make_list([5]), make_list([1, 2, 3, 4]))) == [1, 2, 3, 4, 5]
    # Test 5: recursive version
    assert to_list(mergeTwoListsRecursive(make_list([1, 3, 5]), make_list([2, 4, 6]))) == [1, 2, 3, 4, 5, 6]
    print("All tests passed!")
