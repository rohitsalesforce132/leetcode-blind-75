'''
LEETCODE #703: Kth Largest Element in a Stream
DIFFICULTY: Easy
TOPIC: Heap / Priority Queue

=== PROBLEM STATEMENT ===
Design a class to find the k-th largest element in a stream. Note that it is the
k-th largest element in the sorted order, not the k-th distinct element.

Implement KthLargest:
- KthLargest(int k, int[] nums): initialize with k and the stream nums.
- int add(int val): inserts val into the stream and returns the k-th largest.

=== INTUITION ===
1. We only care about the TOP k largest elements at any time. The k-th largest is
   the SMALLEST among those top k.
2. A MIN-HEAP of size k gives O(1) access to its smallest element, which is
   exactly the k-th largest overall.
3. On add(val): push val, then if heap size > k, pop the smallest. The new top is
   the answer.

=== APPROACHES ===
Approach 1: Min-Heap of size k (Optimal)
- Maintain a min-heap of the k largest elements seen so far.
- add: push, trim to size k, return heap[0].
- Time: constructor O(n log k), add O(log k). Space: O(k).

Approach 2: Keep a sorted list, binary-search insert (bisect)
- add: bisect.insort O(k), then index -k. Works but more code and O(k) insert.

=== DRY RUN ===
k = 3, nums = [4,5,8,2]
Constructor: heapify then trim to size 3.
  After heapify: [2,4,8,5] (conceptually). Trim to 3 largest: keep [4,5,8].
  Min-heap of size 3 -> [4,5,8], top = 4 (the 3rd largest).

add(3): heap=[3,4,5,8] size4 -> pop -> [4,5,8], top=4   (3rd largest is 4)
add(5): heap=[4,5,5,8] size4 -> pop -> [5,5,8], top=5   (3rd largest is 5)
add(10):heap=[5,5,8,10] size4 -> pop -> [5,8,10], top=5
add(9):heap=[5,8,9,10] size4 -> pop -> [8,9,10], top=8
add(4):heap=[4,8,9,10] size4 -> pop -> [8,9,10], top=8

=== COMPLEXITY ANALYSIS ===
Time:
  Constructor: O(n log k) — n pushes, each O(log k).
  add: O(log k) — one push + possibly one pop.
Space: O(k) — heap never exceeds k.

=== EDGE CASES ===
- k = 1 -> heap keeps only the single largest element (a running max).
- add called before any nums -> heap may be smaller than k initially; only return
  top when size == k (problem guarantees enough elements).
- Duplicate values: kept (k-th largest, not distinct).
- nums longer than k: trim in constructor.

=== INTERVIEW TIPS ===
- The insight "k-th largest = smallest of the top k = min-heap of size k" is the
  one-liner that unlocks the problem.
- Contrast with Quickselect (better one-shot, worse for streaming) and sorting
  (O(n log n), wasteful for repeated queries).
- Follow-up: k-th largest in a static array -> Quickselect O(n) average.
- Always use heapq in Python; note heapq is a min-heap, so for "k-th largest"
  you naturally get it. For "k-th smallest" you'd use a max-heap (invert signs).
'''

# === SOLUTION ===
import heapq


class KthLargest:
    def __init__(self, k: int, nums: list[int]):
        self.k = k
        self.heap = []
        for num in nums:
            self._add_internal(num)

    def _add_internal(self, val: int) -> None:
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)

    def add(self, val: int) -> int:
        self._add_internal(val)
        return self.heap[0]  # smallest of the k largest = k-th largest overall


# === TEST CASES ===
if __name__ == "__main__":
    kth = KthLargest(3, [4, 5, 8, 2])
    assert kth.add(3) == 4
    assert kth.add(5) == 5
    assert kth.add(10) == 5
    assert kth.add(9) == 8
    assert kth.add(4) == 8

    kth2 = KthLargest(1, [])
    assert kth2.add(-3) == -3
    assert kth2.add(-2) == -2
    assert kth2.add(-4) == -2
    assert kth2.add(0) == 0
    assert kth2.add(4) == 4
    print("All test cases passed.")
