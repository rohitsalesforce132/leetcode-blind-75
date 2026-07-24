'''
LEETCODE #39: Combination Sum
DIFFICULTY: Medium
TOPIC: Backtracking

=== PROBLEM STATEMENT ===
Given an array of distinct integers `candidates` and a target integer `target`,
return a list of all unique combinations of candidates where the chosen numbers
sum to target. You may choose the same number from candidates an unlimited number
of times. Two combinations are unique if the frequency of at least one of the
chosen numbers is different.

=== INTUITION ===
1. This is the "unlimited use" combination problem.
2. At each step, we can either:
   a. Pick candidates[i] again (unlimited reuse).
   b. Move to candidates[i+1] (stop using candidates[i]).
3. Backtrack with a start index to avoid permutations of the same combination.
4. Prune: if remaining target < candidates[i], stop exploring further (works if sorted).

=== APPROACHES ===
Approach 1: Backtracking with start index (Optimal)
- Idea: Recursively try adding candidates[start], recurse with same start (reuse allowed),
  then backtrack and try next candidate.
- Time: O(N^(T/M)) where N = number of candidates, T = target, M = min candidate.
  In the worst case, we explore many branches.
- Space: O(T/M) recursion depth.

Approach 2: DP
- Idea: dp[i] = list of all combinations summing to i.
- Time: O(T * N * combinations), Space: O(T * combinations).
  Impractical for large outputs but conceptually works.

=== DRY RUN ===
candidates = [2, 3, 6, 7], target = 7

backtrack(start=0, remaining=7, current=[]):
  i=0: pick 2, remaining=5, current=[2]
    i=0: pick 2, remaining=3, current=[2,2]
      i=0: pick 2, remaining=1, current=[2,2,2]
        i=0: pick 2, remaining=-1 -> STOP (overshoot)
      i=1: pick 3, remaining=0 -> FOUND! [2,2,3]
      i=2: pick 6, remaining=-3 -> STOP
    i=1: pick 3, remaining=2, current=[2,3]
      i=1: pick 3, remaining=-1 -> STOP
      ...
    i=2: pick 6, remaining=-1 -> STOP
  i=1: pick 3, remaining=4, current=[3]
    ... (3+3+... overshoots)
  i=2: pick 6, remaining=1
    ... (overshoots with 2,3,6)
  i=3: pick 7, remaining=0 -> FOUND! [7]

Result: [[2,2,3], [7]]

=== COMPLEXITY ANALYSIS ===
Time: O(N^(T/M)) — bounded by the number of valid combinations
Space: O(T/M) recursion depth

=== EDGE CASES ===
- target = 0 -> [[]] (empty combination)
- Single candidate that divides target evenly
- No valid combinations -> []
- Candidate == target (trivial solution)
- Large target with small candidates (exponential blowup)

=== INTERVIEW TIPS ===
- The "unlimited reuse" is the key twist — pass `i` (not `i+1`) in recursion.
- Sorting candidates enables pruning (stop early when overshoot).
- Always append a COPY of current to result.
- Follow-up: Combination Sum II (#40) — each number used once, with duplicates.
- Follow-up: Combination Sum III (#216), IV (#377).
'''

# === SOLUTION ===

def combinationSum(candidates, target):
    """Backtracking with unlimited reuse allowed."""
    result = []
    candidates.sort()  # sort for pruning

    def backtrack(start, remaining, current):
        if remaining == 0:
            result.append(current[:])  # found a valid combination
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break  # pruning: no point trying larger numbers
            current.append(candidates[i])
            backtrack(i, remaining - candidates[i], current)  # note: `i`, not `i+1`
            current.pop()

    backtrack(0, target, [])
    return result


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: standard
    print(combinationSum([2, 3, 6, 7], 7))  # [[2,2,3],[7]]

    # Test 2: another
    print(combinationSum([2, 3, 5], 8))  # [[2,2,2,2],[2,3,3],[3,5]]

    # Test 3: single candidate
    print(combinationSum([2], 1))  # []

    # Test 4: target is a candidate
    print(combinationSum([1], 1))  # [[1]]

    # Test 5: all ones
    print(combinationSum([1], 3))  # [[1,1,1]]
