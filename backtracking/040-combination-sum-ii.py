'''
LEETCODE #40: Combination Sum II
DIFFICULTY: Medium
TOPIC: Backtracking

=== PROBLEM STATEMENT ===
Given a collection of candidate numbers (candidates) and a target number target,
find all unique combinations in candidates where the candidate numbers sum to target.
Each number in candidates may only be used once in the combination.
The solution set must not contain duplicate combinations.

=== INTUITION ===
1. Like Combination Sum, but each candidate used at most once AND duplicates exist.
2. The challenge: avoid duplicate combinations. E.g., candidates=[1,1,2], target=3.
   We want [[1,2]] once, not twice.
3. Solution: sort candidates. When skipping a candidate at a given loop level,
   skip ALL identical candidates (if candidates[i] == candidates[i-1], skip).
4. This ensures: at each position in the combination, we only pick the "first"
   of any group of duplicates.

=== APPROACHES ===
Approach 1: Backtracking with duplicate skipping (Optimal)
- Idea: Sort, then at each recursion level skip consecutive duplicate candidates.
- Time: O(2^n) worst case, Space: O(n) recursion depth

Approach 2: Count frequencies, then backtrack over unique values
- Idea: Use a Counter, backtrack over unique values with their counts.
- Time: O(2^n), Space: O(n)

=== DRY RUN ===
candidates = [1, 1, 2, 5, 6, 7, 10], target = 8

After sorting: [1, 1, 2, 5, 6, 7, 10]

backtrack(start=0, remaining=8):
  i=0: pick 1 (i==start, ok), remaining=7, current=[1]
    i=1: pick 1 (i==start), remaining=6, current=[1,1]
      i=2: pick 2, remaining=4, current=[1,1,2]
        i=3: pick 5, remaining=-1 -> STOP
      i=3: pick 5, remaining=1, current=[1,1,5]
        ... overshoots
    i=2: pick 2, remaining=5, current=[1,2]
      i=3: pick 5, remaining=0 -> FOUND! [1,2,5]
      i=4: pick 6, remaining=-1 -> STOP
    i=3: pick 5, remaining=2, current=[1,5]
      ... overshoot
  i=1: candidates[1]==candidates[0] -> SKIP (avoids duplicate)
  i=2: pick 2, remaining=6, current=[2]
    i=3: pick 5, remaining=1 -> overshoot
    i=4: pick 6, remaining=0 -> FOUND! [2,6]
  i=3: pick 5, remaining=3 -> ...
  i=4: pick 6, remaining=2 -> ...
  i=5: pick 7, remaining=1 -> ...
  i=6: pick 10 -> overshoot

Result: [[1,2,5], [2,6], [1,7]]

Wait, let me verify [1,7]: start=0 pick 1 (remaining 7), then i=5 pick 7 (remaining 0).
Yes! That works.

=== COMPLEXITY ANALYSIS ===
Time: O(2^n) worst case (each element in or out)
Space: O(n) recursion depth

=== EDGE CASES ===
- All candidates are the same (e.g., [1,1,1,1], target=2 -> [[1,1]])
- No valid combinations
- Single element matching target
- target = 0 -> [[]]
- Large candidate list with many duplicates

=== INTERVIEW TIPS ===
- The duplicate-skipping condition `if i > start and candidates[i] == candidates[i-1]: continue`
  is the key line. Understand WHY `i > start` — it allows the first of a group
  to be picked but skips the rest at the same loop level.
- Sorting is REQUIRED for the duplicate skipping to work.
- Contrast with #39: there candidates were distinct, here they may have dups.
'''

# === SOLUTION ===

def combinationSum2(candidates, target):
    """Backtracking with duplicate avoidance."""
    result = []
    candidates.sort()

    def backtrack(start, remaining, current):
        if remaining == 0:
            result.append(current[:])
            return
        for i in range(start, len(candidates)):
            # Skip duplicates at this level (only first of each group)
            if i > start and candidates[i] == candidates[i - 1]:
                continue
            if candidates[i] > remaining:
                break  # sorted, so no point continuing
            current.append(candidates[i])
            backtrack(i + 1, remaining - candidates[i], current)  # i+1: use once
            current.pop()

    backtrack(0, target, [])
    return result


def combinationSum2_counter(candidates, target):
    """Alternative: count frequencies, backtrack over unique values."""
    from collections import Counter
    counts = Counter(candidates)
    unique = sorted(counts.keys())
    result = []

    def backtrack(idx, remaining, current):
        if remaining == 0:
            result.append(current[:])
            return
        for i in range(idx, len(unique)):
            val = unique[i]
            if val > remaining:
                break
            if counts[val] == 0:
                continue
            current.append(val)
            counts[val] -= 1
            backtrack(i, remaining - val, current)  # same i, can reuse if count left
            counts[val] += 1
            current.pop()

    backtrack(0, target, [])
    return result


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: standard
    print(combinationSum2([10, 1, 2, 7, 6, 1, 5], 8))
    # [[1,1,6],[1,2,5],[1,7],[2,6]]

    # Test 2: all duplicates
    print(combinationSum2([1, 1, 1, 1], 2))  # [[1,1]]

    # Test 3: single element
    print(combinationSum2([1], 1))  # [[1]]

    # Test 4: no solution
    print(combinationSum2([1, 2], 4))  # []

    # Test 5: counter approach
    print(combinationSum2_counter([10, 1, 2, 7, 6, 1, 5], 8))
    # [[1,1,6],[1,2,5],[1,7],[2,6]]
