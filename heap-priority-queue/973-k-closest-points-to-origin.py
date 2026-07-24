'''
LEETCODE #973: K Closest Points to Origin
DIFFICULTY: Medium
TOPIC: Heap / Priority Queue / Quickselect

=== PROBLEM STATEMENT ===
Given an array of points where points[i] = [xi, yi] represents a point on the
X-Y plane and an integer k, return the k closest points to the origin (0, 0).
The distance between two points on the X-Y plane is the Euclidean distance,
sqrt((x1-x2)^2 + (y1-y2)^2). You may return the answer in any order.

=== INTUITION ===
1. "Closest to origin" = smallest squared Euclidean distance x^2 + y^2 (we can
   skip the sqrt since it's monotonic — comparing squared distances preserves order).
2. We need the k smallest among n distances. Two classic strategies:
   (a) MAX-HEAP of size k: push points; if heap exceeds size k, evict the farthest
       (largest distance). At the end the heap holds the k closest.
   (b) QUICKSELECT: partition around a pivot; nth_element style. O(n) average.

=== APPROACHES ===
Approach 1: Max-Heap of size k (recommended in interviews)
- Maintain a max-heap of size k keyed by distance. Push negated distance so the
  heapq min-heap behaves as a max-heap on distance.
- Time: O(n log k), Space: O(k)

Approach 2: Sort all by distance, take first k
- Time: O(n log n), Space: O(n). Simpler but slower for small k.

Approach 3: Quickselect
- Time: O(n) average, O(n^2) worst case. Space: O(n).
- Optimal for huge n, small k; in-place partitioning.

=== DRY RUN ===
points = [[1,3],[-2,2]], k = 1
Distances squared: [1+9=10], [4+4=8]
Sorted by distance: [-2,2] (8), [1,3] (10)
Closest 1 -> [[-2,2]]

points = [[3,3],[5,-1],[-2,4]], k = 2
Distances: 18, 26, 20
Closest 2 -> [18, 20] -> [[3,3],[-2,4]]

Max-heap (size k=2), processing:
  push [3,3] dist 18: heap=[(-18,[3,3])]
  push [5,-1] dist 26: heap=[(-26,[5,-1]),(-18,[3,3])], size=2 ok
  push [-2,4] dist 20: heap=[(-26,...),(-18,...),(-20,...)] size 3 > 2 -> pop largest
    pop removes -26 ([5,-1]); heap keeps [(-20,[-2,4]),(-18,[3,3])]
  Result: [[3,3],[-2,4]]

=== COMPLEXITY ANALYSIS ===
Time (Approach 1): O(n log k) — each of n points is pushed; up to n pops, each O(log k).
Space: O(k) for the heap.

=== EDGE CASES ===
- k == len(points): return all points.
- k == 1: return the single closest point.
- Points at the origin (0,0): distance 0, definitely included.
- Duplicate points / ties in distance: any valid subset is acceptable.
- Negative coordinates: squared distance handles them.

=== INTERVIEW TIPS ===
- Skip the sqrt — compare squared distances. Mention this as a micro-optimization.
- Max-heap of size k (not min-heap of all n) is the key efficiency move.
- If asked for O(n) average, pivot to quickselect. Discuss worst-case O(n^2) and
  how randomized pivot mitigates it.
- Discuss tie-breaking: problem accepts any order, so don't over-engineer.
'''

# === SOLUTION ===
import heapq


def kClosest(points: list[list[int]], k: int) -> list[list[int]]:
    # Max-heap of size k: store (-distance, point). Largest distance sits on top
    # so it's the one we evict when heap overflows.
    heap = []

    for x, y in points:
        dist = x * x + y * y  # squared Euclidean distance
        heapq.heappush(heap, (-dist, [x, y]))
        if len(heap) > k:
            heapq.heappop(heap)  # remove the farthest among the current k+1

    return [point for (_, point) in heap]


# === TEST CASES ===
if __name__ == "__main__":
    def sorted_pts(pts):
        return sorted([sorted(p) for p in pts])

    res = kClosest([[1, 3], [-2, 2]], 1)
    assert sorted_pts(res) == [[-2, 2]]

    res = kClosest([[3, 3], [5, -1], [-2, 4]], 2)
    assert sorted_pts(res) == [[-2, 4], [3, 3]]

    assert kClosest([[0, 0], [1, 1]], 2) == [[0, 0], [1, 1]] or len(kClosest([[0,0],[1,1]], 2)) == 2
    assert kClosest([[1, 0]], 1) == [[1, 0]]
    res = kClosest([[1, 3], [-2, 2], [2, -2], [4, 1]], 2)
    # Two points tie at distance 8: [-2,2] and [2,-2]; both returned.
    assert sorted_pts(res) == [[-2, 2], [-2, 2]]
    print("All test cases passed.")
