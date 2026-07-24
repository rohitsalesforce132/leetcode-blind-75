'''
LEETCODE #78: Subsets
DIFFICULTY: Medium
TOPIC: Backtracking

=== PROBLEM STATEMENT ===
Given an integer array nums of unique elements, return all possible subsets (the
power set). The solution set must not contain duplicate subsets.

=== INTUITION ===
1. A subset is a selection of elements where each element is either IN or OUT.
2. For n elements, there are 2^n subsets.
3. At each position, we make a binary choice: include or exclude.
4. Backtracking: build subsets recursively by deciding for each element.

Alternative thinking: iterative approach. Start with [[]], for each number,
duplicate all existing subsets and add the number to the copies.

=== APPROACHES ===
Approach 1: Backtracking (pick/don't pick)
- Idea: Recursively decide to include/exclude each element. Every leaf = one subset.
- Time: O(n * 2^n), Space: O(n) recursion depth

Approach 2: Iterative (Cascading)
- Idea: Start with [[]]. For each num, add num to copies of all existing subsets.
- Time: O(n * 2^n), Space: O(n * 2^n) for output

Approach 3: Bitmask
- Idea: Enumerate 0 to 2^n - 1, each number's bits represent inclusion.
- Time: O(n * 2^n), Space: O(n * 2^n)

=== DRY RUN ===
nums = [1, 2, 3]

Backtracking (include-or-skip):
                                   []
                        /                      \
                   [1]                          []
                /        \                   /        \
            [1,2]        [1]               [2]         []
           /     \       /    \           /    \       /    \
       [1,2,3] [1,2] [1,3]  [1]       [2,3]  [2]   [3]     []

Result (collected at every node): [[],[1],[1,2],[1,2,3],[1,3],[2],[2,3],[3]]

=== COMPLEXITY ANALYSIS ===
Time: O(n * 2^n) — 2^n subsets, each up to n elements
Space: O(n) recursion stack, O(n * 2^n) for output

=== EDGE CASES ===
- Empty array -> [[]] (the empty subset)
- Single element -> [[], [x]]
- Large n (n=20 -> 2^20 = 1M subsets, watch memory)

=== INTERVIEW TIPS ===
- This is THE fundamental backtracking problem.
- Two ways to draw the recursion tree: "pick/don't pick" vs "for loop with start index".
- Always add a copy of current path to result (never the reference).
- Follow-up: Subsets II (#90) with duplicates.
'''

# === SOLUTION ===

def subsets(nums):
    """Backtracking: for each element, choose to include or exclude."""
    result = []

    def backtrack(start, current):
        result.append(current[:])  # add a COPY of current subset
        for i in range(start, len(nums)):
            current.append(nums[i])     # choose
            backtrack(i + 1, current)   # explore
            current.pop()               # un-choose (backtrack)

    backtrack(0, [])
    return result


def subsets_iterative(nums):
    """Cascading approach."""
    result = [[]]
    for num in nums:
        # For each existing subset, create new subset with num added
        result += [subset + [num] for subset in result]
    return result


def subsets_bitmask(nums):
    """Bitmask enumeration."""
    n = len(nums)
    result = []
    for mask in range(1 << n):  # 0 to 2^n - 1
        subset = []
        for i in range(n):
            if mask & (1 << i):
                subset.append(nums[i])
        result.append(subset)
    return result


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: standard
    r = subsets([1, 2, 3])
    print(sorted([sorted(s) for s in r]))  # 8 subsets

    # Test 2: single element
    print(subsets([0]))  # [[], [0]]

    # Test 3: empty array
    print(subsets([]))  # [[]]

    # Test 4: iterative
    print(len(subsets_iterative([1, 2, 3])))  # 8

    # Test 5: bitmask
    print(len(subsets_bitmask([1, 2, 3])))  # 8

    # Test 6: verify all approaches give same count
    assert len(subsets([1, 2, 3, 4])) == 16
    assert len(subsets_iterative([1, 2, 3, 4])) == 16
    assert len(subsets_bitmask([1, 2, 3, 4])) == 16
