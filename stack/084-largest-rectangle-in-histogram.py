'''
LEETCODE #84: Largest Rectangle in Histogram
DIFFICULTY: Hard
TOPIC: Stack (Monotonic Stack)

=== PROBLEM STATEMENT ===
Given an array of integers heights representing the histogram's bar heights
where the width of each bar is 1, return the area of the largest rectangle that
can be formed within the histogram.

=== INTUITION ===
1. The largest rectangle using bar i as the shortest bar extends left and right
   as far as the bars are >= heights[i]. So for each i we need the FIRST bar
   shorter than it on the left (left_bound) and on the right (right_bound).
2. Rectangle area with bar i as the shortest = heights[i] * (right_bound - left_bound - 1).
3. A MONOTONIC INCREASING stack finds these bounds efficiently. When we encounter
   a bar shorter than the stack top, the stack top's right bound is the current
   index, and its left bound is the new stack top after popping.
4. Trick: append a sentinel 0 at the end so all bars get resolved.

=== APPROACHES ===
Approach 1: Brute Force
- For each bar, expand left and right while bars >= height.
- Time: O(n^2), Space: O(1)

Approach 2: Monotonic Increasing Stack (Optimal)
- Maintain stack of indices with increasing heights. On a shorter bar, pop and
  compute area using current index as right bound and new stack top as left bound.
- Time: O(n), Space: O(n)

=== DRY RUN ===
heights = [2,1,5,6,2,3]
Append sentinel 0 -> process [2,1,5,6,2,3,0]

i  h  stack(before) action
0  2  []            stack empty -> push. stack=[0]
1  1  [0]           1 < heights[0]=2 -> pop 0: area = 2*(1-(-1)-1) = 2*1 = 2
                    stack empty -> push 1. stack=[1]
2  5  [1]           5 >= 1 -> push. stack=[1,2]
3  6  [1,2]         6 >= 5 -> push. stack=[1,2,3]
4  2  [1,2,3]       2 < 6 -> pop 3: area = 6*(4-2-1) = 6*1 = 6
                    2 < 5 -> pop 2: area = 5*(4-1-1) = 5*2 = 10
                    2 >= 1 -> push. stack=[1,4]
5  3  [1,4]         3 >= 2 -> push. stack=[1,4,5]
6  0  [1,4,5]       0 < 3 -> pop 5: area = 3*(6-4-1) = 3*1 = 3
                    0 < 2 -> pop 4: area = 2*(6-1-1) = 2*4 = 8
                    0 < 1 -> pop 1: area = 1*(6-(-1)-1) = 1*6 = 6
Max area = 10

=== COMPLEXITY ANALYSIS ===
Time: O(n) — each index pushed and popped at most once.
Space: O(n) for the stack.

=== EDGE CASES ===
- Empty array -> 0.
- All equal heights [3,3,3] -> 3*3 = 9.
- Strictly increasing [1,2,3,4] -> max is 4 (single bar) or 2*3=6, etc.
- Single bar [7] -> 7.
- Very tall single bar.

=== INTERVIEW TIPS ===
- This is THE classic hard stack problem. Master it.
- The sentinel 0 at the end elegantly forces the stack to fully drain.
- Explain left_bound = stack[-1] AFTER popping (the bar still on the stack is
  the first one strictly shorter than the popped bar on the left).
- right_bound = current index i (the first bar strictly shorter on the right).
- Width = right_bound - left_bound - 1.
- Related: Maximal Rectangle (LC #85) builds on this; Trapping Rain Water uses a
  similar monotonic-stack idea but for a different objective.
'''

# === SOLUTION ===
def largestRectangleArea(heights: list[int]) -> int:
    stack = []   # indices, with heights[stack[i]] monotonically increasing
    max_area = 0

    for i, h in enumerate(heights + [0]):  # sentinel forces final drainage
        # Pop all bars taller than the current bar; resolve their rectangles.
        while stack and heights[stack[-1]] > h:
            popped_idx = stack.pop()
            height = heights[popped_idx]
            # Left bound is the new top of stack (-1 if empty).
            left_bound = stack[-1] if stack else -1
            width = i - left_bound - 1
            max_area = max(max_area, height * width)
        stack.append(i)

    return max_area


# === TEST CASES ===
if __name__ == "__main__":
    assert largestRectangleArea([2,1,5,6,2,3]) == 10
    assert largestRectangleArea([2,4]) == 4
    assert largestRectangleArea([1]) == 1
    assert largestRectangleArea([0]) == 0
    assert largestRectangleArea([3,3,3,3]) == 12
    assert largestRectangleArea([1,2,3,4,5]) == 9   # heights[2..4] = 3*3 = 9
    print("All test cases passed.")
