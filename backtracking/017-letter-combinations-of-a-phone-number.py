'''
LEETCODE #17: Letter Combinations of a Phone Number
DIFFICULTY: Medium
TOPIC: Backtracking

=== PROBLEM STATEMENT ===
Given a string containing digits from 2-9 inclusive, return all possible letter
combinations that the number could represent. Return the answer in any order.
A mapping of digits to letters (like on telephone buttons) is given.

=== INTUITION ===
1. Each digit maps to 3-4 letters (like T9 phone keypad).
2. This is a Cartesian product problem: we need all combinations of letters,
   one from each digit's mapping.
3. Backtracking: build combinations character by character. At each position,
   try each letter mapped to the current digit.
4. Base case: when the combination length equals the number of digits, add to result.

=== APPROACHES ===
Approach 1: Backtracking (Optimal)
- Idea: Recursively choose one letter per digit.
- Time: O(4^N * N) where N = number of digits (each up to 4 letters, N to build string)
- Space: O(N) recursion depth

Approach 2: Iterative
- Idea: Start with [""], for each digit, extend all combinations with its letters.
- Time: O(4^N * N), Space: O(4^N * N) for output

=== DRY RUN ===
digits = "23"
mapping: 2->"abc", 3->"def"

backtrack(idx=0, current=""):
  for letter in "abc":
    backtrack(1, "a"):
      for letter in "def":
        backtrack(2, "ad"): len==2 -> add "ad"
        backtrack(2, "ae"): add "ae"
        backtrack(2, "af"): add "af"
    backtrack(1, "b"):
      add "bd", "be", "bf"
    backtrack(1, "c"):
      add "cd", "ce", "cf"

Result: ["ad","ae","af","bd","be","bf","cd","ce","cf"] (9 combos = 3*3)

=== COMPLEXITY ANALYSIS ===
Time: O(4^N * N) — 4^N combinations, O(N) to build each string
Space: O(N) recursion depth (excluding output)

=== EDGE CASES ===
- Empty digits string -> [] (no combinations, NOT [""])
- Single digit -> letters mapped to that digit
- Digits with 4 letters (7, 9) vs 3 letters (2-6, 8)
- Contains 1 or 0 (no letters mapped — problem says 2-9 only)

=== INTERVIEW TIPS ===
- Handle empty input explicitly (return []).
- Define the mapping clearly. The tricky part is 7 ("pqrs") and 9 ("wxyz").
- This is the simplest form of backtracking — good warm-up problem.
- Follow-up: what if digits could include 1 and 0? (Just skip them.)
'''

# === SOLUTION ===

def letterCombinations(digits):
    """Backtracking approach."""
    if not digits:
        return []

    phone = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }
    result = []

    def backtrack(idx, current):
        if idx == len(digits):
            result.append(current)
            return
        for letter in phone[digits[idx]]:
            backtrack(idx + 1, current + letter)

    backtrack(0, "")
    return result


def letterCombinations_iterative(digits):
    """Iterative cascading approach."""
    if not digits:
        return []
    phone = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }
    result = [""]
    for digit in digits:
        letters = phone[digit]
        result = [prefix + letter for prefix in result for letter in letters]
    return result


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: standard
    print(letterCombinations("23"))
    # ["ad","ae","af","bd","be","bf","cd","ce","cf"]

    # Test 2: empty
    print(letterCombinations(""))  # []

    # Test 3: single digit
    print(letterCombinations("2"))  # ["a","b","c"]

    # Test 4: digits with 4 letters
    print(len(letterCombinations("79")))  # 16 (4*4)

    # Test 5: iterative
    print(letterCombinations_iterative("23"))
    # ["ad","ae","af","bd","be","bf","cd","ce","cf"]

    # Test 6: longer
    print(len(letterCombinations("234")))  # 27 (3*3*3)
