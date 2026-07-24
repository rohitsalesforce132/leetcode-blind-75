'''
LEETCODE #46: Permutations
DIFFICULTY: Medium
TOPIC: Backtracking

=== PROBLEM STATEMENT ===
Given an array nums of distinct integers, return all the possible permutations.
You can return the answer in any order.

=== INTUITION ===
1. A permutation is an arrangement of all elements. For n distinct elements,
   there are n! permutations.
2. At each position in the permutation, we choose one of the remaining elements.
3. Backtracking: maintain a `used` boolean array. At each step, try every unused
   element.
4. Alternative: swap-based approach (in-place, no extra space for `used`).

=== APPROACHES ===
Approach 1: Backtracking with used array
- Idea: Track which elements are used. At each step, try each unused element.
- Time: O(n * n!), Space: O(n) for used array + recursion

Approach 2: Swap-based (Heap's-like)
- Idea: Fix position 0 by swapping each element to position 0, recurse on rest.
- Time: O(n * n!), Space: O(n) for recursion

Approach 3: Python itertools.permutations
- Time: O(n!), Space: O(n!)

=== DRY RUN ===
nums = [1, 2, 3]

Backtracking tree (used array approach):
                    []
           /        |        \
         [1]       [2]       [3]
        /   \     /   \     /   \
     [1,2] [1,3] [2,1] [2,3] [3,1] [3,2]
       |     |     |     |     |     |
   [1,2,3][1,3,2][2,1,3][2,3,1][3,1,2][3,2,1]

6 permutations = 3!

=== COMPLEXITY ANALYSIS ===
Time: O(n * n!) — n! permutations, each takes O(n) to copy
Space: O(n) recursion depth

=== EDGE CASES ===
- Single element -> [[x]]
- Two elements -> [[a,b],[b,a]]
- Large n (n=10 -> 3.6M permutations, n=12 -> 479M)

=== INTERVIEW TIPS ===
- Two variants: "used array" and "swap" approach. Know both.
- The swap approach is more space-efficient but harder to explain.
- Always add a COPY of current to result.
- Follow-up: Permutations II (#47) with duplicates.
- Follow-up: permutations of a string (same problem).
'''

# === SOLUTION ===

def permute(nums):
    """Backtracking with a 'used' boolean array."""
    result = []
    used = [False] * len(nums)

    def backtrack(current):
        if len(current) == len(nums):
            result.append(current[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            current.append(nums[i])
            backtrack(current)
            current.pop()
            used[i] = False

    backtrack([])
    return result


def permute_swap(nums):
    """Swap-based backtracking."""
    result = []

    def backtrack(first):
        if first == len(nums):
            result.append(nums[:])  # copy current arrangement
            return
        for i in range(first, len(nums)):
            nums[first], nums[i] = nums[i], nums[first]  # swap in
            backtrack(first + 1)
            nums[first], nums[i] = nums[i], nums[first]  # swap back

    backtrack(0)
    return result


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: standard
    r = permute([1, 2, 3])
    print(r)  # 6 permutations
    print(len(r))  # 6

    # Test 2: single element
    print(permute([0]))  # [[0]]

    # Test 3: two elements
    print(permute([1, 2]))  # [[1,2],[2,1]]

    # Test 4: swap approach
    print(len(permute_swap([1, 2, 3])))  # 6

    # Test 5: verify count for n=4
    print(len(permute([1, 2, 3, 4])))  # 24
