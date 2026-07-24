'''
LEETCODE #141: Linked List Cycle
DIFFICULTY: Easy
TOPIC: Linked List

=== PROBLEM STATEMENT ===
Given head, the head of a linked list, determine if the linked list has a
cycle in it. There is a cycle in a linked list if there is some node in the
list that can be reached again by continuously following the next pointer.
Return true if there is a cycle in the linked list. Otherwise, return false.

=== INTUITION ===
Floyd's Tortoise and Hare algorithm: use two pointers moving at different
speeds (slow = 1 step, fast = 2 steps). If there's a cycle, the fast pointer
will eventually "lap" the slow pointer inside the cycle. If there's no cycle,
fast reaches the end (None).

Why it works: Once both pointers are inside the cycle, the fast pointer gains
on the slow pointer by 1 node per step. Since the cycle has finite length,
they must meet.

=== APPROACHES ===
Approach 1: Brute Force — Hash Set
- Idea: Store visited nodes in a set. If we see a node again, there's a cycle.
- Time: O(n)
- Space: O(n) for the set.

Approach 2: Optimal — Floyd's Tortoise and Hare (Two Pointers)
- Idea: Slow moves 1 step, fast moves 2 steps. They meet iff there's a cycle.
- Time: O(n)
- Space: O(1)

=== DRY RUN ===
List: 3 -> 2 -> 0 -> -4
             ^___________|   (-4 points back to 2, creating a cycle)

slow=3, fast=3

Step 1: slow=2, fast=0   (fast moved 3->2->0)
Step 2: slow=0, fast=2   (fast moved 0->-4->2)
Step 3: slow=-4, fast=-4 (slow moved 0->-4, fast moved 2->0->-4)
        slow == fast => cycle detected! return True

=== COMPLEXITY ANALYSIS ===
Time: O(n) — in the worst case, we traverse the list before detecting.
Space: O(1)

=== EDGE CASES ===
- No cycle (fast reaches None)
- Single node with a self-loop (next points to itself)
- Single node, no cycle
- Cycle that includes the head
- Very long acyclic list
- Cycle at the very end (tail points to head or some middle node)

=== INTERVIEW TIPS ===
- Floyd's algorithm is a classic — know the intuition (fast gains 1 per step
  inside the cycle).
- Explain why it's O(n): the slow pointer enters the cycle in at most n steps.
  Then fast catches up within cycle_length steps. Total is O(n).
- Follow-up (LeetCode 142): Find the START of the cycle. After slow and fast
  meet, reset one pointer to head and move both at the same speed — they meet
  at the cycle start. (Mathematical proof involves the distance relationships.)
- Common bug: checking fast == slow at the WRONG time (should check after
  moving, not before; and must check fast/fast.next for None before advancing).
'''

# === SOLUTION ===
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def hasCycle(head: Optional[ListNode]) -> bool:
    """Floyd's Tortoise and Hare cycle detection."""
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next          # Moves 1 step.
        fast = fast.next.next     # Moves 2 steps.

        if slow == fast:
            return True

    return False


# === TEST CASES ===
if __name__ == "__main__":
    def make_list(vals, pos):
        """Create list with optional cycle at index `pos` (or -1 for none)."""
        if not vals:
            return None
        nodes = [ListNode(v) for v in vals]
        for i in range(len(nodes) - 1):
            nodes[i].next = nodes[i + 1]
        if pos >= 0:
            nodes[-1].next = nodes[pos]
        return nodes[0]

    # Test 1: cycle present (tail connects to index 1)
    assert hasCycle(make_list([3, 2, 0, -4], 1)) is True
    # Test 2: cycle present (tail connects to index 0)
    assert hasCycle(make_list([1, 2], 0)) is True
    # Test 3: no cycle
    assert hasCycle(make_list([1, 2, 3, 4], -1)) is False
    # Test 4: single node, no cycle
    assert hasCycle(make_list([1], -1)) is False
    # Test 5: single node, self-loop
    assert hasCycle(make_list([1], 0)) is True
    # Test 6: empty
    assert hasCycle(None) is False
    print("All tests passed!")
