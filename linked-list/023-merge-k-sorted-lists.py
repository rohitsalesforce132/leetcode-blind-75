'''
LEETCODE #23: Merge K Sorted Lists
DIFFICULTY: Hard
TOPIC: Linked List / Heap

=== PROBLEM STATEMENT ===
You are given an array of k linked-lists lists, where each linked-list is
sorted in ascending order.

Merge all the linked-lists into one sorted linked-list and return it.

=== INTUITION ===
We need to merge k lists. At each step, we pick the smallest current head
among all k lists and append it to the result. A min-heap makes this
efficient: instead of scanning all k heads each time (O(k) per node), the
heap gives us the minimum in O(log k).

Key detail: Python's heapq compares tuples. If we push (node.val, node),
ties on val cause heap to compare node objects, which aren't comparable. To
avoid this, we push (node.val, index, node) where index is a unique tie-
breaker (so node objects are never compared).

=== APPROACHES ===
Approach 1: Brute Force — Gather and Sort
- Idea: Collect all nodes into a list, sort by value, rebuild list.
- Time: O(N log N) where N = total number of nodes.
- Space: O(N)

Approach 2: Merge One by One
- Idea: Repeatedly merge pairs of lists using the two-list merge.
- Time: O(k * N) in the worst case (merging into an increasingly large list).
- Space: O(1)

Approach 3: Divide and Conquer (Merge Pairs)
- Idea: Merge lists in pairs, halving the number of lists each round.
- Time: O(N log k)
- Space: O(log k) for recursion stack.

Approach 4: Optimal — Min-Heap
- Idea: Keep all current heads in a min-heap; extract min, push its next.
- Time: O(N log k)
- Space: O(k) for the heap.

=== DRY RUN ===
lists = [1->4->5, 2->3->6, 7->8]

Heap initially: [(1,0,n1), (2,1,n2), (7,2,n7)]  (min-heap by val)

Step 1: Pop (1,0,n1). Append 1 to result. Push n1.next=n4.
        Heap: [(2,1,n2), (4,0,n4), (7,2,n7)]
        Result: 1

Step 2: Pop (2,1,n2). Append 2. Push n2.next=n3.
        Heap: [(3,1,n3), (4,0,n4), (7,2,n7)]
        Result: 1->2

Step 3: Pop (3,1,n3). Append 3. Push n3.next=n6.
        Heap: [(4,0,n4), (6,1,n6), (7,2,n7)]
        Result: 1->2->3

Step 4: Pop (4,0,n4). Append 4. Push n4.next=n5.
        Heap: [(5,0,n5), (6,1,n6), (7,2,n7)]
        Result: 1->2->3->4

Step 5: Pop (5,0,n5). Append 5. n5.next=None, nothing to push.
        Heap: [(6,1,n6), (7,2,n7)]
        Result: 1->2->3->4->5

Step 6: Pop (6,1,n6). Append 6. Nothing to push.
        Heap: [(7,2,n7)]
        Result: 1->2->3->4->5->6

Step 7: Pop (7,2,n7). Append 7. Push n7.next=n8.
        Heap: [(8,2,n8)]
        Result: 1->2->3->4->5->6->7

Step 8: Pop (8,2,n8). Append 8. Nothing to push.
        Heap: []
        Result: 1->2->3->4->5->6->7->8

=== COMPLEXITY ANALYSIS ===
Time: O(N log k) — each of N nodes is pushed/popped once, each heap op is
      O(log k).
Space: O(k) for the heap.

=== EDGE CASES ===
- Empty lists array (lists = [])
- All lists empty
- Some lists empty, some not
- Single list
- Lists of very different lengths
- All lists have identical values

=== INTERVIEW TIPS ===
- The min-heap approach is the most common expected solution. Be ready to
  explain the tie-breaking trick with the index.
- The divide-and-conquer approach is also excellent — it avoids the heap
  entirely and has the same time complexity.
- Clarify: can lists be empty? Can the array itself be empty?
- Follow-up: What if k is very large? (The heap approach handles this well.)
- Follow-up: What if lists are not sorted? (You'd need to sort all nodes,
  making it O(N log N).)
'''

# === SOLUTION ===
from typing import List, Optional
import heapq


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def mergeKLists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """Merge k sorted lists using a min-heap."""
    min_heap = []

    # Push the head of each non-empty list into the heap.
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(min_heap, (node.val, i, node))

    dummy = ListNode()
    tail = dummy

    while min_heap:
        val, i, node = heapq.heappop(min_heap)
        tail.next = node
        tail = tail.next

        # If the popped node has a next, push it into the heap.
        if node.next:
            heapq.heappush(min_heap, (node.next.val, i, node.next))

    return dummy.next


def mergeKListsDivideConquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """Divide and conquer: merge pairs of lists."""
    if not lists:
        return None

    def merge_two(l1, l2):
        """Merge two sorted lists (same as LeetCode 21)."""
        dummy = ListNode()
        tail = dummy
        while l1 and l2:
            if l1.val <= l2.val:
                tail.next = l1
                l1 = l1.next
            else:
                tail.next = l2
                l2 = l2.next
            tail = tail.next
        tail.next = l1 if l1 else l2
        return dummy.next

    # Keep merging pairs until one list remains.
    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(merge_two(l1, l2))
        lists = merged

    return lists[0]


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
    lists = [make_list([1, 4, 5]), make_list([2, 3, 6]), make_list([7, 8])]
    assert to_list(mergeKLists(lists)) == [1, 2, 3, 4, 5, 6, 7, 8]
    # Test 2: empty array
    assert to_list(mergeKLists([])) == []
    # Test 3: all empty lists
    assert to_list(mergeKLists([None, None, None])) == []
    # Test 4: single list
    assert to_list(mergeKLists([make_list([1, 2, 3])])) == [1, 2, 3]
    # Test 5: some empty lists
    lists = [None, make_list([1, 3]), None, make_list([2, 4])]
    assert to_list(mergeKLists(lists)) == [1, 2, 3, 4]
    # Test 6: divide and conquer version
    lists = [make_list([1, 4, 5]), make_list([2, 3, 6]), make_list([7, 8])]
    assert to_list(mergeKListsDivideConquer(lists)) == [1, 2, 3, 4, 5, 6, 7, 8]
    print("All tests passed!")
