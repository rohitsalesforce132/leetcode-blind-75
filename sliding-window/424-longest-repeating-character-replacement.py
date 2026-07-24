'''
LEETCODE #424: Longest Repeating Character Replacement
DIFFICULTY: Medium
TOPIC: Sliding Window

=== PROBLEM STATEMENT ===
You are given a string s and an integer k. You can choose any character of the
string and change it to any other uppercase English character. You can perform
this operation at most k times. Return the length of the longest substring
containing the same letter you can get after performing the above operations.

Example 1: Input: s = "ABAB", k = 2  Output: 4 (change both A's to B or vice versa)
Example 2: Input: s = "AABABBA", k = 1  Output: 4

=== INTUITION ===
- In any valid window, we can replace at most k characters to make them all the same.
- A window [left, right] is valid if (window_length - count_of_most_frequent_char) <= k.
  The "other" characters (window_length - max_freq) are the ones we'd need to replace.
- Expand right; if the window becomes invalid, shrink left until valid again.
- Track the frequency of each char in the current window (hash map or array[26]).
- Key optimization: we only need to track max_frequency, and we DON'T need to
  recompute it when shrinking - because a smaller max_freq never improves the answer.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: For every substring, check if (length - max_freq) <= k.
- Time: O(n^2)
- Space: O(1) (26-char array)

Approach 2: Sliding Window - OPTIMAL
- Idea: Expand right; maintain char counts and max_freq. If window invalid
  (window_len - max_freq > k), shrink left. Track max valid window size.
- Time: O(n)
- Space: O(1) (26 uppercase letters)

=== DRY RUN ===
s = "AABABBA", k = 1

count = {}, left = 0, max_freq = 0, max_len = 0

right=0, char='A': count={'A':1}; max_freq=1
  window_len=1; need to replace = 1-1=0 <= 1 -> valid; max_len=1
right=1, char='A': count={'A':2}; max_freq=2
  window_len=2; replace=2-2=0 <=1 -> valid; max_len=2
right=2, char='B': count={'A':2,'B':1}; max_freq=2
  window_len=3; replace=3-2=1 <=1 -> valid; max_len=3
right=3, char='A': count={'A':3,'B':1}; max_freq=3
  window_len=4; replace=4-3=1 <=1 -> valid; max_len=4
right=4, char='B': count={'A':3,'B':2}; max_freq=3
  window_len=5; replace=5-3=2 > 1 -> INVALID
  shrink: remove s[left]='A'; count={'A':2,'B':2}; left=1
  window_len=4; replace=4-3=1 <=1 -> valid (note: max_freq stays 3)
right=5, char='B': count={'A':2,'B':3}; max_freq=3
  window_len=5 (left=1,right=5); replace=5-3=2 >1 -> INVALID
  shrink: remove s[left]='A'; count={'A':1,'B':3}; left=2
  window_len=4; valid
right=6, char='A': count={'A':2,'B':3}; max_freq=3
  window_len=5 (left=2,right=6); replace=5-3=2 >1 -> INVALID
  shrink: remove s[left]='B'; count={'A':2,'B':2}; left=3
  window_len=4; valid

Result: max_len = 4  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - each character is added and removed at most once.
Space: O(1) - at most 26 entries in the count map.

=== EDGE CASES ===
- k = 0: longest run of a single repeating character.
- k >= len(s): entire string (can replace everything).
- Single character string.
- All characters the same.
- String with even distribution of characters.

=== INTERVIEW TIPS ===
- The validity condition is crucial: window_len - max_freq <= k.
- Explain WHY we don't decrement max_freq when shrinking: because the answer only
  grows when max_freq increases. A stale (too-high) max_freq only makes the window
  appear shorter than it could be, but it never produces a wrong (too-long) answer.
- This is a "non-shrinking window" trick that keeps the algorithm O(n).
- Follow-up: Longest Repeating Character Replacement with lowercase too -> same approach.
- Common mistake: recomputing max_freq every step (O(26n) still fine but unnecessary).
- The window only grows or stays the same size; it never shrinks below the best found.
'''

# === SOLUTION ===


def characterReplacement(s: str, k: int) -> int:
    """Sliding window: O(n) time, O(1) space."""
    count = {}  # char -> frequency in current window
    left = 0
    max_freq = 0  # highest frequency of a single char in the window
    max_len = 0

    for right in range(len(s)):
        count[s[right]] = count.get(s[right], 0) + 1
        max_freq = max(max_freq, count[s[right]])

        # Window is valid if (window_len - max_freq) <= k
        window_len = right - left + 1
        if window_len - max_freq > k:
            # Invalid: shrink from left
            count[s[left]] -= 1
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert characterReplacement("ABAB", 2) == 4
    # Test 2: Another example
    assert characterReplacement("AABABBA", 1) == 4
    # Test 3: k = 0, longest single-char run
    assert characterReplacement("AAAA", 0) == 4
    # Test 4: k = 0, mixed
    assert characterReplacement("AABABBA", 0) == 2  # longest run "AA" or "BB"
    # Test 5: k large enough to cover entire string
    assert characterReplacement("ABCD", 4) == 4
    # Test 6: Single character
    assert characterReplacement("A", 0) == 1
    # Test 7: Empty string
    assert characterReplacement("", 2) == 0
    print("All tests passed!")
