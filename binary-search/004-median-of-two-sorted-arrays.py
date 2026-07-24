'''
LEETCODE #4: Median of Two Sorted Arrays
DIFFICULTY: Hard
TOPIC: Binary Search

=== PROBLEM STATEMENT ===
Given two sorted arrays nums1 and nums2 of sizes m and n respectively,
return the median of the two sorted arrays.

The overall run time complexity should be O(log (m+n)).

=== INTUITION ===
The median is the value that splits the combined array into two equal halves.
Instead of merging (O(m+n)), we binary search on the SMALLER array to find
a partition point such that:

- Elements in the left partition (from both arrays) are all <= elements in
  the right partition.
- The left partition has exactly (or one more than) half the total elements.

Let A be the smaller array. We binary search `i` = number of elements taken
from A in the left partition. Then j = (m + n + 1) // 2 - i is the number
of elements taken from B.

We check four boundary elements:
  maxLeftA = A[i-1]    minRightA = A[i]
  maxLeftB = B[j-1]    minRightB = B[j]

Valid partition when:
  maxLeftA <= minRightB  and  maxLeftB <= minRightA

If maxLeftA > minRightB: i is too big, search left (right = i - 1).
Else: i is too small, search right (left = i + 1).

=== APPROACHES ===
Approach 1: Brute Force — Merge and Find Median
- Idea: Merge both arrays into a single sorted array, then compute median.
- Time: O(m + n)
- Space: O(m + n)

Approach 2: Optimal — Binary Search on Partition
- Idea: Binary search on the smaller array to find the correct partition.
- Time: O(log(min(m, n)))
- Space: O(1)

=== DRY RUN ===
nums1 = [1, 3], nums2 = [2]
A = [2] (smaller, m=1), B = [1, 3] (larger, n=2), total = 3

Search range for i (partition of A): [0, 1]

Step 1: left=0, right=1, i=0, j = (1+2+1)//2 - 0 = 2
        maxLeftA = -inf (A[-1]), minRightA = A[0] = 2
        maxLeftB = B[1] = 3,     minRightB = +inf (B[2])
        maxLeftA (-inf) <= minRightB (+inf)? Yes
        maxLeftB (3) <= minRightA (2)? No => i too small, left = i+1 = 1

Step 2: left=1, right=1, i=1, j = 2 - 1 = 1
        maxLeftA = A[0] = 2, minRightA = +inf
        maxLeftB = B[0] = 1, minRightB = B[1] = 3
        maxLeftA (2) <= minRightB (3)? Yes
        maxLeftB (1) <= minRightA (+inf)? Yes => valid partition!
        total=3 (odd) => median = max(maxLeftA, maxLeftB) = max(2, 1) = 2

Output: 2.0

=== COMPLEXITY ANALYSIS ===
Time: O(log(min(m, n)))
Space: O(1)

=== EDGE CASES ===
- One array is empty
- Arrays don't overlap (e.g., [1, 2] and [3, 4])
- Arrays fully overlap (e.g., [1, 2] and [1, 2])
- Total length odd vs even
- All elements of one array are smaller/larger than the other
- Single-element arrays

=== INTERVIEW TIPS ===
- This is one of the hardest Blind 75 problems. Don't panic if you can't
  derive it from scratch — it's more important to know the pattern and
  explain the partition logic clearly.
- Always binary search on the SMALLER array to guarantee O(log(min(m,n)))
  and avoid index-out-of-bounds on j.
- Use float('-inf') and float('inf') for boundary elements to handle edge
  cases where i=0 or i=m cleanly.
- Draw the partition on paper: visualize left-partition and right-partition
  elements from both arrays.
- Follow-up: How would you generalize to find the k-th element of two sorted
  arrays? (Same binary search on partition, but targeting the k-th element.)
'''

# === SOLUTION ===
from typing import List


def findMedianSortedArrays(nums1: List[int], nums2: List[int]) -> float:
    """Find median of two sorted arrays in O(log(min(m,n))) time."""
    # Ensure A is the smaller array for optimal complexity.
    if len(nums1) <= len(nums2):
        A, B = nums1, nums2
    else:
        A, B = nums2, nums1

    m, n = len(A), len(B)
    total = m + n
    half = (total + 1) // 2  # left partition size (larger if odd)

    left, right = 0, m

    while True:
        # i = elements from A in left partition, j = elements from B.
        i = (left + right) // 2
        j = half - i

        # Boundary elements (use infinities for out-of-bounds).
        maxLeftA = A[i - 1] if i > 0 else float('-inf')
        minRightA = A[i] if i < m else float('inf')
        maxLeftB = B[j - 1] if j > 0 else float('-inf')
        minRightB = B[j] if j < n else float('inf')

        # Check if this is a valid partition.
        if maxLeftA <= minRightB and maxLeftB <= minRightA:
            # Found the correct partition.
            if total % 2 == 1:
                # Odd total: median is the max of the left partition.
                return float(max(maxLeftA, maxLeftB))
            else:
                # Even total: median is average of max-left and min-right.
                return (max(maxLeftA, maxLeftB) + min(minRightA, minRightB)) / 2.0
        elif maxLeftA > minRightB:
            # i is too big: took too many from A, move left.
            right = i - 1
        else:
            # i is too small: need to take more from A.
            left = i + 1


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: odd total
    assert findMedianSortedArrays([1, 3], [2]) == 2.0
    # Test 2: even total
    assert findMedianSortedArrays([1, 2], [3, 4]) == 2.5
    # Test 3: one empty
    assert findMedianSortedArrays([], [1]) == 1.0
    # Test 4: no overlap, even total
    assert findMedianSortedArrays([1, 2], [3, 4]) == 2.5
    # Test 5: identical arrays
    assert findMedianSortedArrays([1, 2], [1, 2]) == 1.5
    # Test 6: one single element each
    assert findMedianSortedArrays([1], [2]) == 1.5
    # Test 7: one much larger array
    assert findMedianSortedArrays([1], [2, 3, 4, 5, 6]) == 3.5
    print("All tests passed!")
