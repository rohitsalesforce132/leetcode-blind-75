'''
LEETCODE #239: Sliding Window Maximum
DIFFICULTY: Hard
TOPIC: Sliding Window

=== PROBLEM STATEMENT ===
You are given an array of integers nums, there is a sliding window of size k
which is moving from the very left of the array to the very right. You can
only see the k numbers in the window. Each time the sliding window moves right
by one position. Return the max element in each window.

Example 1: Input: nums = [1,3,-1,-3,5,3,6,7], k = 3
           Output: [3,3,5,5,6,7]
Example 2: Input: nums = [1], k = 1  Output: [1]

=== INTUITION ===
- We need the maximum in every window of size k.
- A monotonic DECREASING deque stores candidates: front is always the current max.
- For each new element:
  1. Remove indices from the back while their values <= new element (they can never be max).
  2. Add the new index to the back.
  3. Remove the front if it's outside the window (index <= i - k).
  4. Once the first window is formed (i >= k-1), record nums[deque[0]].
- The deque is always sorted in decreasing order of values.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: For each window, scan all k elements for the max.
- Time: O(n * k)
- Space: O(1) (excluding output)

Approach 2: Max-Heap
- Idea: Maintain a max-heap of (value, index); lazily remove stale entries (out of window).
- Time: O(n log n)
- Space: O(n)

Approach 3: Monotonic Deque - OPTIMAL
- Idea: Deque stores indices in decreasing order of their values. Front = max.
- Time: O(n) - each element pushed and popped at most once.
- Space: O(k) - deque holds at most k indices.

=== DRY RUN ===
nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3
        0  1   2   3  4  5  6  7

deque = collections.deque()  # stores indices
result = []

i=0, nums[0]=1:
  deq=[] -> push 0. deq=[0]
  i < k-1 (0 < 2) -> no output yet
i=1, nums[1]=3:
  pop back while nums[deq[-1]] <= 3: nums[0]=1 <= 3 -> pop. deq=[]
  push 1. deq=[1]
  i < 2 -> no output
i=2, nums[2]=-1:
  nums[deq[-1]]=3 > -1 -> don't pop. push 2. deq=[1,2]
  i >= k-1 (2>=2) -> output nums[deq[0]] = nums[1] = 3. result=[3]
  check front in window: deq[0]=1 > 2-3=-1 -> ok
i=3, nums[3]=-3:
  nums[deq[-1]]=-1 > -3 -> push 3. deq=[1,2,3]
  output nums[1]=3. result=[3,3]
  deq[0]=1 > 3-3=0 -> ok
i=4, nums[4]=5:
  pop back: nums[3]=-3<=5 pop; nums[2]=-1<=5 pop; nums[1]=3<=5 pop. deq=[]
  push 4. deq=[4]
  output nums[4]=5. result=[3,3,5]
i=5, nums[5]=3:
  nums[deq[-1]]=5 > 3 -> push 5. deq=[4,5]
  output nums[4]=5. result=[3,3,5,5]
  deq[0]=4 > 5-3=2 -> ok
i=6, nums[6]=6:
  pop back: nums[5]=3<=6 pop; nums[4]=5<=6 pop. deq=[]
  push 6. deq=[6]
  output nums[6]=6. result=[3,3,5,5,6]
i=7, nums[7]=7:
  pop back: nums[6]=6<=7 pop. deq=[]
  push 7. deq=[7]
  output nums[7]=7. result=[3,3,5,5,6,7]

Result: [3, 3, 5, 5, 6, 7]  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - each element is added to the deque once and removed at most once.
Space: O(k) - deque holds at most k indices at any time.

=== EDGE CASES ===
- k = 1: every element is its own window max -> return nums as-is.
- k = n: single window -> return [max(nums)].
- Single element array.
- All elements equal -> every window max is that value.
- Strictly increasing -> each new element is the max.
- Strictly decreasing -> front is always the oldest, then replaced.
- Negative numbers.

=== INTERVIEW TIPS ===
- The monotonic deque is the canonical solution; interviewers expect it for this problem.
- Key properties: deque stores INDICES (not values), in DECREASING order of values.
- Explain the three operations per step: (1) pop smaller elements from back,
  (2) add new index, (3) evict stale front, (4) record max once window is formed.
- Why O(n)? Each element enters and leaves the deque at most once.
- Alternative: use a heap for O(n log n) if deque logic is hard to recall.
- Follow-up: Sliding Window Median (#480) -> two heaps or sorted container.
- Common mistake: storing values instead of indices (can't check window bounds).
'''

# === SOLUTION ===
from typing import List
from collections import deque


def maxSlidingWindow(nums: List[int], k: int) -> List[int]:
    """Monotonic decreasing deque: O(n) time, O(k) space."""
    deq = deque()  # stores indices; values in decreasing order
    result = []

    for i, num in enumerate(nums):
        # Remove indices from the back whose values are <= current (they're useless)
        while deq and nums[deq[-1]] <= num:
            deq.pop()
        deq.append(i)

        # Remove the front if it's outside the current window
        if deq[0] <= i - k:
            deq.popleft()

        # Once the first full window is formed, start recording
        if i >= k - 1:
            result.append(nums[deq[0]])

    return result


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert maxSlidingWindow([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    # Test 2: Single element
    assert maxSlidingWindow([1], 1) == [1]
    # Test 3: k = n (single window)
    assert maxSlidingWindow([1, 2, 3], 3) == [3]
    # Test 4: k = 1 (each element is its own window)
    assert maxSlidingWindow([4, 3, 2, 1], 1) == [4, 3, 2, 1]
    # Test 5: All equal
    assert maxSlidingWindow([5, 5, 5, 5], 2) == [5, 5, 5]
    # Test 6: Strictly increasing
    assert maxSlidingWindow([1, 2, 3, 4], 2) == [2, 3, 4]
    # Test 7: Strictly decreasing
    assert maxSlidingWindow([4, 3, 2, 1], 2) == [4, 3, 2]
    # Test 8: Negative numbers
    assert maxSlidingWindow([-7, -8, 7, 5, 7, 1, 6, 0], 4) == [7, 7, 7, 7, 7]
    print("All tests passed!")
