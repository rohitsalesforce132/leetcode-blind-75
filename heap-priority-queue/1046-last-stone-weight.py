'''
LEETCODE #1046: Last Stone Weight
DIFFICULTY: Easy
TOPIC: Heap / Priority Queue

=== PROBLEM STATEMENT ===
We have a collection of stones, each with a positive integer weight. Each turn we
choose the two heaviest stones and smash them. Let their weights be x <= y.
- If x == y, both stones are destroyed.
- If x != y, the stone of weight x is destroyed and the stone of weight y has
  new weight y - x.
Continue until at most one stone is left. Return its weight (or 0 if none).

=== INTUITION ===
1. We repeatedly need the two LARGEST elements. That's the textbook use case for
   a MAX-HEAP (priority queue).
2. Python's heapq is a min-heap, so we store NEGATED weights to simulate a max-heap.
3. Loop: pop the two largest (smallest negated). If equal, both gone. Else push
   back the difference (still negated). Stop when <= 1 stone remains.

=== APPROACHES ===
Approach 1: Max-Heap (Optimal)
- Heapify (negated), then repeatedly extract top two.
- Time: O(n log n) overall (n pops/pushes, each O(log n)).
- Space: O(n) for the heap.

Approach 2: Sort + re-sort each turn
- Sort descending, take two, re-insert maintaining order (bisect).
- Time: O(n^2) worst case; fine for small n but heap is cleaner.

=== DRY RUN ===
stones = [2,7,4,1,8,1]
Negate -> [-2,-7,-4,-1,-8,-1], heapify -> [-8,-7,-4,-2,-1,-1]

Turn 1: pop -8 (y=8), pop -7 (x=7). 8 != 7 -> push -(8-7) = -1. heap=[-4,-2,-1,-1,-1]
Turn 2: pop -4 (y=4), pop -2 (x=2). 4 != 2 -> push -2.            heap=[-2,-1,-1,-1]
Turn 3: pop -2 (y=2), pop -1 (x=1). 2 != 1 -> push -1.            heap=[-1,-1,-1]
Turn 4: pop -1 (y=1), pop -1 (x=1). 1 == 1 -> both gone.          heap=[-1]
One stone left of weight 1. Answer: 1.

=== COMPLEXITY ANALYSIS ===
Time: O(n log n) — heapify is O(n); each of up to n turns does O(log n) work.
Space: O(n) for the heap.

=== EDGE CASES ===
- Single stone [x] -> x (no smashing possible).
- All equal [a,a,a,a] -> pairs cancel -> 0.
- [1,1] -> 0.
- Two stones [2,5] -> 3.

=== INTERVIEW TIPS ===
- Identify the "two largest" need -> max-heap. Negation trick in Python.
- Loop invariant: while len(heap) > 1.
- Push the absolute difference back (negated) only when unequal.
- Follow-up: if you needed to log every collision, just collect results each turn.
- Be careful: heapq.heappop on negated values; convert back with abs() or - when
  reading the final answer.
'''

# === SOLUTION ===
import heapq


def lastStoneWeight(stones: list[int]) -> int:
    # Max-heap via negation: Python's heapq is a min-heap.
    heap = [-s for s in stones]
    heapq.heapify(heap)

    while len(heap) > 1:
        y = -heapq.heappop(heap)  # heaviest
        x = -heapq.heappop(heap)  # second heaviest
        if x != y:
            heapq.heappush(heap, -(y - x))  # push the remaining fragment

    return -heap[0] if heap else 0


# === TEST CASES ===
if __name__ == "__main__":
    assert lastStoneWeight([2,7,4,1,8,1]) == 1
    assert lastStoneWeight([1]) == 1
    assert lastStoneWeight([1,1]) == 0
    assert lastStoneWeight([2,5]) == 3
    assert lastStoneWeight([10,10,10,10]) == 0
    assert lastStoneWeight([9,3,2,10]) == 0   # 10-9=1, 3-2=1, 1-1=0
    print("All test cases passed.")
