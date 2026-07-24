'''
LEETCODE #15: 3Sum
DIFFICULTY: Medium
TOPIC: Two Pointers

=== PROBLEM STATEMENT ===
Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]]
such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.

Notice that the solution set must not contain duplicate triplets.

Example 1: Input: nums = [-1,0,1,2,-1,-4]
           Output: [[-1,-1,2],[-1,0,1]]
Example 2: Input: nums = [0,1,1]   Output: []
Example 3: Input: nums = [0,0,0]   Output: [[0,0,0]]

=== INTUITION ===
- We need all unique triplets summing to zero.
- SORT the array first. Then fix one element nums[i] and use two pointers
  on the remaining suffix to find pairs that sum to -nums[i].
- Skip duplicates for the fixed element AND for the two-pointer moves to
  avoid identical triplets in the output.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: Three nested loops; use a set to dedupe triplets.
- Time: O(n^3)
- Space: O(1) (ignoring output)

Approach 2: Hash Set for the Third Element
- Idea: For each pair (i, j), check if -(nums[i]+nums[j]) exists in a set.
- Time: O(n^2)
- Space: O(n)
- Dedup is awkward.

Approach 3: Sort + Two Pointers - OPTIMAL
- Idea: Sort. For each i, run two pointers (left=i+1, right=n-1) on the suffix.
        Skip duplicate values of nums[i], nums[left], nums[right].
- Time: O(n^2)  (O(n log n) sort + O(n^2) two-pointer scan)
- Space: O(1) extra (ignoring output; sort may use O(log n) stack)

=== DRY RUN ===
nums = [-1, 0, 1, 2, -1, -4]

Step 1: Sort -> [-4, -1, -1, 0, 1, 2]

Step 2: Fix i=0, nums[i]=-4, target_sum = 4
  left=1 (-1), right=5 (2): -1+2=1 < 4 -> left++
  left=2 (-1), right=5 (2): -1+2=1 < 4 -> left++
  left=3 (0),  right=5 (2): 0+2=2  < 4 -> left++
  left=4 (1),  right=5 (2): 1+2=3  < 4 -> left++
  left=5 == right -> stop. No triplet found for i=0.

Step 3: Fix i=1, nums[i]=-1, target_sum = 1
  left=2 (-1), right=5 (2): -1+2=1 == 1 -> FOUND [-1,-1,2]
    left++, right--, skip dups
  left=3 (0), right=4 (1): 0+1=1 == 1 -> FOUND [-1,0,1]
    left++, right--, left >= right -> stop

Step 4: Fix i=2, nums[i]=-1 (duplicate of nums[1]) -> SKIP

Step 5: Fix i=3, nums[i]=0, target_sum = 0
  left=4 (1), right=5 (2): 1+2=3 > 0 -> right--
  left=4, right=4 -> stop

Result: [[-1,-1,2], [-1,0,1]]  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n^2) - outer loop O(n), inner two-pointer scan O(n).
Space: O(1) extra (output list not counted; sorting uses O(log n) stack).

=== EDGE CASES ===
- Fewer than 3 elements -> return [].
- All zeros: [0,0,0] -> [[0,0,0]]; [0,0,0,0] -> still just [[0,0,0]].
- No valid triplets -> [].
- All negative or all positive -> [] (can't sum to zero).
- Many duplicates (dedup logic is critical).
- Large input (O(n^2) is the target; avoid O(n^3)).

=== INTERVIEW TIPS ===
- SORT FIRST. This enables two pointers AND makes dedup trivial.
- Dedup at THREE places: (1) outer i loop, (2) after finding a triplet, skip
  duplicate left values, (3) skip duplicate right values.
- Explain why sorting doesn't lose solutions: triplets are unordered sets of values.
- Follow-up: 4Sum (#18) -> generalize with more pointers or recursion.
- Follow-up: 3Sum Closest (#16) -> track the closest sum to target.
- Common bug: forgetting to skip duplicates produces redundant triplets.
'''

# === SOLUTION ===
from typing import List


def threeSum(nums: List[int]) -> List[List[int]]:
    """Sort + two pointers: O(n^2) time, O(1) extra space."""
    nums.sort()
    result = []
    n = len(nums)

    for i in range(n - 2):
        # Skip duplicate fixed elements
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        # Early termination: if smallest possible triplet > 0, stop
        if nums[i] + nums[i + 1] + nums[i + 2] > 0:
            break
        # If nums[i] + two largest < 0, this i can't work, skip to next i
        if nums[i] + nums[n - 2] + nums[n - 1] < 0:
            continue

        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicate left values
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # Skip duplicate right values
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1  # need a bigger sum
            else:
                right -= 1  # need a smaller sum

    return result


# === TEST CASES ===
if __name__ == "__main__":
    def sort_outer(triplets):
        return sorted([sorted(t) for t in triplets])

    # Test 1: Classic example
    assert sort_outer(threeSum([-1, 0, 1, 2, -1, -4])) == [[-1, -1, 2], [-1, 0, 1]]
    # Test 2: No valid triplets
    assert threeSum([0, 1, 1]) == []
    # Test 3: All zeros
    assert sort_outer(threeSum([0, 0, 0])) == [[0, 0, 0]]
    # Test 4: Fewer than 3 elements
    assert threeSum([1, 2]) == []
    # Test 5: Many duplicates
    assert sort_outer(threeSum([0, 0, 0, 0])) == [[0, 0, 0]]
    # Test 6: All negative
    assert threeSum([-1, -2, -3]) == []
    # Test 7: Mixed with multiple triplets
    res = threeSum([-2, 0, 1, 1, 2])
    assert sort_outer(res) == [[-2, 0, 2], [-2, 1, 1]]
    print("All tests passed!")
