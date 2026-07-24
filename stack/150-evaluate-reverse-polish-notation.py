'''
LEETCODE #150: Evaluate Reverse Polish Notation
DIFFICULTY: Medium
TOPIC: Stack

=== PROBLEM STATEMENT ===
Evaluate the value of an arithmetic expression in Reverse Polish Notation (RPN).

Valid operators are +, -, *, /. Each operand may be an integer or another
expression. Division between two integers truncates toward zero (floor toward
zero, i.e. drop the fractional part). The input is guaranteed valid.

=== INTUITION ===
1. RPN (postfix notation) is designed so that it can be evaluated with a single
   left-to-right scan using a stack — no parentheses or precedence rules needed.
2. When we see a number, push it. When we see an operator, it applies to the two
   MOST RECENT operands, which are the top two elements of the stack.
3. Pop the right operand first (top), then the left operand. Apply operator,
   push result back. Final stack holds exactly one value: the answer.

=== APPROACHES ===
Approach 1: Stack
- Idea: push numbers; on operator pop two, apply, push result.
- Time: O(n), Space: O(n)

=== DRY RUN ===
tokens = ["2","1","+","3","*"]

Step  token   stack          action
 1    "2"     [2]            push
 2    "1"     [2, 1]         push
 3    "+"     [3]            pop b=1, a=2; 2+1=3; push
 4    "3"     [3, 3]         push
 5    "*"     [9]            pop b=3, a=3; 3*3=9; push
Result: 9

Division example: ["10","6","9","3","+","-11","*","/","*","17","+","5","+"]
  -> ((10 * (6 / ((9 + 3) * -11))) + 17) + 5 = 22

=== COMPLEXITY ANALYSIS ===
Time: O(n) — each token processed once; each value pushed/popped at most once.
Space: O(n) — stack holds at most ceil(n/2)+1 numbers.

=== EDGE CASES ===
- Single token: it's just the number. Return it.
- Negative numbers including "-11": handled (we check operator set, not "-").
- Division truncation toward zero: Python's // floors toward -inf, so for
  negatives use int(a / b) which truncates toward zero.
- Large division values (10^9 range).
- Subtract/divide order: left operand is SECOND popped.

=== INTERVIEW TIPS ===
- Critical: order matters. b = stack.pop() then a = stack.pop(); compute a OP b.
- Python division pitfall: int(a / b) truncates toward zero (7/-3 = -2), but
  a // b floors toward -inf (7 // -3 = -3). Always explain this.
- Follow-up: convert infix to postfix (shunting-yard algorithm), or build an
  expression tree.
'''

# === SOLUTION ===
def evalRPN(tokens: list[str]) -> int:
    stack = []
    operators = {"+", "-", "*", "/"}

    for tok in tokens:
        if tok in operators:
            b = stack.pop()  # right operand (popped first = top)
            a = stack.pop()  # left operand
            if tok == "+":
                stack.append(a + b)
            elif tok == "-":
                stack.append(a - b)
            elif tok == "*":
                stack.append(a * b)
            else:  # "/"
                # int() truncates toward zero, unlike // which floors toward -inf.
                stack.append(int(a / b))
        else:
            stack.append(int(tok))

    return stack[0]


# === TEST CASES ===
if __name__ == "__main__":
    assert evalRPN(["2","1","+","3","*"]) == 9
    assert evalRPN(["4","13","5","/","+"]) == 6
    assert evalRPN(["10","6","9","3","+","-11","*","/","*","17","+","5","+"]) == 22
    assert evalRPN(["18"]) == 18
    assert evalRPN(["3","11","+","5","-"]) == 9
    assert evalRPN(["7","-3","/"]) == -2   # truncate toward zero, not floor
    print("All test cases passed.")
