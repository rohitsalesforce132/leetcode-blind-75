'''
LEETCODE #242: Valid Anagram
DIFFICULTY: Easy
TOPIC: Arrays & Hashing

=== PROBLEM STATEMENT ===
Given two strings s and t, return true if t is an anagram of s, and false
otherwise. An Anagram is a word or phrase formed by rearranging the letters
of a different word or phrase, typically using all the original letters
exactly once.

Example 1: Input: s = "anagram", t = "nagaram"  Output: true
Example 2: Input: s = "rat", t = "car"          Output: false

Follow up: What if the inputs contain Unicode characters? How would you adapt
your solution to such a case?

=== INTUITION ===
- Two strings are anagrams iff they have identical character frequency counts.
- Lengths must be equal first (quick rejection).
- Count chars with a hash map (or a fixed array of 26 for lowercase a-z).
- Alternatively, sorting both strings and comparing is simple but slower.

=== APPROACHES ===
Approach 1: Sorting
- Idea: Sort both strings; anagrams produce identical sorted strings.
- Time: O(n log n)
- Space: O(n) for the sorted copies (or O(1) if sorting in place on a list)

Approach 2: Hash Map Counter - OPTIMAL (Unicode friendly)
- Idea: Count characters in s; decrement for t. All counts must be zero.
        Or compare Counter(s) == Counter(t).
- Time: O(n)
- Space: O(k) where k = number of distinct characters (O(1) for fixed alphabet)

Approach 3: Fixed Array (26 chars) - OPTIMAL for lowercase a-z
- Idea: Use an int[26]; increment for s, decrement for t; check all zeros.
- Time: O(n)
- Space: O(1) (exactly 26 ints)

=== DRY RUN ===
s = "anagram", t = "nagaram"

Lengths: len(s)=7 == len(t)=7 -> proceed

Building count from s:
  a -> count['a']++  ...  count['a']=3, count['n']=1, count['g']=1, count['r']=1, count['m']=1

Decrementing with t = "nagaram":
  n: count['n']=0
  a: count['a']=2
  g: count['g']=0
  a: count['a']=1
  r: count['r']=0
  a: count['a']=0
  m: count['m']=0

All counts zero -> True

=== COMPLEXITY ANALYSIS ===
Time: O(n) - one pass over each string.
Space: O(1) - at most 26 entries (lowercase) or O(k) distinct Unicode chars.

=== EDGE CASES ===
- Different lengths -> immediately False.
- Both empty strings -> True (vacuous anagram).
- Single character strings, equal or different.
- Unicode characters (use hash map, not fixed array).
- Whitespace / punctuation if problem extends beyond lowercase letters.
- Case sensitivity (problem states lowercase; clarify in interview).

=== INTERVIEW TIPS ===
- Always check length equality first - cheap O(1) early exit.
- Counter comparison is Pythonic: `return Counter(s) == Counter(t)`.
- Mention sorting as the "simple but slower" alternative.
- For Unicode follow-up: use a dict/hash map instead of a 26-element array.
- Follow-up: Group Anagrams (#49) builds on this frequency idea.
'''

# === SOLUTION ===
from typing import List
from collections import Counter


def isAnagram(s: str, t: str) -> bool:
    """Hash map counter approach (Unicode friendly)."""
    if len(s) != len(t):
        return False
    return Counter(s) == Counter(t)


def isAnagram_array(s: str, t: str) -> bool:
    """Fixed 26-element array for lowercase English letters only."""
    if len(s) != len(t):
        return False
    count = [0] * 26
    for c in s:
        count[ord(c) - ord('a')] += 1
    for c in t:
        count[ord(c) - ord('a')] -= 1
        if count[ord(c) - ord('a')] < 0:  # early exit
            return False
    return True


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic anagram
    assert isAnagram("anagram", "nagaram") is True
    # Test 2: Not an anagram
    assert isAnagram("rat", "car") is False
    # Test 3: Both empty
    assert isAnagram("", "") is True
    # Test 4: Different lengths
    assert isAnagram("ab", "a") is False
    # Test 5: Single char equal
    assert isAnagram("a", "a") is True
    # Test 6: Single char different
    assert isAnagram("a", "b") is False
    # Test 7: Same letters different counts
    assert isAnagram("aab", "abb") is False
    print("All tests passed!")
