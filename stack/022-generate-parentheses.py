'''
LEETCODE #22: Generate Parentheses
DIFFICULTY: Medium
TOPIC: Backtracking / Stack

=== PROBLEM STATEMENT ===
Given n pairs of parentheses, write a function to generate all combinations of
well-formed parentheses. Return the list of all valid combinations.

Example: n = 3 -> ["((()))","(()())","(())()","()(())","()()()"]

=== INTUITION ===
1. We build the string one character at a time. At each step we may add '(' or ')'.
2. Constraints that keep it valid:
   - We can add '(' as long as we haven't used all n.
   - We can add ')' ONLY if it wouldn't make open parens negative, i.e. only if
     the count of ')' so far is less than the count of '(' so far.
3. Recurse with two counters (open used, close used). When both == n, we have a
   full valid string.

=== APPROACHES ===
Approach 1: Backtracking (Optimal)
- Idea: Recursive DFS, only branch into valid choices. Pruning built into the
  recursion via the two counting constraints.
- Time: O(4^n / sqrt(n))  (Catalan number of nodes)
- Space: O(n) recursion depth (output list is O(Catalan * n))

Approach 2: Iterative / Stack-based DFS
- Idea: Use an explicit stack of (current_string, open, close) tuples.
- Same complexity.

=== DRY RUN ===
n = 3

DFS(state, open=0, close=0):
                       ("", 0, 0)
                    add '('
                       ("(", 1, 0)
                 /                    \
            ("((", 2, 0)             ("()", 1, 1)   [close<open so ')' allowed]
            /         \
       ("(((", 3, 0)  ("(()", 2, 1)
           |               \
       ("((()", 3, 1)    ("(())", 2, 2)
           |                   \
       ("((())", 3, 2)     ("(())(", 3, 2)
           |                      \
       ("((()))", 3, 3) ★        ("(())()", 3, 3) ★
       ... etc -> 5 total leaves

=== COMPLEXITY ANALYSIS ===
Time: O(4^n / sqrt(n)) — bounded by the n-th Catalan number C_n ~ 4^n / (n*sqrt(n)),
  each valid string costs O(n) to build.
Space: O(n) recursion stack; output list holds C_n strings of length 2n.

=== EDGE CASES ===
- n = 1 -> ["()"].
- n = 0 -> [""] (degenerate; some specs say return [""]).
- Verify counts never go negative and never exceed n.

=== INTERVIEW TIPS ===
- The two-counter pruning is the key insight. State it clearly.
- The Catalan bound justifies why brute force (2^(2n) then validate) is wasteful.
- Follow-up: count valid sequences (just return Catalan), or generate all valid
  bracket combinations for k types (use different counters).
- An iterative stack version shows you can convert recursion to explicit stack.
'''

# === SOLUTION ===
def generateParenthesis(n: int) -> list[str]:
    result = []

    def backtrack(current: str, open_count: int, close_count: int):
        # Base case: used all n pairs -> a complete valid string.
        if open_count == n and close_count == n:
            result.append(current)
            return
        # Branch 1: add '(' if we still have opens available.
        if open_count < n:
            backtrack(current + "(", open_count + 1, close_count)
        # Branch 2: add ')' only if it keeps the sequence valid (close < open).
        if close_count < open_count:
            backtrack(current + ")", open_count, close_count + 1)

    backtrack("", 0, 0)
    return result


# === TEST CASES ===
if __name__ == "__main__":
    assert generateParenthesis(1) == ["()"]
    assert len(generateParenthesis(3)) == 5
    assert set(generateParenthesis(3)) == {"((()))", "(()())", "(())()", "()(())", "()()()"}
    assert len(generateParenthesis(4)) == 14  # Catalan number C_4 = 14
    assert generateParenthesis(2) == ["(())", "()()"]
    print("All test cases passed.")
