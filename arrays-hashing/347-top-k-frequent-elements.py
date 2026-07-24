'''
LEETCODE #347: Top K Frequent Elements
DIFFICULTY: Medium
TOPIC: Arrays & Hashing

=== PROBLEM STATEMENT ===
Given an integer array nums and an integer k, return the k most frequent
elements. You may return the answer in any order.

Example 1: Input: nums = [1,1,1,2,2,3], k = 2  Output: [1,2]
Example 2: Input: nums = [1], k = 1            Output: [1]

Constraints: 1 <= nums.length <= 10^5, -10^4 <= nums[i] <= 10^4
k is in the range [1, number of unique elements].
It is guaranteed that the answer is unique.

=== INTUITION ===
- First, count frequencies with a hash map: O(n).
- Then we need the top-k by frequency. Three strategies:
  (a) Sort by frequency and take top k           -> O(n log n)
  (b) Use a min-heap of size k                   -> O(n log k)
  (c) Bucket sort by frequency (max freq <= n)   -> O(n)
- Bucket sort is optimal because frequencies range from 1 to n.

=== APPROACHES ===
Approach 1: Sorting
- Idea: Count frequencies, sort items by freq descending, take first k.
- Time: O(n log n)
- Space: O(n)

Approach 2: Min-Heap of Size k
- Idea: Keep a heap of the k most frequent; push all, pop smallest when size > k.
        Use heapq.nlargest(k, items, key=lambda x: x[1]).
- Time: O(n log k)
- Space: O(n)

Approach 3: Bucket Sort - OPTIMAL
- Idea: freq_map gives element->count. Create buckets indexed by frequency
        (bucket[i] = list of elements appearing exactly i times). Scan buckets
        from high to low, collecting k elements.
- Time: O(n)
- Space: O(n)

=== DRY RUN ===
nums = [1,1,1,2,2,3], k = 2

Step 1: Count frequencies
  freq = {1: 3, 2: 2, 3: 1}

Step 2: Build buckets (index = frequency)
  bucket[3] = [1]
  bucket[2] = [2]
  bucket[1] = [3]

Step 3: Scan buckets from high freq to low, collect k=2 elements
  freq=3: add 1  -> result = [1], count=1
  freq=2: add 2  -> result = [1, 2], count=2  -> done (count == k)

Result: [1, 2]  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - counting O(n), building buckets O(n), collecting k <= n items O(n).
Space: O(n) - frequency map + bucket array of size n+1.

=== EDGE CASES ===
- k = 1: return the single most frequent element.
- k equals number of unique elements: return all unique elements.
- All elements identical: only one unique element, k must be 1.
- All elements distinct: every frequency is 1, return any k.
- Large array with skewed frequencies.

=== INTERVIEW TIPS ===
- Bucket sort is the "impressive" O(n) answer interviewers love.
- Always count first (O(n)); the challenge is selecting top-k efficiently.
- Heap approach: good when k << n; mention heapq.nlargest as Pythonic shortcut.
- Sorting approach: simplest to code; acceptable if interviewer doesn't demand O(n).
- Follow-up: Return results sorted by frequency? -> collect then sort (still O(n) if k small).
- Follow-up: Streaming data / too large for memory? -> reservoir sampling / Count-Min Sketch.
- Clarify that output order does not matter (problem says "any order").
'''

# === SOLUTION ===
from typing import List
import heapq
from collections import Counter


def topKFrequent(nums: List[int], k: int) -> List[int]:
    """Bucket sort: O(n) time, O(n) space."""
    freq_map = Counter(nums)
    n = len(nums)
    # bucket[i] = list of elements with frequency exactly i
    bucket = [[] for _ in range(n + 1)]
    for num, freq in freq_map.items():
        bucket[freq].append(num)

    result = []
    for freq in range(n, 0, -1):  # high to low frequency
        for num in bucket[freq]:
            result.append(num)
            if len(result) == k:
                return result
    return result


def topKFrequent_heap(nums: List[int], k: int) -> List[int]:
    """Min-heap of size k: O(n log k) time."""
    freq_map = Counter(nums)
    # nlargest keeps the k items with largest frequencies
    return [num for num, _ in heapq.nlargest(k, freq_map.items(), key=lambda x: x[1])]


# === TEST CASES ===
if __name__ == "__main__":
    def sort_result(r):
        return sorted(r)

    # Test 1: Classic example
    assert sort_result(topKFrequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
    # Test 2: Single element
    assert sort_result(topKFrequent([1], 1)) == [1]
    # Test 3: All distinct, k = number of uniques
    assert sort_result(topKFrequent([1, 2, 3], 3)) == [1, 2, 3]
    # Test 4: Tie in frequencies
    result = topKFrequent([1, 2, 2, 3, 3, 3], 1)
    assert sort_result(result) == [3]
    # Test 5: Negative numbers
    assert sort_result(topKFrequent([-1, -1, -2, -2, -2, -3], 1)) == [-2]
    # Test 6: Larger k
    assert sort_result(topKFrequent([3, 0, 1, 0], 1)) == [0]
    print("All tests passed!")
