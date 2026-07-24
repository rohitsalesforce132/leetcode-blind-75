'''
LEETCODE #739: Daily Temperatures
DIFFICULTY: Medium
TOPIC: Stack (Monotonic Stack)

=== PROBLEM STATEMENT ===
Given an array of integers temperatures representing daily temperatures, return
an array answer such that answer[i] is the number of days you have to wait after
the i-th day to get a warmer temperature. If there is no future day with a warmer
temperature, answer[i] == 0.

=== INTUITION ===
1. For each day i we want the NEXT day j > i with temperatures[j] > temperatures[i].
2. Naively that's O(n^2). We can do better by remembering days we haven't found
   an answer for yet, stored in a stack.
3. KEY: maintain a MONOTONICALLY DECREASING stack of indices (by their temps).
   When a new temperature arrives that's warmer than the temperature at the index
   on top of the stack, we have just found the answer for that index. Pop it,
   record the gap, and keep popping while the stack top is colder.

=== APPROACHES ===
Approach 1: Brute Force
- For each i, scan forward for first warmer day.
- Time: O(n^2), Space: O(1)

Approach 2: Monotonic Stack (Optimal)
- Maintain decreasing stack of indices. Process left to right. When current temp
  > temp[stack.top], resolve those indices.
- Time: O(n) — each index pushed/popped once.
- Space: O(n)

=== DRY RUN ===
temperatures = [73, 74, 75, 71, 69, 72, 76, 73]

i  temp  stack(before)  resolved                stack(after)   answer
0  73    []                                      [0]            [0,0,0,0,0,0,0,0]
1  74    [0]            0: 74>73 -> ans[0]=1-0=1 [1]            [1,0,0,0,0,0,0,0]
2  75    [1]            1: 75>74 -> ans[1]=2-1=1 [2]            [1,1,0,0,0,0,0,0]
3  71    [2]            (71 < 75, no resolve)    [2,3]          ...
4  69    [2,3]          (69 < 71, no resolve)    [2,3,4]
5  72    [2,3,4]        4: 72>69 -> ans[4]=5-4=1 [2,3,5]
                        3: 72>71 -> ans[3]=5-3=2 [2,5]
6  76    [2,5]          5: 76>72 -> ans[5]=6-5=1 [2]
                        2: 76>75 -> ans[2]=6-2=4 [6]
7  73    [6]            (73 < 76, no resolve)    [6,7]
End: answer = [1,1,4,2,1,1,0,0]

=== COMPLEXITY ANALYSIS ===
Time: O(n) — each index is pushed and popped at most once.
Space: O(n) for the stack.

=== EDGE CASES ===
- All equal temps [5,5,5] -> all zeros (no strictly warmer day).
- Strictly decreasing [9,8,7] -> all zeros.
- Strictly increasing [1,2,3] -> [1,1,0].
- Single element -> [0].

=== INTERVIEW TIPS ===
- The phrase "next greater element" should immediately suggest a monotonic stack.
- Stack stores INDICES (not values) so you can compute the day gap = j - i.
- The same pattern solves Next Greater Element I/II, stock span, online stock span.
- Explain WHY O(n): amortized — each element pushed once, popped once.
'''

# === SOLUTION ===
def dailyTemperatures(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    answer = [0] * n
    stack = []  # stores indices; temperatures[index] are monotonically decreasing

    for i, t in enumerate(temperatures):
        # Resolve all unresolved days that are colder than today.
        while stack and temperatures[stack[-1]] < t:
            prev_idx = stack.pop()
            answer[prev_idx] = i - prev_idx
        stack.append(i)

    # Indices left in the stack never found a warmer day; their answer stays 0.
    return answer


# === TEST CASES ===
if __name__ == "__main__":
    assert dailyTemperatures([73,74,75,71,69,72,76,73]) == [1,1,4,2,1,1,0,0]
    assert dailyTemperatures([30,40,50,60]) == [1,1,1,0]
    assert dailyTemperatures([30,20,10]) == [0,0,0]
    assert dailyTemperatures([50]) == [0]
    assert dailyTemperatures([5,5,5]) == [0,0,0]
    assert dailyTemperatures([89,62,70,58,47,47,46,76,100,70]) == [8,1,5,4,3,2,1,1,0,0]
    print("All test cases passed.")
