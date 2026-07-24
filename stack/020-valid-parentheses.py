'''
LEETCODE #20: Valid Parentheses
DIFFICULTY: Easy
TOPIC: Stack

=== PROBLEM STATEMENT ===
Given a string s containing just the characters '(', ')', '{', '}', '[' and ']',
determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order (LIFO).
3. Every close bracket has a corresponding open bracket of the same type.

Return true if valid, otherwise false.

=== INTUITION ===
1. Openers ('(', '{', '[') must close in REVERSE order of opening. This is the
   defining property of a Stack (Last-In-First-Out).
2. For each closing bracket we encounter, it must match the MOST RECENTLY opened
   bracket that is still unmatched. So we peek at the stack top.
3. After processing the whole string, the stack must be empty (every opener got
   closed). If anything is left, something was never closed -> invalid.

=== APPROACHES ===
Approach 1: Stack (Optimal)
- Idea: Push openers onto a stack. On a closer, check the top of the stack for a
  matching opener; pop if match, else invalid. At end, stack must be empty.
- Time: O(n), Space: O(n)

Approach 2: Counter (WRONG for mixed types)
- Idea: Count open vs close. Fails: "([)]" has balanced counts but is invalid.
- Only works for a single bracket type.

=== DRY RUN ===
s = "({[]})"

Step  char   stack (bottom->top)    action
 1    '('    ['(']                   push
 2    '{'    ['(', '{']              push
 3    '['    ['(', '{', '[']         push
 4    ']'    ['(', '{']              '[' matches -> pop
 5    '}'    ['(']                   '{' matches -> pop
 6    ')'    []                      '(' matches -> pop
End: stack empty -> True

=== COMPLEXITY ANALYSIS ===
Time: O(n) — single pass, each char pushed/popped at most once.
Space: O(n) — stack grows to size of all openers in worst case "((((...".

=== EDGE CASES ===
- Empty string "" -> True (vacuously valid).
- Single char "(" or ")" -> False.
- Only closers "))" -> False (stack empty when we try to pop).
- Only openers "(((" -> False (non-empty stack at end).
- Mismatched types "(]" -> False.

=== INTERVIEW TIPS ===
- Map closers -> openers (not the reverse) so a single lookup handles matching.
- Mention the "wrong counter approach" to show you understand WHY a stack is needed.
- Follow-up: extend to '(*' where '*' can be '(' or ')' -> use two stacks or greedy
  (low/high count of unmatched openers).
'''

# === SOLUTION ===
def isValid(s: str) -> bool:
    # Map each closer to its required opener.
    close_to_open = {')': '(', '}': '{', ']': '['}
    stack = []

    for ch in s:
        if ch in close_to_open:  # ch is a closing bracket
            # Pop the top if non-empty, else use a sentinel that can never match.
            top = stack.pop() if stack else '#'
            if close_to_open[ch] != top:
                return False
        else:  # ch is an opening bracket
            stack.append(ch)

    return len(stack) == 0  # valid only if nothing left unclosed


# === TEST CASES ===
if __name__ == "__main__":
    assert isValid("()") is True
    assert isValid("()[]{}") is True
    assert isValid("(]") is False
    assert isValid("([)]") is False
    assert isValid("{[]}") is True
    assert isValid("") is True
    assert isValid("(") is False
    assert isValid(")") is False
    assert isValid("(((") is False
    print("All test cases passed.")
