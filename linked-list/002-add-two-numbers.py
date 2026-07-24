'''
LEETCODE #2: Add Two Numbers
DIFFICULTY: Medium
TOPIC: Linked List

=== PROBLEM STATEMENT ===
You are given two non-empty linked lists representing two non-negative
integers. The digits are stored in reverse order, and each of their nodes
contains a single digit. Add the two numbers and return the sum as a linked
list (also in reverse order).

You may assume the two numbers do not contain any leading zero, except the
number 0 itself.

=== INTUITION ===
This is exactly like manual addition from right to left — and since the
digits are stored in reverse order (least significant digit first), we can
simply iterate from the heads and add digit by digit, carrying over any
overflow to the next position.

We use a dummy node to build the result list, and maintain a `carry` variable
that can be 0 or 1 (since max digit sum is 9+9+1=19).

=== APPROACHES ===
Approach 1: Brute Force — Convert to Integers
- Idea: Walk each list to reconstruct the number, add them, then rebuild a
  list. Fails for very large numbers (beyond 64-bit integer range).
- Time: O(max(m, n))
- Space: O(max(m, n))
- NOTE: Not recommended — doesn't work for arbitrarily large inputs.

Approach 2: Optimal — Digit-by-Digit with Carry
- Idea: Add digit by digit with a carry, exactly like grade-school addition.
- Time: O(max(m, n))
- Space: O(max(m, n)) for the result list.

=== DRY RUN ===
l1 = 2 -> 4 -> 3   (represents 342)
l2 = 5 -> 6 -> 4   (represents 465)
Expected: 7 -> 0 -> 8  (represents 807)

dummy -> None, carry=0, tail=dummy

Step 1: l1=2, l2=5, carry=0 => total=7, digit=7, carry=0
        tail.next = node(7), tail=node(7)
        l1=4, l2=6

Step 2: l1=4, l2=6, carry=0 => total=10, digit=0, carry=1
        tail.next = node(0), tail=node(0)
        l1=3, l2=4

Step 3: l1=3, l2=4, carry=1 => total=8, digit=8, carry=0
        tail.next = node(8), tail=node(8)
        l1=None, l2=None

Loop exits (both None, carry=0). Return dummy.next.
Result: 7 -> 0 -> 8

=== COMPLEXITY ANALYSIS ===
Time: O(max(m, n)) — iterate through the longer list.
Space: O(max(m, n)) — result list has at most max(m,n)+1 nodes.

=== EDGE CASES ===
- Different length lists
- Carry propagation at the end (e.g., 9+9 = 18, needs extra digit)
- One list much longer than the other
- Sum results in an extra digit (e.g., 999 + 1 = 1000)
- Both lists represent zero ([0] + [0])

=== INTERVIEW TIPS ===
- The dummy node pattern is essential here — without it, you'd need to
  special-case the head of the result.
- The carry can be 0 or 1 since the max sum of two digits + carry is 19.
- Clarify: digits are in REVERSE order (LSB first). This actually makes the
  problem easier because you process from least significant to most.
- Follow-up (LeetCode 445): What if digits were in forward order? (You'd need
  to reverse the lists first, or use stacks.)
'''

# === SOLUTION ===
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def addTwoNumbers(l1: Optional[ListNode],
                  l2: Optional[ListNode]) -> Optional[ListNode]:
    """Add two numbers represented in reverse-order linked lists."""
    dummy = ListNode()
    tail = dummy
    carry = 0

    while l1 or l2 or carry:
        # Get the current digits (0 if list exhausted).
        d1 = l1.val if l1 else 0
        d2 = l2.val if l2 else 0

        total = d1 + d2 + carry
        carry = total // 10
        digit = total % 10

        tail.next = ListNode(digit)
        tail = tail.next

        # Advance the input pointers if available.
        if l1:
            l1 = l1.next
        if l2:
            l2 = l2.next

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

    # Test 1: standard (342 + 465 = 807)
    assert to_list(addTwoNumbers(make_list([2, 4, 3]), make_list([5, 6, 4]))) == [7, 0, 8]
    # Test 2: zero + zero
    assert to_list(addTwoNumbers(make_list([0]), make_list([0]))) == [0]
    # Test 3: carry at end (999 + 1 = 1000)
    assert to_list(addTwoNumbers(make_list([9, 9, 9]), make_list([1]))) == [0, 0, 0, 1]
    # Test 4: different lengths (99 + 1 = 100)
    assert to_list(addTwoNumbers(make_list([9, 9]), make_list([1]))) == [0, 0, 1]
    # Test 5: no carry needed
    assert to_list(addTwoNumbers(make_list([1, 2, 3]), make_list([4, 5, 6]))) == [5, 7, 9]
    print("All tests passed!")
