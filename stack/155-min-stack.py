'''
LEETCODE #155: Min Stack
DIFFICULTY: Medium
TOPIC: Stack

=== PROBLEM STATEMENT ===
Design a stack that supports push, pop, top, and retrieving the minimum element
in O(1) time.

Implement the MinStack class:
- push(val): push element val onto stack.
- pop(): remove the element on top of the stack.
- top(): get the top element.
- getMin(): retrieve the minimum element in the stack.

=== INTUITION ===
1. We need getMin in O(1). Scanning is O(n). Sorting destroys order. We must
   STORE the current min in a way that's instantly accessible.
2. Key idea: maintain a SECOND stack ("min_stack") that tracks the running min.
   Every time we push to the main stack, we also push max(new_val, current_min)
   (or, equivalently, push the value that becomes the new min).
3. When we pop, both stacks pop together, so min_stack's top always reflects the
   min of the remaining elements.

=== APPROACHES ===
Approach 1: Two Stacks
- Idea: main stack stores values; min_stack[i] = min of main[0..i].
- Time: O(1) all operations. Space: O(n).

Approach 2: Single Stack with (val, current_min) tuples
- Idea: store pairs so one stack suffices. Same complexity, slightly cleaner.

Approach 3: One stack, constant extra space (diff trick)
- Idea: encode diffs when new min is set. Complex; rarely worth it in interviews.

=== DRY RUN ===
push(5):  main=[5],    min_stack=[5]
push(3):  main=[5,3],  min_stack=[5,3]    (3 < 5, so 3 is new min)
push(7):  main=[5,3,7],min_stack=[5,3,3]  (7 >= 3, push current min 3)
top()  -> 7
getMin()-> 3
pop():   main=[5,3],  min_stack=[5,3]
getMin()-> 3
pop():   main=[5],    min_stack=[5]
getMin()-> 5

=== COMPLEXITY ANALYSIS ===
Time: O(1) for push, pop, top, getMin.
Space: O(n).

=== EDGE CASES ===
- Pop on empty (problem guarantees it won't happen, but mention it).
- Pushing equal values: must still push to min_stack to keep counts correct.
- Single element: that element is the min.
- Descending sequence 5,4,3,2,1: min_stack mirrors main.

=== INTERVIEW TIPS ===
- State the tradeoff: we trade space for time. O(2n) space is acceptable.
- Mention the tuple variant as a cleaner one-stack alternative.
- Follow-up: Max Stack (LC #716) — same technique.
- Discuss the constant-space diff-encoding trick only if asked.
'''

# === SOLUTION ===
class MinStack:
    def __init__(self):
        self.stack = []      # main data stack
        self.min_stack = []  # parallel stack tracking running minimum

    def push(self, val: int) -> None:
        self.stack.append(val)
        # min_stack top is the min of everything currently in the stack.
        if self.min_stack:
            self.min_stack.append(min(val, self.min_stack[-1]))
        else:
            self.min_stack.append(val)

    def pop(self) -> None:
        self.stack.pop()
        self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]


# === TEST CASES ===
if __name__ == "__main__":
    ms = MinStack()
    ms.push(-2); ms.push(0); ms.push(-3)
    assert ms.getMin() == -3
    ms.pop()
    assert ms.top() == 0
    assert ms.getMin() == -2

    ms2 = MinStack()
    ms2.push(5); ms2.push(3); ms2.push(7)
    assert ms2.top() == 7
    assert ms2.getMin() == 3
    ms2.pop()
    assert ms2.getMin() == 3
    ms2.pop()
    assert ms2.getMin() == 5
    print("All test cases passed.")
