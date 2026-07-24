'''
LEETCODE #121: Best Time to Buy and Sell Stock
DIFFICULTY: Easy
TOPIC: Sliding Window

=== PROBLEM STATEMENT ===
You are given an array prices where prices[i] is the price of a given stock on
the ith day. You want to maximize your profit by choosing a single day to buy
one stock and choosing a different day in the future to sell that stock.
Return the maximum profit you can achieve. If you cannot achieve any profit,
return 0.

Example 1: Input: prices = [7,1,5,3,6,4]  Output: 5 (buy at 1, sell at 6)
Example 2: Input: prices = [7,6,5,4,3,1]  Output: 0 (no profit possible)

=== INTUITION ===
- We need max(prices[j] - prices[i]) for j > i.
- Track the minimum price seen so far as we iterate.
- At each day, compute potential profit = current_price - min_price_so_far.
- Keep the maximum profit seen.
- This is a one-pass Kadane-like / sliding-window approach.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: For each pair (buy_day, sell_day) with sell > buy, compute profit.
- Time: O(n^2)
- Space: O(1)

Approach 2: One Pass (track min price) - OPTIMAL
- Idea: Iterate; track min_price_so_far; compute profit each day; track max_profit.
- Time: O(n)
- Space: O(1)

=== DRY RUN ===
prices = [7, 1, 5, 3, 6, 4]

Initialize: min_price = infinity, max_profit = 0

Day 0: price=7
  min_price = min(inf, 7) = 7
  profit = 7 - 7 = 0; max_profit = 0
Day 1: price=1
  min_price = min(7, 1) = 1
  profit = 1 - 1 = 0; max_profit = 0
Day 2: price=5
  profit = 5 - 1 = 4; max_profit = 4
Day 3: price=3
  profit = 3 - 1 = 2; max_profit = 4
Day 4: price=6
  profit = 6 - 1 = 5; max_profit = 5
Day 5: price=4
  profit = 4 - 1 = 3; max_profit = 5

Result: max_profit = 5  CORRECT (buy at 1, sell at 6)

=== COMPLEXITY ANALYSIS ===
Time: O(n) - single pass.
Space: O(1) - two variables.

=== EDGE CASES ===
- Empty array or single element -> 0 (cannot transact).
- Strictly decreasing prices -> 0 (no profit).
- Strictly increasing prices -> last - first.
- All equal prices -> 0.
- Profit opportunity at the very end.
- Multiple equal min prices.

=== INTERVIEW TIPS ===
- The insight: track the minimum so far; profit is always relative to it.
- This is essentially Kadane's algorithm applied to daily price differences.
- Clarify: only ONE transaction allowed (buy once, sell once).
- Follow-up: Best Time to Buy and Sell Stock II (#122) - unlimited transactions.
- Follow-up: Best Time to Buy and Sell Stock III/IV - at most k transactions (DP).
- Follow-up: With cooldown / transaction fee -> state machine DP.
- Common mistake: buying and selling on the same day is not allowed (must be different days).
'''

# === SOLUTION ===
from typing import List


def maxProfit(prices: List[int]) -> int:
    """One pass: track min price and max profit. O(n) time, O(1) space."""
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        if price < min_price:
            min_price = price
        else:
            profit = price - min_price
            if profit > max_profit:
                max_profit = profit
    return max_profit


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert maxProfit([7, 1, 5, 3, 6, 4]) == 5
    # Test 2: Decreasing prices, no profit
    assert maxProfit([7, 6, 5, 4, 3, 1]) == 0
    # Test 3: Empty array
    assert maxProfit([]) == 0
    # Test 4: Single element
    assert maxProfit([5]) == 0
    # Test 5: Increasing prices
    assert maxProfit([1, 2, 3, 4, 5]) == 4
    # Test 6: All equal
    assert maxProfit([3, 3, 3, 3]) == 0
    # Test 7: Profit at the end
    assert maxProfit([2, 1, 2, 1, 0, 1, 2]) == 2
    print("All tests passed!")
