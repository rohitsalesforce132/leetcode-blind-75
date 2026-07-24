'''
LEETCODE #217: Contains Duplicate
DIFFICULTY: Easy
TOPIC: Arrays & Hashing

=== PROBLEM STATEMENT ===
Given an integer array nums, return true if any value appears at least twice
in the array, and false if every element is distinct.

Example 1: Input: nums = [1,2,3,1]     Output: true
Example 2: Input: nums = [1,2,3,4]     Output: false
Example 3: Input: nums = [1,1,1,3,3,4,3,2,4,2]  Output: true

=== INTUITION ===
- We only need a boolean: does any value repeat?
- The moment we see a value we've already recorded, return True.
- A hash set gives O(1) membership checks.
- Alternatively, sorting brings duplicates adjacent for an O(1)-space scan.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: For each pair (i, j), check if nums[i] == nums[j].
- Time: O(n^2)
- Space: O(1)

Approach 2: Hash Set - OPTIMAL for time
- Idea: Iterate; if num in set, return True; else add to set.
- Time: O(n)
- Space: O(n)

Approach 3: Sorting
- Idea: Sort, then check adjacent elements for equality.
- Time: O(n log n)
- Space: O(1) or O(n) depending on sort implementation
- Useful when memory is extremely constrained.

Approach 4: Set Length Comparison
- Idea: return len(nums) != len(set(nums))
- Time: O(n)
- Space: O(n)
- Concise but always scans the entire array (no early exit).

=== DRY RUN ===
nums = [1, 2, 3, 1]

Step 1: num=1, seen={} -> 1 not in seen -> seen={1}
Step 2: num=2, seen={1} -> 2 not in seen -> seen={1,2}
Step 3: num=3, seen={1,2} -> 3 not in seen -> seen={1,2,3}
Step 4: num=1, seen={1,2,3} -> 1 IS in seen -> return True

Result: True  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - single pass; each set operation is O(1) amortized.
Space: O(n) - worst case all elements distinct, set holds n items.

=== EDGE CASES ===
- Empty array -> False (no duplicates possible).
- Single element -> False.
- All elements identical -> True (caught on 2nd element).
- Very large array with all distinct elements (memory stress).
- Array of negative numbers / zeros.

=== INTERVIEW TIPS ===
- Lead with the hash set approach; mention early-exit advantage over len() trick.
- Offer sorting approach when asked for O(1) space.
- Follow-up: Contains Duplicate II (within distance k) -> sliding window / set of size k.
- Follow-up: Contains Duplicate III (value within t, index within k) -> buckets/balanced BST.
- Discuss hash collision worst case (O(n) per op) but note amortized O(1) in practice.
'''

# === SOLUTION ===
from typing import List


def containsDuplicate(nums: List[int]) -> bool:
    """Hash set with early exit on first duplicate."""
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False


def containsDuplicate_sorting(nums: List[int]) -> bool:
    """O(1) extra space alternative (sort in place)."""
    nums.sort()
    for i in range(1, len(nums)):
        if nums[i] == nums[i - 1]:
            return True
    return False


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Duplicate present
    assert containsDuplicate([1, 2, 3, 1]) is True
    # Test 2: All distinct
    assert containsDuplicate([1, 2, 3, 4]) is False
    # Test 3: Multiple duplicates
    assert containsDuplicate([1, 1, 1, 3, 3, 4, 3, 2, 4, 2]) is True
    # Test 4: Empty array
    assert containsDuplicate([]) is False
    # Test 5: Single element
    assert containsDuplicate([5]) is False
    # Test 6: Negative duplicates
    assert containsDuplicate([-1, -2, -3, -1]) is True
    print("All tests passed!")
