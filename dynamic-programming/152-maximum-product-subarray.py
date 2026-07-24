'''
LEETCODE #152: Maximum Product Subarray
DIFFICULTY: Medium
TOPIC: Dynamic Programming

=== PROBLEM STATEMENT ===
Given an integer array nums, find a contiguous non-empty subarray
within the array that has the largest product, and return the product.

=== INTUITION ===
A single negative number can flip min to max, so we must track BOTH
the running max and min products. At each element:
  temp_max = max(num, max_prod*num, min_prod*num)
  min_prod = min(num, max_prod*num, min_prod*num)
  max_prod = temp_max
Update global answer with max_prod.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: Try every subarray, compute product.
- Time: O(n^2)
- Space: O(1)

Approach 2: Top-Down DP (Memoization)
- Idea: Track (max, min) products ending at index i.
- Time: O(n)
- Space: O(n) for memo stack

Approach 3: Bottom-Up DP (Tabulation) — Kadane-style
- Idea: Maintain running max/min products; update in one pass.
- Time: O(n)
- Space: O(1)
'''

# === DRY RUN ===
# nums = [2,3,-2,4]
# cur_max=2, cur_min=2, result=2
# i=1 (3): temp=max(3, 2*3=6, 2*3=6)=6; min=min(3,6,6)=3; result=6
# i=2 (-2): temp=max(-2, 6*-2=-12, 3*-2=-6)=-2; min=min(-2,-12,-6)=-12; result=6
# i=3 (4): temp=max(4, -2*4=-8, -12*4=-48)=4; min=min(4,-8,-48)=-48; result=6
# Answer: 6

# === COMPLEXITY ANALYSIS ===
# Time: O(n)
# Space: O(1)

# === EDGE CASES ===
# Single element; zeros (reset running products); all negatives

# === INTERVIEW TIPS ===
# - Key insight: negatives flip min<->max; track both.
# - Common follow-up: return the subarray indices, not just the value.

# === SOLUTION ===

# Approach 1: Brute Force — O(n^2)
def maxProduct_brute(nums):
    n = len(nums)
    result = nums[0]
    for i in range(n):
        prod = 1
        for j in range(i, n):
            prod *= nums[j]
            result = max(result, prod)
    return result


# Approach 2: Top-Down DP (Memoization via recursion) — O(n)
def maxProduct_memo(nums):
    memo = {}
    n = len(nums)

    def dp(i):
        """Return (max_prod_ending_at_i, min_prod_ending_at_i)."""
        if i == 0:
            return (nums[0], nums[0])
        if i in memo:
            return memo[i]
        prev_max, prev_min = dp(i - 1)
        candidates = (nums[i], nums[i] * prev_max, nums[i] * prev_min)
        memo[i] = (max(candidates), min(candidates))
        return memo[i]

    return max(dp(i)[0] for i in range(n))


# Approach 3: Bottom-Up DP (Kadane-style) — O(n), O(1)
def maxProduct(nums):
    if not nums:
        return 0
    cur_max = cur_min = result = nums[0]
    for num in nums[1:]:
        candidates = (num, num * cur_max, num * cur_min)
        cur_max = max(candidates)
        cur_min = min(candidates)
        result = max(result, cur_max)
    return result


# === TEST CASES ===
if __name__ == "__main__":
    assert maxProduct([2, 3, -2, 4]) == 6
    assert maxProduct([-2, 0, -1]) == 0
    assert maxProduct([-2, 3, -4]) == 24
    assert maxProduct([0, 2]) == 2
    assert maxProduct([-2]) == -2
    assert maxProduct_memo([2, 3, -2, 4]) == 6
    print("All test cases passed!")
