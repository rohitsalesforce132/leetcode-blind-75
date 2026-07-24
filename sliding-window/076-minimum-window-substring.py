'''
LEETCODE #76: Minimum Window Substring
DIFFICULTY: Hard
TOPIC: Sliding Window

=== PROBLEM STATEMENT ===
Given two strings s and t of lengths m and n respectively, return the minimum
window substring of s such that every character in t (including duplicates)
is included in the window. If there is no such substring, return the empty
string "".

The testcases will be generated such that the answer is unique.

Example 1: Input: s = "ADOBECODEBANC", t = "ABC"  Output: "BANC"
Example 2: Input: s = "a", t = "a"                Output: "a"
Example 3: Input: s = "a", t = "aa"               Output: ""

=== INTUITION ===
- We need the smallest substring of s that contains all characters of t (with multiplicity).
- Use an expandable/contractible sliding window:
  - Expand right until the window contains all of t's characters ("valid").
  - Then contract left to shrink the window while keeping it valid.
  - Track the minimum valid window found.
- Use two counters: need (char counts from t) and have (counts in current window).
- Track a "formed" counter: how many unique chars have met their required count.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: Check every substring of s; see if it contains all of t.
- Time: O(m^2 * n) or O(m^2 * alphabet)
- Space: O(alphabet)

Approach 2: Sliding Window - OPTIMAL
- Idea: Expand right to find a valid window; contract left to minimize it.
        Use frequency maps and a "formed" counter to check validity in O(1).
- Time: O(m + n) where m = len(s), n = len(t).
- Space: O(alphabet) for the two frequency maps.

=== DRY RUN ===
s = "ADOBECODEBANC", t = "ABC"

need = {A:1, B:1, C:1}, required = 3 (unique chars in t)
have = {}, formed = 0, left = 0, min_window = ""

right=0 'A': have={A:1}; A meets need -> formed=1
right=1 'D': have={A:1,D:1}; formed=1
right=2 'O': have={A:1,D:1,O:1}; formed=1
right=3 'B': have={...B:1}; B meets need -> formed=2
right=4 'E': formed=2
right=5 'C': have={...C:1}; C meets need -> formed=3 == required -> VALID!
  Contract left: window="ADOBEC" (indices 0-5)
  Try shrinking: remove 'A' (left=0) -> have[A]=0 < need[A]=1 -> formed=2; stop
  min_window = "ADOBEC" (len 6)

  (formed dropped, continue expanding right)
right=6 'O': formed=2
right=7 'D': formed=2
right=8 'E': formed=2
right=9 'B': have[B]=2; formed=2
right=10 'A': have[A]=1 -> formed=3 -> VALID!
  Contract: window="DOBECODEBA"... actually left=1, so window=indices 1-10
  Shrink: remove 'D'(1) -> have[D]-- (still >0, not in need) -> formed stays 3
    left=2; window="OBECODEBA"
  remove 'O'(2) -> formed=3
    left=3; window="BECODEBA"
  remove 'B'(3) -> have[B]=1 (was 2) -> still meets -> formed=3
    left=4; window="ECODEBA"
  remove 'E'(4) -> formed=3
    left=5; window="CODEBA"
  remove 'C'(5) -> have[C]=0 < need[C]=1 -> formed=2; stop
    min_window candidate was "CODEBA" (len 6), not smaller than current best
  Actually let's track: before removing C, window was "CODEBA" len 6. Same as best.

right=11 'N': formed=2
right=12 'C': have[C]=1 -> formed=3 -> VALID!
  Contract: left=6, window=indices 6-12="ODEBANC"
  remove 'O'(6) -> formed=3; left=7 window="DEBANC"
  remove 'D'(7) -> formed=3; left=8 window="EBANC"
  remove 'E'(8) -> formed=3; left=9 window="BANC"
  remove 'B'(9) -> have[B]=0 < 1 -> formed=2; stop
  Best valid window before removing B was "BANC" (len 4) -> NEW BEST

min_window = "BANC" (len 4)  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(m + n) - each character of s is visited at most twice (expand + contract).
      Building the need map is O(n).
Space: O(alphabet) - two frequency maps of at most the alphabet size.

=== EDGE CASES ===
- t is empty -> return "" (or s, depending on interpretation; problem implies non-empty t).
- s shorter than t -> return "".
- s == t -> return s.
- t has repeated characters: t = "AA", need[A]=2.
- No valid window -> return "".
- Multiple valid windows of same min length -> return any (problem says answer is unique).

=== INTERVIEW TIPS ===
- This is the hardest sliding window problem in Blind 75. Master the template.
- The two-phase approach: EXPAND right until valid, then CONTRACT left to minimize.
- The "formed" counter is the key to O(1) validity checks.
- An alternative: instead of "formed", track a single "missing" count (total chars
  still needed). Decrement when a needed char enters; increment when it leaves.
- Follow-up: Minimum Window Subsequence (#727) - order matters (harder).
- Common bug: incrementing "formed" when have[c] EXCEEDS need[c] (should only count
  the exact match, not overshoot).
'''

# === SOLUTION ===
from collections import Counter


def minWindow(s: str, t: str) -> str:
    """Sliding window: O(m+n) time, O(alphabet) space."""
    if not t or not s:
        return ""

    need = Counter(t)  # required character counts
    required = len(need)  # number of unique chars that must be satisfied
    have = Counter()
    formed = 0  # how many unique chars currently meet their required count

    left = 0
    min_len = float('inf')
    min_start = 0

    for right, char in enumerate(s):
        have[char] += 1
        # Check if this char's count just reached the required amount
        if char in need and have[char] == need[char]:
            formed += 1

        # Contract from left while the window is valid
        while formed == required and left <= right:
            window_len = right - left + 1
            if window_len < min_len:
                min_len = window_len
                min_start = left

            # Remove leftmost char
            left_char = s[left]
            have[left_char] -= 1
            if left_char in need and have[left_char] < need[left_char]:
                formed -= 1
            left += 1

    return s[min_start:min_start + min_len] if min_len != float('inf') else ""


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert minWindow("ADOBECODEBANC", "ABC") == "BANC"
    # Test 2: Single char exact match
    assert minWindow("a", "a") == "a"
    # Test 3: Impossible (t has more chars)
    assert minWindow("a", "aa") == ""
    # Test 4: Entire string is the answer
    assert minWindow("abc", "abc") == "abc"
    # Test 5: t empty (edge case)
    assert minWindow("abc", "") == ""
    # Test 6: Repeated chars in t
    assert minWindow("BBBA", "AB") == "BA"
    # Test 7: Answer at the start
    assert minWindow("ABCDDD", "ABC") == "ABC"
    print("All tests passed!")
