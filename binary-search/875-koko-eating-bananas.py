'''
LEETCODE #875: Koko Eating Bananas
DIFFICULTY: Medium
TOPIC: Binary Search

=== PROBLEM STATEMENT ===
Koko loves to eat bananas. There are n piles of bananas, the i-th pile has
piles[i] bananas. The guards have gone and will come back in h hours.

Koko can decide her bananas-per-hour eating speed of k. Each hour, she
chooses some pile of bananas and eats k bananas from that pile. If the pile
has less than k bananas, she eats all of them and will not eat any more
bananas during that hour.

Koko likes to eat slowly but still wants to finish eating all the bananas
before the guards return.

Return the minimum integer k such that she can eat all the bananas within
h hours.

=== INTUITION ===
This is binary search on the ANSWER (the eating speed k), not on the array.
- The minimum possible speed is 1 (one banana per hour).
- The maximum possible speed is max(piles) (eating the largest pile in one
  hour — going faster yields no benefit since each pile takes at least 1 hour).

For any given speed k, we can compute the total hours needed in O(n) time.
Then we binary search the range [1, max(piles)] to find the smallest k
where total hours <= h.

This "binary search on the answer" pattern is extremely powerful for
min-max optimization problems.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: Try every speed from 1 to max(piles) and return the first that works.
- Time: O(n * max(piles)) — potentially huge.
- Space: O(1)

Approach 2: Optimal — Binary Search on the Answer
- Idea: Binary search the speed range [1, max(piles)].
- Time: O(n * log(max(piles)))
- Space: O(1)

=== DRY RUN ===
piles = [3, 6, 7, 11], h = 8

Search range for k: [1, 11]

Step 1: left=1, right=11, mid=6
        hours = ceil(3/6) + ceil(6/6) + ceil(7/6) + ceil(11/6)
              = 1 + 1 + 2 + 2 = 6 <= 8 => try slower
        right = 6

Step 2: left=1, right=6, mid=3
        hours = ceil(3/3)+ceil(6/3)+ceil(7/3)+ceil(11/3)
              = 1 + 2 + 3 + 4 = 10 > 8 => too slow
        left = 4

Step 3: left=4, right=6, mid=5
        hours = ceil(3/5)+ceil(6/5)+ceil(7/5)+ceil(11/5)
              = 1 + 2 + 2 + 3 = 8 <= 8 => try slower
        right = 5

Step 4: left=4, right=5, mid=4
        hours = ceil(3/4)+ceil(6/4)+ceil(7/4)+ceil(11/4)
              = 1 + 2 + 2 + 3 = 8 <= 8 => try slower
        right = 4

Loop exits: left=4, right=4 => return 4

Output: 4

=== COMPLEXITY ANALYSIS ===
Time: O(n * log(max(piles))) — binary search over range max(piles), each
      check costs O(n).
Space: O(1)

=== EDGE CASES ===
- h == len(piles): must eat one pile per hour -> speed must be max(piles)
- h very large: speed of 1 may suffice
- Single pile
- All piles same size
- Very large pile values (need ceil division without floating point issues)

=== INTERVIEW TIPS ===
- Recognize "binary search on the answer" pattern: whenever the problem asks
  to minimize/maximize a value and you can check feasibility of a candidate
  in O(n), binary search is likely the answer.
- The ceil division trick: ceil(a/b) = (a + b - 1) // b for positive integers.
  Avoids floating-point precision issues with math.ceil(a/b).
- Follow-up: what if speeds could be fractional? (Doesn't change the answer
  much, but worth discussing.)
'''

# === SOLUTION ===
import math
from typing import List


def minEatingSpeed(piles: List[int], h: int) -> int:
    """Find minimum integer eating speed to finish within h hours."""
    # The search range for speed k is [1, max(piles)].
    left, right = 1, max(piles)

    while left < right:
        mid = left + (right - left) // 2

        # Compute total hours needed at speed `mid`.
        total_hours = 0
        for pile in piles:
            # ceil(pile / mid) without floating-point issues.
            total_hours += (pile + mid - 1) // mid

        if total_hours <= h:
            # Feasible at this speed — try slower (smaller k).
            right = mid
        else:
            # Too slow — need a faster speed.
            left = mid + 1

    return left


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: standard case
    assert minEatingSpeed([3, 6, 7, 11], 8) == 4
    # Test 2: tight hours
    assert minEatingSpeed([30, 11, 23, 4, 20], 5) == 30
    # Test 3: generous hours
    assert minEatingSpeed([30, 11, 23, 4, 20], 6) == 23
    # Test 4: single pile
    assert minEatingSpeed([1], 1) == 1
    # Test 5: all piles equal, tight hours
    assert minEatingSpeed([3, 3, 3, 3], 4) == 3
    # Test 6: very generous hours
    assert minEatingSpeed([1000000000], 2) == 500000000
    print("All tests passed!")
