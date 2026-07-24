'''
LEETCODE #11: Container With Most Water
DIFFICULTY: Medium
TOPIC: Two Pointers

=== PROBLEM STATEMENT ===
You are given an integer array height of length n. There are n vertical lines
drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).
Find two lines that together with the x-axis form a container, such that the
container contains the most water. Return the maximum amount of water a
container can hold.

Example 1: Input: height = [1,8,6,2,5,4,8,3,7]  Output: 49
Example 2: Input: height = [1,1]                Output: 1

=== INTUITION ===
- Area between two lines at indices i and j = min(height[i], height[j]) * (j - i).
- We want to MAXIMIZE this area.
- Start with the widest container (left=0, right=n-1).
- The limiting factor is the SHORTER line. Moving the taller pointer inward can
  only decrease or keep width the same while height is still capped by the shorter
  line - so area can't improve. Move the SHORTER pointer inward to potentially
  find a taller line that increases the height.
- This greedy two-pointer approach finds the optimal in O(n).

=== APPROACHES ===
Approach 1: Brute Force
- Idea: Check every pair (i, j); compute area; track max.
- Time: O(n^2)
- Space: O(1)

Approach 2: Two Pointers - OPTIMAL
- Idea: left=0, right=n-1. Compute area. Move the shorter pointer inward.
        Rationale: moving the taller pointer can't help (height capped by shorter).
- Time: O(n)
- Space: O(1)

=== DRY RUN ===
height = [1, 8, 6, 2, 5, 4, 8, 3, 7]
indices:  0  1  2  3  4  5  6  7  8

left=0, right=8: area = min(1,7)*(8-0) = 1*8 = 8.  max_area=8.
  height[0]=1 < height[8]=7 -> move left (shorter)
left=1, right=8: area = min(8,7)*(8-1) = 7*7 = 49. max_area=49.
  height[1]=8 > height[8]=7 -> move right (shorter)
left=1, right=7: area = min(8,3)*(7-1) = 3*6 = 18. max_area=49.
  height[1]=8 > height[7]=3 -> move right
left=1, right=6: area = min(8,8)*(6-1) = 8*5 = 40. max_area=49.
  equal heights; move either (say left)
left=2, right=6: area = min(6,8)*(6-2) = 6*4 = 24. max_area=49.
  height[2]=6 < height[6]=8 -> move left
left=3, right=6: area = min(2,8)*(6-3) = 2*3 = 6. max_area=49.
  move left
left=4, right=6: area = min(5,8)*(6-4) = 5*2 = 10. max_area=49.
  move left
left=5, right=6: area = min(4,8)*(6-5) = 4*1 = 4. max_area=49.
  move left
left=6, right=6 -> stop (left >= right)

Result: max_area = 49  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - each pointer moves at most n steps.
Space: O(1) - only a few variables.

=== EDGE CASES ===
- Two elements only (minimum container).
- All heights equal -> area depends only on width.
- Strictly increasing or decreasing heights.
- Very large n (O(n) is essential).
- One very tall line among short ones.
- Plateau (many equal heights in the middle).

=== INTERVIEW TIPS ===
- The key insight: moving the SHORTER line inward is the only way to potentially
  improve area. Moving the taller line can never help. Explain this clearly.
- Area formula: min(h[l], h[r]) * (r - l). Width shrinks as pointers move in.
- This is a classic "greedy two-pointer" problem; interviewers love the proof of correctness.
- Follow-up: Trapping Rain Water (#42) is a related but different problem (uses stacks/DP).
- Common mistake: moving both pointers or moving the taller one. Only move the shorter.
'''

# === SOLUTION ===
from typing import List


def maxArea(height: List[int]) -> int:
    """Two-pointer greedy: O(n) time, O(1) space."""
    left, right = 0, len(height) - 1
    max_area = 0
    while left < right:
        # Area = shorter height * width
        area = min(height[left], height[right]) * (right - left)
        max_area = max(max_area, area)
        # Move the shorter pointer inward
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_area


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    # Test 2: Two elements
    assert maxArea([1, 1]) == 1
    # Test 3: Increasing heights
    assert maxArea([1, 2, 3, 4, 5]) == 6  # min(4,5)*2=8? check: pairs...
    # Test 4: Decreasing heights
    assert maxArea([5, 4, 3, 2, 1]) == 6
    # Test 5: All equal
    assert maxArea([3, 3, 3, 3]) == 9
    # Test 6: One tall among short
    assert maxArea([1, 2, 1]) == 2
    print("All tests passed!")
