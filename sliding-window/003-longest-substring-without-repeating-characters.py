'''
LEETCODE #3: Longest Substring Without Repeating Characters
DIFFICULTY: Medium
TOPIC: Sliding Window

=== PROBLEM STATEMENT ===
Given a string s, find the length of the longest substring without repeating
characters.

Example 1: Input: s = "abcabcbb"  Output: 3  ("abc" or "bca" or "cab")
Example 2: Input: s = "bbbbb"     Output: 1  ("b")
Example 3: Input: s = "pwwkew"    Output: 3  ("wke")

=== INTUITION ===
- We want the longest window [left, right] with all distinct characters.
- Expand the window by moving right; if s[right] is already in the window,
  shrink from the left until it's removed.
- Use a hash set to track characters in the current window.
- Track the maximum window size seen.
- Optimization: use a hash map char -> last index to jump left directly.

=== APPROACHES ===
Approach 1: Brute Force
- Idea: Check all substrings; use a set to verify uniqueness.
- Time: O(n^3) or O(n^2) with a set per start.
- Space: O(min(n, alphabet))

Approach 2: Sliding Window with Set
- Idea: Two pointers; add s[right] to set; if duplicate, remove s[left] and move left.
- Time: O(2n) = O(n) - each char added/removed at most once.
- Space: O(min(n, alphabet))

Approach 3: Sliding Window with Hash Map - OPTIMAL
- Idea: Map char -> last seen index. When a repeat is found within the window,
  jump left to max(left, last_index[char] + 1).
- Time: O(n)
- Space: O(min(n, alphabet))

=== DRY RUN ===
s = "abcabcbb"

Hash map approach: char -> index
left = 0, max_len = 0

right=0, char='a': not in window -> map={'a':0}; max_len=max(0,0-0+1)=1
right=1, char='b': not in window -> map={'a':0,'b':1}; max_len=2
right=2, char='c': not in window -> map={...,'c':2}; max_len=3
right=3, char='a': 'a' seen at 0, 0 >= left(0) -> left=0+1=1; map['a']=3
  max_len=max(3,3-1+1)=3
right=4, char='b': 'b' seen at 1, 1 >= left(1) -> left=1+1=2; map['b']=4
  max_len=3
right=5, char='c': 'c' seen at 2, 2 >= left(2) -> left=2+1=3; map['c']=5
  max_len=3
right=6, char='b': 'b' seen at 4, 4 >= left(3) -> left=4+1=5; map['b']=6
  max_len=max(3,6-5+1)=3
right=7, char='b': 'b' seen at 6, 6 >= left(5) -> left=6+1=7; map['b']=7
  max_len=max(3,7-7+1)=3

Result: max_len = 3  CORRECT

=== COMPLEXITY ANALYSIS ===
Time: O(n) - each character processed once.
Space: O(min(n, alphabet_size)) - at most the alphabet size for the map.

=== EDGE CASES ===
- Empty string -> 0.
- Single character -> 1.
- All identical characters -> 1.
- Entire string is unique -> length of string.
- Very long string (O(n) is essential).
- Unicode / extended character sets (hash map handles this).

=== INTERVIEW TIPS ===
- Sliding window is the canonical technique here.
- The hash map optimization (jump left) is strictly better than the set approach
  because it avoids the inner while loop for shrinking.
- Clarify: substring = contiguous; subsequence = not necessarily contiguous.
- Follow-up: Longest Substring with At Most K Distinct Characters (#340).
- Follow-up: Longest Substring with At Most Two Distinct Characters (#159).
- Common mistake: forgetting to check that the repeated char's index is within
  the current window (left <= last_index[char]).
'''

# === SOLUTION ===


def lengthOfLongestSubstring(s: str) -> int:
    """Sliding window with hash map: O(n) time, O(min(n, alphabet)) space."""
    last_index = {}  # char -> most recent index
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        # If char is repeated within the current window, jump left past it
        if char in last_index and last_index[char] >= left:
            left = last_index[char] + 1
        last_index[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len


def lengthOfLongestSubstring_set(s: str) -> int:
    """Sliding window with set (simpler, O(2n) time)."""
    char_set = set()
    left = 0
    max_len = 0
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)
    return max_len


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic example
    assert lengthOfLongestSubstring("abcabcbb") == 3
    # Test 2: All same character
    assert lengthOfLongestSubstring("bbbbb") == 1
    # Test 3: Another example
    assert lengthOfLongestSubstring("pwwkew") == 3
    # Test 4: Empty string
    assert lengthOfLongestSubstring("") == 0
    # Test 5: Single character
    assert lengthOfLongestSubstring("a") == 1
    # Test 6: All unique
    assert lengthOfLongestSubstring("abcdef") == 6
    # Test 7: Space and special chars
    assert lengthOfLongestSubstring("a b c") == 3  # "a b" or "b c"... actually "a b"=3
    print("All tests passed!")
