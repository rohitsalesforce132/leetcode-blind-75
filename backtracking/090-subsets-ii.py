'''
LEETCODE #90: Subsets II
DIFFICULTY: Medium
TOPIC: Backtracking

=== PROBLEM STATEMENT ===
Given an integer array nums that may contain duplicates, return all possible
subsets (the power set). The solution set must not contain duplicate subsets.

=== INTUITION ===
1. Same as Subsets (#78) but with duplicates in the input.
2. The challenge: avoid generating duplicate subsets.
3. Solution: sort nums first. When choosing elements at a given loop level,
   skip consecutive duplicates (same trick as Combination Sum II).
4. The rule: if i > start and nums[i] == nums[i-1], skip nums[i].
   This ensures we only pick the "first" of any group of identical elements
   at each decision level.

=== APPROACHES ===
Approach 1: Backtracking with duplicate skipping (Optimal)
- Idea: Sort, then skip duplicates at each recursion level.
- Time: O(n * 2^n), Space: O(n)

Approach 2: Frequency map approach
- Idea: Count occurrences. Backtrack over unique values, choosing 0..count copies.
- Time: O(n * 2^n), Space: O(n)

=== DRY RUN ===
nums = [1, 2, 2] (after sorting)

backtrack(start=0, current=[]):
  add [] to result
  i=0: pick 1 -> current=[1]
    add [1]
    i=1: pick 2 -> current=[1,2]
      add [1,2]
      i=2: nums[2]==nums[1] but i>start(1) -> SKIP
    i=2: nums[2]==nums[1] and i>start(0) -> SKIP
  i=1: pick 2 -> current=[2]
    add [2]
    i=2: pick 2 (i==start, ok since within recursion we haven't picked it) -> current=[2,2]
      add [2,2]
  i=2: nums[2]==nums[1] and i>start(0) -> SKIP

Result: [[], [1], [1,2], [2], [2,2]]
(5 unique subsets, not 8)

=== COMPLEXITY ANALYSIS ===
Time: O(n * 2^n)
Space: O(n) recursion depth

=== EDGE CASES ===
- All elements identical -> n+1 subsets ([], [x], [x,x], ..., [x]*n)
- No duplicates -> degrades to standard Subsets (#78)
- Single element
- Empty array -> [[]]

=== INTERVIEW TIPS ===
- The duplicate skipping pattern `if i > start and nums[i] == nums[i-1]: continue`
  is the SAME as Combination Sum II (#40). Master this pattern.
- Sorting MUST happen first.
- Contrast with #78 (no duplicates) — the only difference is this skip line.
'''

# === SOLUTION ===

def subsetsWithDup(nums):
    """Backtracking with duplicate skipping."""
    result = []
    nums.sort()

    def backtrack(start, current):
        result.append(current[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue  # skip duplicate at this level
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()

    backtrack(0, [])
    return result


def subsetsWithDup_freq(nums):
    """Frequency map approach."""
    from collections import Counter
    counts = Counter(nums)
    unique = sorted(counts.keys())
    result = []

    def backtrack(idx, current):
        if idx == len(unique):
            result.append(current[:])
            return
        val = unique[idx]
        # Try using 0, 1, 2, ..., count copies of this value
        for count in range(counts[val] + 1):
            backtrack(idx + 1, current + [val] * count)

    backtrack(0, [])
    return result


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: with duplicates
    print(subsetsWithDup([1, 2, 2]))
    # [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]

    # Test 2: all same
    print(subsetsWithDup([1, 1, 1]))
    # [[], [1], [1, 1], [1, 1, 1]]

    # Test 3: no duplicates (same as Subsets #78)
    r = subsetsWithDup([1, 2, 3])
    print(len(r))  # 8

    # Test 4: single element
    print(subsetsWithDup([0]))  # [[], [0]]

    # Test 5: frequency approach
    print(subsetsWithDup_freq([1, 2, 2]))
    # [[], [1], [2], [2, 2], [1, 2], [1, 2, 2]]
