'''
CHAPTER 3: STACKS, QUEUES & LINKED LISTS
=========================================

"Three data structures that show up everywhere in coding interviews.
Stack = LAST IN FIRST OUT. Queue = FIRST IN FIRST OUT.
Linked List = chain of nodes connected by pointers."

---

PART 1: STACKS
==============

WHAT IS A STACK?
----------------
Real-world analogy: A STACK OF PLATES.

    You add plates to the TOP.
    You take plates from the TOP.
    You CANNOT take a plate from the bottom without removing all plates above it.

    This is called LIFO: Last In, First Out.

         PUSH    ← add to top
          ↓
        ┌─────┐
        │  C  │  ← last added (TOP)
        ├─────┤
        │  B  │
        ├─────┤
        │  A  │  ← first added (BOTTOM)
        └─────┘
          ↑
         POP     ← remove from top

STACK OPERATIONS (ALL O(1)):
    push(x) — add x to the top     → list.append(x)
    pop()   — remove from top       → list.pop()
    peek()  — look at top element   → list[-1]
    size()  — number of elements    → len(list)
'''

# --- STACK USING PYTHON LIST ---
stack = []

# Push (add to top)
stack.append("A")
stack.append("B")
stack.append("C")
print("Stack after pushes:", stack)      # ['A', 'B', 'C']

# Peek (look at top)
print("Top element:", stack[-1])         # 'C'

# Pop (remove from top)
print("Popped:", stack.pop())            # 'C'
print("Popped:", stack.pop())            # 'B'
print("Stack now:", stack)               # ['A']


'''
WHEN TO USE A STACK?
--------------------
1. **Reversing something** — push all items, then pop them all → reversed order
2. **Matching/Balancing** — parentheses, HTML tags, function calls
3. **Undo/Redo** — every action is pushed; undo pops it
4. **Backtracking** — remember where you've been so you can go back
5. **Call stack** — recursion uses a stack internally!

THE #1 STACK INTERVIEW PROBLEM: VALID PARENTHESES
--------------------------------------------------
"Given a string with ()[]{} characters, are all brackets properly matched?"

    "([])"     → valid   ✓
    "([)]"     → invalid ✗
    "("        → invalid ✗ (unclosed)

ALGORITHM:
    - Scan left to right.
    - When you see an OPENING bracket: push it onto the stack.
    - When you see a CLOSING bracket: check if the top of the stack
      has the matching opening bracket. If yes, pop it. If no, invalid.

    At the end: stack should be EMPTY (all brackets closed).

WHY A STACK? Because the most recent opening bracket must be closed first.
    This is exactly LIFO behavior!
'''

def is_valid_parentheses(s):
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}

    for char in s:
        if char in '([{':          # Opening bracket → push
            stack.append(char)
        elif char in ')]}':        # Closing bracket → check match
            if not stack or stack[-1] != matching[char]:
                return False       # Mismatch or nothing to match with
            stack.pop()            # Matched → remove the opening bracket

    return len(stack) == 0         # Stack should be empty (all closed)

print("\n--- Valid Parentheses ---")
print(is_valid_parentheses("([])"))     # True
print(is_valid_parentheses("([)]"))     # False
print(is_valid_parentheses("((()))"))   # True
print(is_valid_parentheses("("))        # False


'''
MONOTONIC STACK (Advanced pattern — appears in 5+ Blind 75 problems)
---------------------------------------------------------------------
A "monotonic stack" is a stack that is always sorted (either increasing or
decreasing). When you push a new element, you first pop any elements that
would violate the sorted order.

Use case: "For each element, find the NEXT element that is bigger/smaller."

Example: Daily Temperatures (LeetCode #739)
    "For each day's temperature, how many days until a warmer day?"

    temps = [73, 74, 75, 71, 69, 72, 76, 73]

    We maintain a stack of INDICES where temperatures are in DECREASING order.
    When we see a temperature warmer than the stack top, we've found the answer
    for those days.
'''

def daily_temperatures(temps):
    n = len(temps)
    result = [0] * n
    stack = []  # stores indices, temperatures are decreasing

    for i in range(n):
        # While current temp is warmer than the temp at stack top
        while stack and temps[i] > temps[stack[-1]]:
            prev_day = stack.pop()
            result[prev_day] = i - prev_day  # Days waited
        stack.append(i)

    return result

print("\n--- Monotonic Stack: Daily Temperatures ---")
print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
# [1, 1, 4, 2, 1, 1, 0, 0]


'''
PART 2: QUEUES
==============

WHAT IS A QUEUE?
----------------
Real-world analogy: A LINE AT A STORE.

    The FIRST person to get in line is the FIRST person served.
    New people join at the BACK. Service happens at the FRONT.

    This is called FIFO: First In, First Out.

    ENQUEUE       DEQUEUE
      ↓              ↑
    BACK           FRONT
    ┌───┬───┬───┬───┐
    │ D │ C │ B │ A │
    └───┴───┴───┴───┘
              ↑
            (oldest, served next)

QUEUE OPERATIONS (ALL O(1)):
    enqueue(x) — add to back    → from collections import deque; d.append(x)
    dequeue()  — remove from front → d.popleft()
    peek()     — look at front     → d[0]

In Python, use collections.deque (double-ended queue) for O(1) operations.
Do NOT use a list — list.pop(0) is O(n)!
'''

from collections import deque

queue = deque()

# Enqueue (add to back)
queue.append("Person 1")
queue.append("Person 2")
queue.append("Person 3")
print("\nQueue:", list(queue))           # ['Person 1', 'Person 2', 'Person 3']

# Dequeue (remove from front)
print("Served:", queue.popleft())        # 'Person 1' (first in, first out)
print("Served:", queue.popleft())        # 'Person 2'
print("Queue now:", list(queue))         # ['Person 3']


'''
WHEN TO USE A QUEUE?
--------------------
1. **BFS (Breadth-First Search)** — explore level by level (trees, graphs)
2. **Level-order traversal** — process nodes floor by floor in a tree
3. **Task scheduling** — processes in order of arrival
4. **Sliding window maximum** — using a deque

STACK vs QUEUE — QUICK COMPARISON:
    Stack: LIFO (last in, first out). Like a stack of plates.
    Queue: FIFO (first in, first out). Like a line at a store.

    Stack: push/pop from SAME end (top).
    Queue: push to one end (back), pop from other end (front).


PART 3: LINKED LISTS
=====================

WHAT IS A LINKED LIST?
----------------------
Real-world analogy: A TREASURE HUNT.

    Each clue tells you where the NEXT clue is.

    Clue 1 → "Go to the oak tree" → Clue 2 → "Go to the river" → Clue 3 → null

    You can't skip to Clue 3 directly. You must follow the chain.

A linked list is a chain of NODES. Each node has:
    - DATA (the value)
    - NEXT (a pointer to the next node)

    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
    │ 10   │───→│ 20   │───→│ 30   │───→│ 40   │───→ None
    │next  │    │next  │    │next  │    │next  │
    └──────┘    └──────┘    └──────┘    └──────┘
     ↑
    head

Compare to an array:
    Array:  [10, 20, 30, 40]    ← stored CONTIGUOUSLY (side by side in memory)
    List:   10 → 20 → 30 → 40   ← stored ANYWHERE, connected by pointers

WHY USE A LINKED LIST INSTEAD OF AN ARRAY?
    - Inserting/deleting at the FRONT is O(1) (just change pointers)
    - No need to shift elements like in an array
    - Dynamic size (grows/shrinks without resizing)
    - BUT: no random access (can't do list[3] in O(1); must walk the chain)
'''

# --- DEFINING A LINKED LIST NODE ---
class ListNode:
    """A single node in a singly linked list."""
    def __init__(self, val=0, next=None):
        self.val = val      # The data stored in this node
        self.next = next    # Pointer to the next node (or None if last)

    def __repr__(self):
        return f"Node({self.val})"


# --- BUILDING A LINKED LIST ---
# Create: 10 → 20 → 30 → None
node3 = ListNode(30)
node2 = ListNode(20, node3)
node1 = ListNode(10, node2)
head = node1  # 'head' is our entry point to the list

# --- TRAVERSING A LINKED LIST ---
def print_list(head):
    """Walk the list from head to end, printing values."""
    current = head
    values = []
    while current:
        values.append(str(current.val))
        current = current.next    # Follow the pointer to next node
    print(" → ".join(values) + " → None")

print("\n--- Linked List ---")
print_list(head)  # 10 → 20 → 30 → None


'''
THE MENTAL MODEL FOR LINKED LIST OPERATIONS
-------------------------------------------
The key skill is POINTER MANIPULATION. You're re-routing arrows.

INSERTING AT THE HEAD (O(1)):
    Before: head → [10] → [20] → [30] → None

    Step 1: Create new node [5]
    Step 2: Point new node's next to current head
        [5] → [10] → [20] → [30] → None
    Step 3: Move head to new node
        head → [5] → [10] → [20] → [30] → None

    Done! Just 2 pointer changes. O(1). No shifting needed.
'''

# --- INSERT AT HEAD ---
def insert_at_head(head, val):
    new_node = ListNode(val)
    new_node.next = head   # New node points to old head
    return new_node        # New node becomes the new head

print("\n--- Insert at Head ---")
head = insert_at_head(head, 5)
print_list(head)  # 5 → 10 → 20 → 30 → None


'''
DELETING A NODE (O(n) to find, O(1) to delete):
    Before: head → [5] → [10] → [20] → [30] → None

    Delete [10]:
    Step 1: Find the node BEFORE [10], which is [5]
    Step 2: Change [5].next to skip [10] and point to [20]
        [5] → [20] → [30] → None
           (10 is now disconnected / garbage collected)

    Just 1 pointer change. But finding the node is O(n) because we must
    walk the chain from the head.
'''

# --- DELETE BY VALUE ---
def delete_node(head, target):
    # Special case: delete the head
    if head and head.val == target:
        return head.next  # New head is the second node

    current = head
    while current and current.next:
        if current.next.val == target:
            current.next = current.next.next  # Skip over the target node
            return head
        current = current.next
    return head  # Target not found

print("\n--- Delete Node ---")
head = delete_node(head, 10)
print_list(head)  # 5 → 20 → 30 → None


'''
THE TWO MOST IMPORTANT LINKED LIST PATTERNS
===========================================

PATTERN 1: REVERSING A LINKED LIST
    Before: 1 → 2 → 3 → 4 → None
    After:  4 → 3 → 2 → 1 → None

    The trick: For each node, flip its "next" pointer to point BACKWARDS.

    Visualization:
        None  ←  [1]  ←  [2]  ←  [3]  ←  [4]
                                        ↑
                                       head

    We use 3 pointers:
    - prev: starts as None (will become the last node's next)
    - current: the node we're processing
    - next_temp: save current.next before we overwrite it
'''

def reverse_list(head):
    prev = None
    current = head

    while current:
        next_temp = current.next   # Save what comes after
        current.next = prev        # Reverse the pointer (point backward)
        prev = current             # Move prev forward
        current = next_temp        # Move current forward

    return prev  # prev is now the new head (was the last node)

print("\n--- Reverse Linked List ---")
# Build 1 → 2 → 3 → 4
n4 = ListNode(4)
n3 = ListNode(3, n4)
n2 = ListNode(2, n3)
n1 = ListNode(1, n2)
print("Before reverse:")
print_list(n1)            # 1 → 2 → 3 → 4 → None
reversed_head = reverse_list(n1)
print("After reverse:")
print_list(reversed_head)  # 4 → 3 → 2 → 1 → None


'''
PATTERN 2: FAST & SLOW POINTERS (TORTOISE & HARE)
    Use two pointers: slow moves 1 step, fast moves 2 steps.

    USE CASE 1: Find the MIDDLE of a linked list
        When fast reaches the end, slow is at the middle.

        1 → 2 → 3 → 4 → 5
        fast:        slow:
        step 1:  2        1
        step 2:  4        2
        step 3:  None     3 ← MIDDLE!

    USE CASE 2: Detect a CYCLE (loop)
        If there's a cycle, fast will eventually lap slow and they'll meet.
        If no cycle, fast reaches the end (None).
'''

def find_middle(head):
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next          # 1 step
        fast = fast.next.next     # 2 steps

    return slow  # slow is at the middle

print("\n--- Find Middle ---")
# Build 1 → 2 → 3 → 4 → 5
n5 = ListNode(5)
n4 = ListNode(4, n5)
n3 = ListNode(3, n4)
n2 = ListNode(2, n3)
n1 = ListNode(1, n2)
mid = find_middle(n1)
print(f"Middle node value: {mid.val}")  # 3


def has_cycle(head):
    """Detect if a linked list has a cycle (loop)."""
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:    # They meet → cycle!
            return True

    return False  # Fast reached the end → no cycle

print("\n--- Cycle Detection ---")
# Create a list with a cycle: 1 → 2 → 3 → 4 → back to 2
a = ListNode(1)
b = ListNode(2)
c = ListNode(3)
d = ListNode(4)
a.next = b
b.next = c
c.next = d
d.next = b  # Cycle! 4 points back to 2

print(has_cycle(a))  # True


'''
LINKED LIST SUMMARY:
    - Each node stores data + a pointer to the next node
    - Access by index: O(n) (must walk the chain)
    - Insert/delete at head: O(1)
    - Insert/delete at position: O(n) to find, O(1) to modify
    - Key patterns:
      * Reversing: flip each pointer backward (prev, current, next_temp)
      * Fast & slow pointers: find middle, detect cycles
      * Dummy head: simplify edge cases for insertion/deletion
'''

# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 3 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Stack = LIFO (plates). Push/pop from top. O(1) all operations.
   Use for: bracket matching, reversing, backtracking, monotonic stacks.
2. Queue = FIFO (line). Enqueue back, dequeue front. O(1) with deque.
   Use for: BFS, level-order traversal, scheduling.
3. Linked List = chain of nodes with pointers. O(1) insert/delete at head.
   - Reversing: flip pointers using prev/current/next
   - Fast & slow: find middle, detect cycles
   - No random access (no arr[i] in O(1))

Next: Chapter 4 — Trees, BST, Heaps & Tries
""")
