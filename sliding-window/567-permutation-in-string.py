'''
LEETCODE #567: Permutation in String
DIFFICULTY: Medium
TOPIC: Sliding Window

=== PROBLEM STATEMENT ===
Given two strings s1 and s2, return true if s2 contains a permutation of s1,
or false otherwise. In other words, return true if one of s1's permutations
is a substring of s2.

Example 1: Input: s1 = "ab", s2 = "eidbaooo"  Output: true ("ba" is a perm of "ab")
Example 2: Input: s1 = "ab", s2 = "eidboaoo"  Output: false

=== INTUITION ===
- A permutation of s1 has the exact same character frequency count as s1.
- So we need a window in s2 of length len(s1) whose frequency matches s1's.
- Sliding window of fixed size len(s1): maintain char counts, compare.
- Optimization: instead of comparing full arrays each step, track the number of
  characters whose counts MATCH between the window and s1.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: Generate all permutations of s1; check if any is a substring of s2.
- Time: O(n! * n) - completely impractical.
- Space: O(n)

Approach 2: Sorting / Counter Comparison per Window
- Idea: For each window of size len(s1) in s2, compare Counter(window) to Counter(s1).
- Time: O(n * m) where n=len(s2), m=len(s1) (recounting each window).
- Space: O(1) (26-char alphabet)

Approach 3: Sliding Window with Match Count - OPTIMAL
- Idea: Maintain counts for s1 and the current window. Track how many of the 26
        characters have matching counts ("matches"). When matches == 26, found.
- Time: O(n) where n = len(s2).
- Space: O(1) (two 26-element arrays)

=== DRY RUN ===
s1 = "ab", s2 = "eidbaooo"

s1_count:  a=1, b=1, rest=0
window_count starts empty (all zeros), window size = 2

Initialize window with first 2 chars of s2: "ei"
  window_count: e=1, i=1
  matches: compare all 26; only e and i differ from s1_count... matches=24
  (24 chars have count 0 in both; e and i have count 1 in window but 0 in s1;
   a and b have count 0 in window but 1 in s1) -> matches=22

Slide right, removing left char each time:
  Add 'd' (index 2), remove 'e' (index 0): window="id"
    window_count: i=1, d=1
  Add 'b' (index 3), remove 'i' (index 1): window="db"
    window_count: d=1, b=1
    b now matches s1_count (both=1)! matches increases.
  Add 'a' (index 4), remove 'd' (index 2): window="ba"
    window_count: b=1, a=1
    a matches (1==1), b matches (1==1) -> all 26 match!

Return True  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) where n = len(s2). Each character is added/removed once; match count
      updated in O(1) per character.
Space: O(1) - two fixed-size 26-element arrays.

=== EDGE CASES ===
- s1 longer than s2 -> False immediately.
- s1 == s2 (and is a permutation) -> True.
- s1 is single character -> check if that char is in s2.
- s1 and s2 identical -> True.
- No matching permutation -> False.
- Repeated characters in s1.

=== INTERVIEW TIPS ===
- The key insight: a permutation has the SAME character frequency as the original.
- Fixed-size sliding window of len(s1) over s2.
- The "matches" counter optimization avoids O(26) comparison per step -> O(1) per step.
- Alternative: maintain a "balance" of how many chars have non-zero difference.
- Follow-up: Find All Anagrams in a String (#438) - return all start indices.
- Common mistake: forgetting to handle the case where len(s1) > len(s2).
'''

# === SOLUTION ===


def checkInclusion(s1: str, s2: str) -> bool:
    """Sliding window with match count: O(n) time, O(1) space."""
    if len(s1) > len(s2):
        return False

    s1_count = [0] * 26
    window_count = [0] * 26
    a_ord = ord('a')

    # Build frequency for s1 and the initial window (first len(s1) chars of s2)
    for i in range(len(s1)):
        s1_count[ord(s1[i]) - a_ord] += 1
        window_count[ord(s2[i]) - a_ord] += 1

    # Count initial matches (chars with identical counts)
    matches = 0
    for i in range(26):
        if s1_count[i] == window_count[i]:
            matches += 1

    if matches == 26:
        return True

    # Slide the window across s2
    for i in range(len(s1), len(s2)):
        # Character entering the window (right side)
        add_idx = ord(s2[i]) - a_ord
        # Character leaving the window (left side)
        remove_idx = ord(s2[i - len(s1)]) - a_ord

        # Update for added character
        if window_count[add_idx] == s1_count[add_idx]:
            matches -= 1  # was matching, will break
        window_count[add_idx] += 1
        if window_count[add_idx] == s1_count[add_idx]:
            matches += 1  # now matching

        # Update for removed character
        if window_count[remove_idx] == s1_count[remove_idx]:
            matches -= 1  # was matching, will break
        window_count[remove_idx] -= 1
        if window_count[remove_idx] == s1_count[remove_idx]:
            matches += 1  # now matching

        if matches == 26:
            return True

    return False


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Permutation present
    assert checkInclusion("ab", "eidbaooo") is True
    # Test 2: No permutation
    assert checkInclusion("ab", "eidboaoo") is False
    # Test 3: s1 longer than s2
    assert checkInclusion("abc", "ab") is False
    # Test 4: Exact match
    assert checkInclusion("abc", "abc") is True
    # Test 5: Single character s1
    assert checkInclusion("a", "bac") is True
    # Test 6: Permutation at the very end
    assert checkInclusion("adc", "dcda") is True
    # Test 7: Repeated chars
    assert checkInclusion("hello", "oell o") is False
    assert checkInclusion("ab", "a") is False
    print("All tests passed!")
