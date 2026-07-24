'''
LEETCODE #42: Trapping Rain Water
DIFFICULTY: Hard
TOPIC: Two Pointers

=== PROBLEM STATEMENT ===
Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Example 1: Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]  Output: 6
Example 2: Input: height = [4,2,0,3,2,5]              Output: 9

=== INTUITION ===
- Water trapped above position i = min(max_left[i], max_right[i]) - height[i]
  (if positive, else 0).
- max_left[i] = tallest bar to the left of i (including i).
- max_right[i] = tallest bar to the right of i (including i).
- The water level at i is determined by the shorter of the two tallest walls
  bounding it from left and right.
- Two-pointer optimization: we don't need full arrays. Track left_max and
  right_max as we move pointers from both ends.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: For each i, scan left and right to find max_left and max_right.
- Time: O(n^2)
- Space: O(1)

Approach 2: Dynamic Programming (prefix/suffix max arrays)
- Idea: Precompute max_left[] and max_right[] in O(n); then compute water per i.
- Time: O(n)
- Space: O(n)

Approach 3: Two Pointers - OPTIMAL
- Idea: left=0, right=n-1. Track left_max and right_max. Move the pointer on the
        side with the smaller max, because that side limits the water level.
- Time: O(n)
- Space: O(1)

Approach 4: Monotonic Stack
- Idea: Use a stack of indices; pop when a taller bar is found, computing trapped
        water in the "valleys".
- Time: O(n)
- Space: O(n)

=== DRY RUN ===
height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]

Two-pointer approach:
left=0, right=11, left_max=0, right_max=0, water=0

  height[0]=0 <= height[11]=1:
    left_max = max(0, 0) = 0; water += 0 - 0 = 0; left=1
  height[1]=1 <= height[11]=1:
    left_max = max(0, 1) = 1; water += 1 - 1 = 0; left=2
  height[2]=0 <= height[11]=1:
    left_max = 1; water += 1 - 0 = 1; left=3  (water=1)
  height[3]=2 > height[11]=1:
    right_max = max(0, 1) = 1; water += 1 - 1 = 0; right=10
  height[3]=2 > height[10]=2:
    right_max = max(1, 2) = 2; water += 2 - 2 = 0; right=9
  height[3]=2 > height[9]=1:
    right_max = 2; water += 2 - 1 = 1; right=8  (water=2)
  height[3]=2 <= height[8]=2:
    left_max = max(1, 2) = 2; water += 2 - 2 = 0; left=4
  height[4]=1 <= height[8]=2:
    left_max=2; water += 2 - 1 = 1; left=5  (water=3)
  height[5]=0 <= height[8]=2:
    water += 2 - 0 = 2; left=6  (water=5)
  height[6]=1 <= height[8]=2:
    water += 2 - 1 = 1; left=7  (water=6)
  height[7]=3 > height[8]=2:
    right_max = max(2, 2) = 2; water += 2 - 2 = 0; right=7
  left=7, right=7 -> stop

Result: water = 6  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - single pass with two pointers.
Space: O(1) - only constant extra variables.

=== EDGE CASES ===
- Fewer than 3 bars -> can't trap water -> 0.
- Flat terrain (all equal heights) -> 0.
- Strictly increasing or decreasing -> 0 (no valleys).
- Single tall bar in the middle -> traps water on both sides.
- All zeros -> 0.
- Very large input (O(n) essential).

=== INTERVIEW TIPS ===
- This is a Hard problem; impress by giving the O(1)-space two-pointer solution.
- Explain the water level formula: min(max_left, max_right) - height[i].
- The two-pointer trick: process the side with the smaller max first, because
  that's the limiting wall and its max is already final.
- Mention the DP (prefix/suffix arrays) approach as the stepping stone to the
  two-pointer optimization.
- Stack approach is another valid O(n) solution; good to know for variety.
- Follow-up: Trapping Rain Water II (3D version) -> BFS/priority queue.
'''

# === SOLUTION ===
from typing import List


def trap(height: List[int]) -> int:
    """Two-pointer approach: O(n) time, O(1) space."""
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            # Left side is the limiting wall
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            # Right side is the limiting wall
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water


def trap_dp(height: List[int]) -> int:
    """DP with prefix/suffix max arrays: O(n) time, O(n) space."""
    if not height:
        return 0
    n = len(height)
    left_max = [0] * n
    right_max = [0] * n
    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])
    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])
    water = 0
    for i in range(n):
        water += min(left_max[i], right_max[i]) - height[i]
    return water


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    # Test 2: Another example
    assert trap([4, 2, 0, 3, 2, 5]) == 9
    # Test 3: Fewer than 3 bars
    assert trap([1, 2]) == 0
    # Test 4: Empty
    assert trap([]) == 0
    # Test 5: Single peak
    assert trap([3, 0, 3]) == 3
    # Test 6: Increasing (no valleys)
    assert trap([1, 2, 3, 4]) == 0
    # Test 7: All zeros
    assert trap([0, 0, 0]) == 0
    # Verify DP approach matches
    assert trap_dp([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    print("All tests passed!")
