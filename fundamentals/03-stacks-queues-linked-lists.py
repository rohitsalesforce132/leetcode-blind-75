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

WHY ARE ALL OPERATIONS O(1)?
    A Python list stores elements in a contiguous block of memory with a
    length counter. Appending to the END only writes to the next slot and
    bumps the counter — no shifting needed. Removing from the END is the
    same in reverse. Only MIDDLE inserts/deletes cost O(n) because every
    later element must shift. The TOP of our stack is the END of the list,
    so we never touch the middle. That is the whole trick.

    ┌───┬───┬───┬───┬───┐
    │ A │ B │ C │   │   │   capacity = 5, len = 3
    └───┴───┴───┴───┴───┘
                ↑
              push("D") writes here, len becomes 4. Done.
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
6. **Expression evaluation** — convert infix "2 + 3" to postfix "2 3 +"
7. **Browser back button** — each page visited is pushed; Back pops it

THE "REVERSING" INTUITION:
    Push "abc", then pop 3 times → "cba".
    Why? The last character pushed ('c') is the first one popped.
    LIFO is a natural reverser.

        push a → [a]
        push b → [a, b]
        push c → [a, b, c]
        pop    → c
        pop    → b
        pop    → a
        Output: c, b, a  (reversed!)


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

    " ( [ ] ) "
         ↑
    At this point stack = ['(', '['].  We see ']', whose match is '['.
    The TOP of the stack is '[' → match! Pop it. Stack = ['('].
    The innermost bracket closed first, just like plates: last on, first off.


COMMON MISTAKES (Valid Parentheses)
-----------------------------------
MISTAKE 1: Forgetting to check if the stack is EMPTY before peeking.
    if stack[-1] != matching[char]:   ← CRASHES if stack is empty!
    Fix: check `not stack` FIRST (short-circuit), then peek.

MISTAKE 2: Forgetting to verify the stack is empty at the END.
    Input "(((" pushes three '(' but never closes them. No mismatch
    happens during the loop, so you'd wrongly return True. The final
    `len(stack) == 0` catches this.

MISTAKE 3: Using `=` instead of `in` for opening brackets.
    `if char == '(' or '[' or '{':` is ALWAYS TRUE in Python because
    the string '[' is truthy on its own. Use `if char in '([{':`.
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
print(is_valid_parentheses(")"))        # False (closing with empty stack)
print(is_valid_parentheses("([{}])"))   # True (nested 3 deep)


'''
DRY RUN: is_valid_parentheses("([)]")
    char | stack before | action                 | stack after
    -----|-------------|--------------------------|------------
    '('  | []          | opening → push           | ['(']
    '['  | ['(']       | opening → push           | ['(', '[']
    ')'  | ['(', '[']  | top='[', match of ')'= '(' → MISMATCH → return False

    Notice how the LIFO nature catches the error: ')' wanted to match the
    most recent opener ('['), but ')' pairs with '('. Nested correctly:
    "([])" would pop '[' for ']' first, THEN '(' for ')'.
'''


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

WHY DOES THIS WORK?
    We want, for each index j, the nearest future index i > j with temps[i] > temps[j].
    Imagine scanning left to right. As long as temps stay the same or drop,
    we don't yet have an answer for those earlier days, so we pile their
    indices onto a stack (in decreasing temp order). The INSTANT a warmer
    day arrives, it is — by construction — the FIRST warmer day for every
    colder day sitting on top of the stack, because we scan left to right
    and anything warmer would already have resolved them. So we pop them
    off, record the distance, and continue. This is O(n): each index is
    pushed once and popped at most once.

THE DECREASING-ORDER INVARIANT (a picture):
    Stack stores indices whose temperatures are STRICTLY DECREASING bottom→top.

    Bottom [index0: 73]            ← warmest among stacked
           [index2: 75] is NOT allowed on top of 73; it would be resolved immediately
           ...
    Top    [index4: 69]            ← coldest among stacked

    When day 5 (72) arrives: 72 > 69 → resolve index4 (dist 5-4=1).
                             72 > 71 → resolve index3 (dist 5-3=2).
                             72 < 75 → stop; push index5.

COMMON MISTAKES (Monotonic Stack)
---------------------------------
MISTAKE 1: Storing VALUES instead of INDICES. You need the index to compute
    the distance "how many days later". Store indices; look up temps[index].

MISTAKE 2: Wrong comparison direction. For "next WARMER day", you pop while
    `temps[i] > temps[stack[-1]]` (current is warmer than stacked). If you
    wrote `<`, you'd resolve on colder days — the opposite of what you want.

MISTAKE 3: Off-by-one in distance. Distance is `i - prev_day`, NOT
    `i - prev_day - 1`. You count the days BETWEEN, inclusive of the warmer
    day's index minus the cold day's index.
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
DRY RUN: daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])
    i | temps[i] | stack before | pops?                           | result changes | stack after
    --|---------|--------------|---------------------------------|----------------|------------
    0 | 73      | []           | stack empty → no pop            | -              | [0]
    1 | 74      | [0]          | 74>73 → pop 0                   | result[0]=1    | [1]
    2 | 75      | [1]          | 75>74 → pop 1                   | result[1]=1    | [2]
    3 | 71      | [2]          | 71<75 → no pop                  | -              | [2,3]
    4 | 69      | [2,3]        | 69<71 → no pop                  | -              | [2,3,4]
    5 | 72      | [2,3,4]      | 72>69 → pop 4; 72>71 → pop 3    | r[4]=1,r[3]=2  | [2,5]
    6 | 76      | [2,5]        | 76>72 → pop 5; 76>75 → pop 2    | r[5]=1,r[2]=4  | [6]
    7 | 73      | [6]          | 73<76 → no pop                  | -              | [6,7]

    Final result: [1, 1, 4, 2, 1, 1, 0, 0]
    Indices 6 and 7 never got popped → they stay 0 (no warmer day after them).
'''


'''
ADDITIONAL PROBLEM: EVALUATE REVERSE POLISH NOTATION (LeetCode #150)
---------------------------------------------------------------------
"Evaluate a postfix expression: tokens like ["2","1","+","3","*"] → 21."

    Infix:     2 + 3          (operator between operands)
    Postfix:   2 3 +          (operator AFTER operands)  = RPN

WHY POSTFIX? No parentheses needed! The order is unambiguous.
    Infix  "(1 + 2) * 3"  vs  "1 + (2 * 3)"  → need parens.
    Postfix "1 2 + 3 *"   vs  "1 2 3 * +"   → no parens, machine unambiguous.

ALGORITHM (textbook stack use):
    - For each token:
        - If it's a NUMBER → push onto the stack.
        - If it's an OPERATOR → pop the top TWO numbers, apply the operator,
          push the result back. (Order matters for - and /!)

    - The final answer is the single value left on the stack.

    Why a stack? Because the most recently pushed operands are the ones the
    next operator should consume. An operator in postfix always applies to
    the two values immediately preceding it — which are exactly the top two
    of the stack.

STEP-BY-STEP: ["4", "13", "5", "/", "+"]
    token  | stack before | action                 | stack after
    -------|--------------|------------------------|------------
    "4"    | []           | push 4                 | [4]
    "13"   | [4]          | push 13                | [4, 13]
    "5"    | [4, 13]      | push 5                 | [4, 13, 5]
    "/"    | [4,13,5]     | pop b=5, pop a=13;     | [4, 2]
           |              | 13 / 5 = 2 (int div)   |
    "+"    | [4, 2]       | pop b=2, pop a=4;      | [6]
           |              | 4 + 2 = 6              |
    Result: 6    (which is 4 + (13/5))

NOTE THE ORDER: For "a b -" we compute a - b. We pop b FIRST (it was pushed
last), then a. Get this backwards and you'll compute b - a. This is THE
classic off-by-one-direction bug in RPN.

COMMON MISTAKES (RPN)
    1. Popping operands in the wrong order for subtraction/division.
    2. Forgetting integer division (Python // truncates toward negative
       infinity, but LeetCode wants truncation toward zero like C/Java).
    3. Not handling negative numbers when parsing tokens.
'''

def eval_rpn(tokens):
    stack = []
    for token in tokens:
        if token in "+-*/":
            b = stack.pop()   # second operand (pushed last)
            a = stack.pop()   # first operand  (pushed earlier)
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)   # a - b, NOT b - a
            elif token == '*':
                stack.append(a * b)
            else:  # '/'
                # int() truncates toward zero (like Java/C), matching LeetCode
                stack.append(int(a / b))
        else:
            stack.append(int(token))
    return stack[0]

print("\n--- Evaluate Reverse Polish Notation ---")
print(eval_rpn(["2", "1", "+", "3", "*"]))       # (2+1)*3 = 9
print(eval_rpn(["4", "13", "5", "/", "+"]))      # 4 + (13/5) = 6
print(eval_rpn(["10", "6", "9", "3", "+", "-11",
                "*", "/", "*", "17", "+", "5", "+"]))
# = 22  (the classic LeetCode example)


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

QUEUE OPERATIONS (ALL O(1) WITH deque):
    enqueue(x) — add to back    → from collections import deque; d.append(x)
    dequeue()  — remove from front → d.popleft()
    peek()     — look at front     → d[0]

In Python, use collections.deque (double-ended queue) for O(1) operations.
Do NOT use a list — list.pop(0) is O(n)!

WHY IS list.pop(0) O(n)? — A Python list is a contiguous array. Removing
the FIRST element leaves a hole at index 0, so Python must SHIFT every
remaining element one slot left: n-1 moves → O(n). A deque is a doubly-
linked structure of blocks — removing the front just re-points the head.

    Before pop(0):  [A, B, C, D, _]   After: [B, C, D, _, _]  ← O(n) shift

    deque:  head → [A] ⇄ [B] ⇄ [C] ⇄ [D] ← tail
    popleft(): head → [B] ⇄ [C] ⇄ [D]   (just re-point head). O(1).
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
5. **Producer/consumer buffers** — requests handled in arrival order
6. **Shortest path in an unweighted graph** — BFS guarantees shortest

STACK vs QUEUE — QUICK COMPARISON:
    Stack: LIFO (plates). push/pop from SAME end (top). Recent matters.
    Queue: FIFO (line). push back, pop front. Arrival order matters.

    ┌──────────────┬─────────┬──────────────────────────────┐
    │              │  Stack  │  Queue                       │
    ├──────────────┼─────────┼──────────────────────────────┤
    │ Insert at    │  top    │  back                        │
    │ Remove from  │  top    │  front                       │
    │ Order        │  LIFO   │  FIFO                        │
    └──────────────┴─────────┴──────────────────────────────┘


BFS TEMPLATE (Breadth-First Search using a queue)
-------------------------------------------------
BFS explores a graph/tree LEVEL BY LEVEL. It uses a queue to remember
"which nodes to visit next." The first node discovered is the first
visited → FIFO → queue.

    start → neighbors (level 1) → their neighbors (level 2) → ...

    Level 0:      [A]
    Level 1:   [B]   [C]
    Level 2: [D] [E]     [F]

    Queue order: A → B → C → D → E → F  (left to right, level by level)

WHY A QUEUE (not a stack) FOR BFS?
    We must process nodes in the order they were DISCOVERED so that all
    nodes at distance d are fully processed before any node at distance
    d+1. A stack would dive deep down one branch (that's DFS instead).

TEMPLATE:
    from collections import deque
    def bfs(start, neighbors_fn):
        visited = set([start])
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nb in neighbors_fn(node):
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)

Below is a concrete BFS on a small graph to find the shortest path length
between two nodes. In an UNWEIGHTED graph, BFS gives the shortest path
because it reaches closer nodes first — the first time we see a node, we
have reached it via the fewest possible edges.
'''

# A tiny graph represented as an adjacency dictionary
GRAPH = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E'],
}

def bfs_shortest_path(graph, start, target):
    """Return the fewest number of edges between start and target."""
    if start == target:
        return 0
    visited = set([start])
    queue = deque([(start, 0)])   # (node, distance_from_start)
    while queue:
        node, dist = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor == target:
                return dist + 1
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return -1  # target unreachable

print("\n--- BFS Shortest Path ---")
print("A → F steps:", bfs_shortest_path(GRAPH, 'A', 'F'))   # 2 (A→C→F)
print("A → D steps:", bfs_shortest_path(GRAPH, 'A', 'D'))   # 2 (A→B→D)
print("A → A steps:", bfs_shortest_path(GRAPH, 'A', 'A'))   # 0


'''
DRY RUN: bfs_shortest_path(GRAPH, 'A', 'F')
    [('A',0)] → pop A(0) → enqueue (B,1),(C,1)
    pop B(1) → A visited; enqueue (D,2),(E,2)
    pop C(1) → neighbor F == target → return 2
    A→F takes 2 edges (A→C→F). BFS guarantees shortest path in an unweighted
    graph because it processes nodes in order of distance.


ADDITIONAL PROBLEM: IMPLEMENT STACK USING QUEUES (LeetCode #225)
-----------------------------------------------------------------
"Design a stack using only queue operations."

    push(x): enqueue x, then rotate the queue so x is at the FRONT.
    pop():   just dequeue (the front is now the most-recently-pushed element).

WHY DOES THIS WORK? A stack's pop must return the MOST RECENTLY pushed item.
But a queue dequeues from the FRONT, where the OLDEST item lives. So after
pushing x, we cyclically shift everything that was ahead of x to BEHIND x.
Now x sits at the front, ready to be dequeued first → LIFO behavior.

    push(1): q = [1]                          front=1 (most recent)
    push(2): q = [1,2] → rotate 1 → [2,1]    front=2 (most recent) ✓
    push(3): q = [2,1,3] → rotate 2,1 → [3,2,1]  front=3 ✓
    pop():   dequeue → 3  (LIFO!)  q = [2,1]

The "rotate" moves every element EXCEPT the newly added one from front to
back, which takes O(n) per push. That's the cost of simulating LIFO with a
FIFO structure.

COMMON MISTAKES (Stack via Queues)
    1. Rotating the wrong number of times. You must rotate (size - 1) times
       AFTER appending, so the new element bubbles to the front.
    2. Forgetting that pop() now means popleft() — there's no "stack pop".
'''

class StackUsingQueue:
    def __init__(self):
        self.q = deque()

    def push(self, x):
        self.q.append(x)
        # Rotate so the new element ends up at the front
        for _ in range(len(self.q) - 1):
            self.q.append(self.q.popleft())

    def pop(self):
        return self.q.popleft()   # front is the most-recent push

    def top(self):
        return self.q[0]

    def empty(self):
        return len(self.q) == 0

print("\n--- Implement Stack Using Queues ---")
s = StackUsingQueue()
s.push(1)
s.push(2)
s.push(3)
print("top after pushes:", s.top())   # 3
print("pop:", s.pop())                # 3
print("pop:", s.pop())                # 2
print("pop:", s.pop())                # 1
print("empty?", s.empty())            # True


'''
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

MEMORY PICTURE (why pointers matter):
    RAM address:   0x10      0x24      0x08      0x3F
                   ┌────┐    ┌────┐    ┌────┐    ┌────┐
    node           │10  │    │20  │    │30  │    │40  │
                   │next│    │next│    │next│    │next│
                   └─0x24┘   └─0x08┘   └─0x3F┘   └─NULL┘

    The nodes are SCATTERED in memory. The "next" pointers are literally
    memory addresses tying them together. head = 0x10.

WHY USE A LINKED LIST INSTEAD OF AN ARRAY?
    - Inserting/deleting at the FRONT is O(1) (just change pointers)
    - No need to shift elements like in an array
    - Dynamic size (grows/shrinks without resizing)
    - BUT: no random access (can't do list[3] in O(1); must walk the chain)
    - BUT: extra memory per node for the pointer
    - BUT: poor cache locality (nodes scattered → cache misses)

    ┌─────────────┬─────────────────┬────────────────────────────┐
    │ Operation   │  Array          │  Linked List               │
    ├─────────────┼─────────────────┼────────────────────────────┤
    │ Access i-th │  O(1)           │  O(n) (walk from head)     │
    │ Insert head │  O(n) (shift)   │  O(1) (re-point)           │
    │ Insert tail │  O(1) amortized │  O(n) (or O(1) w/ tail ptr)│
    │ Delete head │  O(n) (shift)   │  O(1)                      │
    │ Memory      │  compact        │  +1 pointer per node       │
    └─────────────┴─────────────────┴────────────────────────────┘
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

# Helper used by many examples below: build a list from a Python list
def build_list(values):
    """Build 1 → 2 → 3 from [1, 2, 3]; return the head node."""
    dummy = ListNode()          # temporary "pre-head" node
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next

print("\n--- Linked List ---")
print_list(head)  # 10 → 20 → 30 → None


'''
THE MENTAL MODEL FOR LINKED LIST OPERATIONS
-------------------------------------------
The key skill is POINTER MANIPULATION. You're re-routing arrows.

The GOLDEN RULE: never lose a reference you still need.
    Before you overwrite a `next` pointer, save the old value in a temp
    variable. Once a pointer is overwritten, the node it pointed to may
    become unreachable (garbage). This is the #1 source of linked-list bugs.

INSERTING AT THE HEAD (O(1)):
    Before: head → [10] → [20] → [30] → None

    Step 1: Create new node [5]
        head → [10] → [20] → [30] → None
        [5] → None        ← new node, not yet connected

    Step 2: Point new node's next to current head
        head → [10] → [20] → [30] → None
          ↑
        [5] ─┘  (5.next = head)

    Step 3: Move head to new node
        head
          ↓
         [5] → [10] → [20] → [30] → None

    Done! Just 2 pointer changes. O(1). No shifting needed.

ORDER MATTERS: You MUST set new_node.next = head BEFORE moving head.
    If you move head first, you lose the old list! There is no array
    indexing to recover it. Pointers are your only handles.
'''

# --- INSERT AT HEAD ---
def insert_at_head(head, val):
    new_node = ListNode(val)
    new_node.next = head   # New node points to old head  (BEFORE reassigning head)
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
        head → [5] → [20] → [30] → None
                    (10 is now disconnected / garbage collected)

    Just 1 pointer change. But finding the node is O(n) because we must
    walk the chain from the head.

POINTER DIAGRAM:
        ┌────┐    ┌────┐    ┌────┐    ┌────┐
   head→│ 5  │───→│ 10 │───→│ 20 │───→│ 30 │───→ None
        └────┘    └────┘    └────┘    └────┘
          ↑                  ↑
        prev             prev.next (the target)

    After `prev.next = prev.next.next`:
        ┌────┐               ┌────┐    ┌────┐
   head→│ 5  │──────────────→│ 20 │───→│ 30 │───→ None
        └────┘               └────┘    └────┘
                  ┌────┐
                  │ 10 │   ← orphaned; Python GC reclaims it
                  └────┘

COMMON MISTAKES (Delete)
    1. Not handling the special case where the TARGET IS THE HEAD. There is
       no "previous" node before head, so you must return head.next.
    2. Overwriting prev.next before checking prev.next.val — you'd peek one
       node too far and skip the target.
    3. Infinite loop if `current` is never advanced. Always move current
       forward inside the while loop.
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
THE DUMMY HEAD TRICK (eliminates edge cases)
---------------------------------------------
When inserting or deleting, the HEAD node is annoying because it has no
"previous." Solution: create a FAKE node (dummy) that points to the real
head. Now EVERY real node — including the original head — has a "previous."

    dummy → [head] → [..] → ...

    At the end, return dummy.next (which may be a new head, or the same one).

This turns "handle head specially" into "treat head like any other node,"
removing a whole class of bugs. We used it in build_list() above and will
use it in merge_two_lists below.
'''


'''
THE THREE MOST IMPORTANT LINKED LIST PATTERNS
=============================================

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

WHY 3 POINTERS? The moment we set current.next = prev, we have BROKEN the
    forward link to the rest of the list. If we hadn't saved current.next
    in next_temp FIRST, we'd lose the rest of the list forever (the golden
    rule!). next_temp is our safety rope to the unprocessed tail.

STEP-BY-STEP POINTER DIAGRAM (reverse 1 → 2 → 3 → None):

  Initial:
    prev=None   current=[1]   [1] → [2] → [3] → None

  Iteration 1 (process [1]):
    next_temp = current.next          → next_temp = [2]    (SAVE forward link)
    current.next = prev               → [1].next = None    (REVERSE pointer)
        None  ←  [1]     [2] → [3] → None
        prev↑       current↑   next_temp↑
    prev = current                    → prev = [1]
    current = next_temp               → current = [2]
        None  ←  [1]     [2] → [3] → None
                   ↑        ↑
                 prev     current

  Iteration 2 (process [2]):
    next_temp = [3]
    current.next = prev               → [2].next = [1]
        None  ←  [1]  ←  [2]     [3] → None
        prev↑          current↑   next_temp↑
    prev = [2];  current = [3]

  Iteration 3 (process [3]):
    next_temp = None
    current.next = prev               → [3].next = [2]
        None  ←  [1]  ←  [2]  ←  [3]     None
                            prev↑   current↑  next_temp↑
    prev = [3];  current = None  → loop ends

  Return prev = [3], the new head.
  Final list:  3 → 2 → 1 → None   ✓

COMMON MISTAKES (Reverse)
    1. Saving next_temp AFTER setting current.next = prev. By then the
       forward link is gone — you've lost the rest of the list.
    2. Returning `current` instead of `prev`. When the loop ends, current
       is None; prev is the new head.
    3. Forgetting to initialize prev = None. The last node's next MUST be
       None; prev=None is what makes that happen on the first iteration.
'''

def reverse_list(head):
    prev = None
    current = head

    while current:
        next_temp = current.next   # 1. SAVE what comes after (don't lose it!)
        current.next = prev        # 2. REVERSE the pointer (point backward)
        prev = current             # 3. ADVANCE prev forward
        current = next_temp        # 4. ADVANCE current forward

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
ADDITIONAL PROBLEM: MERGE TWO SORTED LINKED LISTS (LeetCode #21)
-----------------------------------------------------------------
"Given two sorted linked lists, merge them into one sorted list."

    L1: 1 → 2 → 4
    L2: 1 → 3 → 4
    Out: 1 → 1 → 2 → 3 → 4 → 4

STRATEGY: Use a DUMMY HEAD so we never special-case the first node. Keep a
    `tail` pointer that always points at the last node of the merged list.
    Compare the two fronts; append the smaller; advance that list. When one
    list runs out, attach the remainder of the other.

WHY A DUMMY HEAD? Without it, the very first append needs a special case
    ("is `merged_head` set yet?"). The dummy absorbs that special case:
    every append — including the first — is just `tail.next = ...; tail = ...`.

POINTER DIAGRAM (merging 1→2→4 and 1→3→4):

  Start:
    dummy → ?           tail=dummy
    L1: [1] → [2] → [4]    L2: [1] → [3] → [4]

  Compare 1 vs 1 → take L1's 1 (tie-break to L1):
    dummy → [1]          tail=[1]; L1 → [2] → [4]
  Compare 2 vs 1 → take L2's 1:
    dummy → [1] → [1]    tail=[1'] ; L2 → [3] → [4]
  Compare 2 vs 3 → take L1's 2:
    dummy → [1] → [1] → [2]   tail=[2]; L1 → [4]
  Compare 4 vs 3 → take L2's 3:
    ...→ [2] → [3]            tail=[3]; L2 → [4]
  Compare 4 vs 4 → take L1's 4:
    ...→ [3] → [4]            tail=[4]; L1 = None
  L1 is None → attach L2's remainder:
    ...→ [4] → [4] → None
  Return dummy.next → head of merged list: 1 → 1 → 2 → 3 → 4 → 4

COMMON MISTAKES (Merge)
    1. Advancing the WRONG list after appending. If you took from L1, move
       L1 = L1.next; don't touch L2.
    2. Forgetting to attach the leftover list at the end. When the loop
       finishes, one list may still have nodes — splice them on wholesale.
    3. Returning the dummy instead of dummy.next.
'''

def merge_two_lists(l1, l2):
    dummy = ListNode()      # fake pre-head
    tail = dummy

    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1     # append L1's node
            l1 = l1.next
        else:
            tail.next = l2     # append L2's node
            l2 = l2.next
        tail = tail.next       # advance tail to the new last node

    # Attach any remaining nodes (at most one of these is non-None)
    tail.next = l1 if l1 is not None else l2

    return dummy.next

print("\n--- Merge Two Sorted Lists ---")
l1 = build_list([1, 2, 4])
l2 = build_list([1, 3, 4])
print("L1: ", end=""); print_list(l1)
print("L2: ", end=""); print_list(l2)
merged = merge_two_lists(l1, l2)
print("Merged: ", end=""); print_list(merged)   # 1 → 1 → 2 → 3 → 4 → 4

print("Merge empties: ", end="")
print_list(merge_two_lists(build_list([]), build_list([0])))  # 0 → None


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

WHY DOES SLOW END UP AT THE MIDDLE?
    fast travels TWICE as fast as slow. So when fast has walked the whole
    list (n nodes), slow has walked n/2 nodes — exactly the middle. This is
    a direct consequence of the 2:1 speed ratio.

USE CASE 2: Detect a CYCLE (loop)
    If there's a cycle, fast will eventually lap slow and they'll meet.
    If no cycle, fast reaches the end (None).

WHY MUST THEY MEET INSIDE A CYCLE? (the hand-waving intuition)
    Imagine slow and fast are runners on a circular track, fast moving twice
    as fast. Each lap, fast GAINS one full lap on slow... no — fast gains on
    slow by 1 step per slow-step. Concretely: once both are inside the cycle,
    the gap between them changes by ±1 each step (fast moves 2, slow moves 1,
    so the "distance from fast to slow" shrinks by 1 mod cycle-length each
    tick). Because the gap shrinks by exactly 1 each step and the cycle has
    finite length, the gap MUST hit 0 — they meet. A more rigorous proof
    notes that after slow enters the cycle, fast is at most one cycle behind
    and closes at 1 node per step, so they collide within one cycle length.

    No cycle → fast hits None first → we return False.

POINTER DIAGRAM (cycle detection on 1→2→3→4→back to 2):
    step | slow pos | fast pos | note
    -----|----------|----------|-----------------------------
      0  |   1      |   1      | both start at head
      1  |   2      |   3      | slow +1, fast +2
      2  |   3      |   2      | fast jumped 3→4→2 (cycle!)
      3  |   4      |   4      | MEET at node 4 → cycle detected

COMMON MISTAKES (Fast & Slow)
    1. Loop condition `while fast and fast.next:` — forgetting fast.next
       makes fast.next.next dereference None → AttributeError crash.
    2. Starting slow and fast at DIFFERENT nodes. For cycle detection they
       must start together; otherwise the "gap changes by 1" reasoning breaks.
    3. For middle-finding, on EVEN-length lists there are two middles; the
       standard template returns the SECOND one (slow ends one past center).
       Know which your problem wants.
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

# A normal list (no cycle) for contrast
print(has_cycle(build_list([1, 2, 3])))  # False


'''
ADDITIONAL PROBLEM: FIND THE CYCLE START NODE (LeetCode #142)
--------------------------------------------------------------
If a list has a cycle, return the node where the cycle BEGINS.

    1 → 2 → 3 → 4
            ↑       ↓
            └──←───┘
    Cycle starts at node 3.

THE TRICK (two phases):
    Phase 1: Run fast & slow pointers until they MEET (proves a cycle).
    Phase 2: Put one pointer back at the HEAD, keep the other at the MEETING
             point. Now move BOTH one step at a time. Where they meet again
             is the cycle's start.

WHY DOES PHASE 2 WORK? (the math)
    Let:
      L = distance from head to cycle start
      C = length of the cycle
      x = distance from cycle start to the meeting point (inside the cycle)

    When they meet:
      slow has traveled:  L + x
      fast has traveled:  L + x + k*C   (fast did some extra full loops)
      fast = 2 * slow  →  L + x + k*C = 2(L + x)
      →  L + x + k*C = 2L + 2x
      →  k*C = L + x
      →  L = k*C - x      ← THE KEY EQUATION

    L = k*C - x means: starting from the HEAD and walking L steps lands you
    at the cycle start. Starting from the MEETING point and walking (k*C - x)
    steps ALSO lands you at the cycle start (because k*C is full loops, and
    -x backs up to the start). So if both pointers walk one step at a time,
    one from head and one from meeting point, they meet exactly at the cycle
    start after L steps. Elegant!

COMMON MISTAKES (Cycle Start)
    1. Returning the meeting point from Phase 1 — that's NOT the cycle start.
    2. Forgetting to reset one pointer to head in Phase 2.
    3. Not handling the no-cycle case (return None).
'''

def detect_cycle_start(head):
    slow = fast = head
    has_loop = False

    # Phase 1: detect meeting point
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            has_loop = True
            break

    if not has_loop:
        return None

    # Phase 2: find cycle start
    finder = head
    while finder != slow:
        finder = finder.next
        slow = slow.next
    return slow  # this is the cycle-start node

print("\n--- Find Cycle Start ---")
# Reuse a→b→c→d→b from above (cycle starts at b, value 2)
start = detect_cycle_start(a)
print(f"Cycle starts at node value: {start.val if start else None}")  # 2

no_cycle = build_list([1, 2, 3])
print("Cycle start in acyclic list:",
      detect_cycle_start(no_cycle))  # None


'''
PATTERN 3 (BONUS): TWO POINTERS / "RUNNER" FOR NTH-FROM-END
-------------------------------------------------------------
"Remove the N-th node from the END of the list." (LeetCode #19)

    1 → 2 → 3 → 4 → 5,  n=2  →  remove 4  →  1 → 2 → 3 → 5

TRICK: Send a `fast` pointer N steps ahead. Then move `fast` and `slow`
    together until `fast` hits the end. Now `slow` is just BEFORE the node
    to remove (because fast was N ahead, so slow is N behind the end).

WHY A DUMMY HEAD HERE? If n equals the list length, we must remove the HEAD.
    The dummy gives us a "previous" before head, so the same one-line delete
    (`slow.next = slow.next.next`) works even in that case.

STEP DIAGRAM (list 1→2→3→4→5, n=2):
    dummy → [1] → [2] → [3] → [4] → [5] → None
    Phase 1: fast advances n=2 steps → fast at [2]
        dummy → [1] → [2] → [3] → [4] → [5] → None
        slow↑          fast↑
    Phase 2: move both until fast is None
        dummy → [1] → [2] → [3] → [4] → [5] → None
                            slow↑          fast↑
    slow is just before node [4] → remove it: slow.next = slow.next.next
        dummy → [1] → [2] → [3] ──────→ [5] → None
    Return dummy.next → [1].

COMMON MISTAKES (Nth from end)
    1. Advancing fast n steps but then moving both n more — off by one.
       The gap between slow and fast should be exactly n.
    2. Not using a dummy head → crash when removing the original head.
'''

def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    slow = fast = dummy

    # Phase 1: fast goes n steps ahead
    for _ in range(n):
        fast = fast.next

    # Phase 2: move both until fast hits the end
    while fast.next:
        slow = slow.next
        fast = fast.next

    # slow is right before the node to delete
    slow.next = slow.next.next
    return dummy.next

print("\n--- Remove Nth From End ---")
print("Original: ", end=""); print_list(build_list([1, 2, 3, 4, 5]))
print("Remove 2nd from end: ", end="")
print_list(remove_nth_from_end(build_list([1, 2, 3, 4, 5]), 2))  # 1→2→3→5
print("Remove 5th from end (head): ", end="")
print_list(remove_nth_from_end(build_list([1, 2, 3, 4, 5]), 5))  # 2→3→4→5


'''
PART 4: PUTTING IT TOGETHER — STACK MEETS LINKED LIST
=====================================================
A linked list with push/pop at the HEAD is itself a stack! This is exactly
how stacks are implemented under the hood in many languages. Each push is an
O(1) insert_at_head; each pop is an O(1) delete_at_head. No resizing needed.

    push 3:  head → [3] → None
    push 2:  head → [2] → [3] → None
    push 1:  head → [1] → [2] → [3] → None
    pop   :  returns 1, head → [2] → [3] → None   (LIFO!)

This connects Chapter 3's two halves: the STACK abstraction can be built on
top of a LINKED LIST — the algorithm (e.g. Valid Parentheses) is unchanged;
only the storage changes. This shows the STACK as an abstraction independent
of its implementation.
'''

class LinkedListStack:
    """A stack backed by a singly linked list. All operations O(1)."""
    class _Node:
        __slots__ = ('val', 'next')
        def __init__(self, val, next=None):
            self.val = val
            self.next = next

    def __init__(self):
        self._head = None
        self._size = 0

    def push(self, x):
        self._head = self._Node(x, self._head)   # insert at head
        self._size += 1

    def pop(self):
        if self._head is None:
            raise IndexError("pop from empty stack")
        val = self._head.val
        self._head = self._head.next             # remove head
        self._size -= 1
        return val

    def peek(self):
        return None if self._head is None else self._head.val

    def __len__(self):
        return self._size

# A tiny adapter so a Python list has push()/peek() like LinkedListStack.
class ListStackAdapter:
    def __init__(self):
        self._data = []
    def push(self, x):
        self._data.append(x)
    def pop(self):
        return self._data.pop()
    def peek(self):
        return self._data[-1] if self._data else None
    def __len__(self):
        return len(self._data)

# Reuse our earlier validator, parameterized by any stack-like object.
# Both ListStackAdapter and LinkedListStack expose push/pop/peek/__len__.
def is_valid_parentheses_with(s, stack_factory):
    stack = stack_factory()
    matching = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in '([{':
            stack.push(char)
        elif char in ')]}':
            if len(stack) == 0 or stack.peek() != matching[char]:
                return False
            stack.pop()
    return len(stack) == 0

print("\n--- Stack built on a Linked List ---")
lls = LinkedListStack()
lls.push("A"); lls.push("B"); lls.push("C")
print("peek:", lls.peek())   # C
print("pop :", lls.pop())    # C
print("pop :", lls.pop())    # B
print("size:", len(lls))     # 1

print("\n--- Valid Parentheses using LinkedListStack ---")
print(is_valid_parentheses_with("([])", LinkedListStack))        # True
print(is_valid_parentheses_with("([)]", LinkedListStack))        # False
print(is_valid_parentheses_with("((()))", LinkedListStack))      # True
print("\n--- Same algorithm, ListStackAdapter (list-backed) ---")
print(is_valid_parentheses_with("([])", ListStackAdapter))       # True
print(is_valid_parentheses_with("([)]", ListStackAdapter))       # False


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
      * Two-pointer runner: nth-from-end removal

THE GOLDEN RULE (one more time):
    Before overwriting ANY pointer, ask: "Do I still need where this points?"
    If yes, save it in a temp variable FIRST. Linked-list bugs are almost
    always lost-pointer bugs.

STACK SUMMARY:
    - LIFO; push/pop/peek/size all O(1)
    - Python list is a fine stack (append/pop at end)
    - Patterns: matching, reversing, monotonic (next greater element),
      expression evaluation (RPN)

QUEUE SUMMARY:
    - FIFO; enqueue/dequeue/peek all O(1) with collections.deque
    - NEVER use list.pop(0) — it's O(n)
    - Patterns: BFS / level-order, shortest path (unweighted), scheduling,
      sliding-window-maximum (monotonic deque)
'''

# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 3 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Stack = LIFO (plates). Push/pop from top. O(1) all operations.
   Use for: bracket matching, reversing, backtracking, monotonic stacks,
   expression evaluation (RPN). A linked list with head-push IS a stack.
2. Queue = FIFO (line). Enqueue back, dequeue front. O(1) with deque.
   Use for: BFS, level-order traversal, scheduling, shortest path.
   NEVER use list.pop(0) — it's O(n).
3. Linked List = chain of nodes with pointers. O(1) insert/delete at head.
   - Reversing: flip pointers using prev/current/next (save before overwrite!)
   - Fast & slow: find middle, detect cycles, find cycle start
   - Dummy head: eliminates head-edge-cases for insert/delete/merge
   - Two-pointer runner: nth-from-end removal
   - No random access (no arr[i] in O(1))

Golden Rule of pointers: save a temp BEFORE you overwrite, or you'll lose
the rest of the list. Nearly every linked-list bug is a lost-pointer bug.

Next: Chapter 4 — Trees, BST, Heaps & Tries
""")
