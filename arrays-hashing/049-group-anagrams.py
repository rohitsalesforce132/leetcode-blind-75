'''
LEETCODE #49: Group Anagrams
DIFFICULTY: Medium
TOPIC: Arrays & Hashing

=== PROBLEM STATEMENT ===
Given an array of strings strs, group the anagrams together. You can return
the answer in any order. An Anagram is a word or phrase formed by rearranging
the letters of a different word or phrase, typically using all the original
letters exactly once.

Example 1: Input: strs = ["eat","tea","tan","ate","nat","bat"]
           Output: [["bat"],["nat","tan"],["ate","eat","tea"]]
Example 2: Input: strs = [""]   Output: [[""]]
Example 3: Input: strs = ["a"]  Output: [["a"]]

=== INTUITION ===
- All anagrams share a common "signature" - a canonical form.
- Two natural signatures: (1) the sorted string, (2) a character-count tuple.
- Use a hash map: signature -> list of original strings.
- Group every string by its signature, then return the grouped lists.

=== APPROACHES ===
Approach 1: Sorted String as Key
- Idea: key = "".join(sorted(s)). All anagrams produce the same sorted string.
- Time: O(n * k log k) where n = #strings, k = max string length.
- Space: O(n * k) for the map and output.

Approach 2: Character Count Tuple as Key - often faster for long strings
- Idea: Build a 26-element count tuple; use it as the hash map key.
- Time: O(n * k) - no sorting overhead.
- Space: O(n * k).

=== DRY RUN ===
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]

Process each word, key = sorted(word):
  "eat" -> key="aet" -> groups["aet"] = ["eat"]
  "tea" -> key="aet" -> groups["aet"] = ["eat", "tea"]
  "tan" -> key="ant" -> groups["ant"] = ["tan"]
  "ate" -> key="aet" -> groups["aet"] = ["eat", "tea", "ate"]
  "nat" -> key="ant" -> groups["ant"] = ["tan", "nat"]
  "bat" -> key="abt" -> groups["abt"] = ["bat"]

groups = {
  "aet": ["eat", "tea", "ate"],
  "ant": ["tan", "nat"],
  "abt": ["bat"]
}

Output: [["eat","tea","ate"], ["tan","nat"], ["bat"]]  (order may vary)

=== COMPLEXITY ANALYSIS ===
Time: O(n * k log k) for sorted-key approach; O(n * k) for count-tuple approach.
Space: O(n * k) - storing all strings plus keys in the hash map.

=== EDGE CASES ===
- Empty string input [""] -> [[""]].
- Single string ["a"] -> [["a"]].
- All strings identical -> one group.
- All strings distinct (no anagrams) -> each in its own group.
- Very long strings (count tuple avoids sorting cost).
- Strings with repeated characters.

=== INTERVIEW TIPS ===
- Explain WHY sorting works: anagrams sort to the identical string.
- Mention both key strategies and their trade-offs (sorting simpler; count tuple faster for long strings).
- Clarify output order doesn't matter.
- Follow-up: How to handle Unicode? -> use Counter/dict-based key or sort with key=ord.
- Time complexity must account for both number of strings AND string length.
- Python's defaultdict(list) makes grouping clean and idiomatic.
'''

# === SOLUTION ===
from typing import List
from collections import defaultdict


def groupAnagrams(strs: List[str]) -> List[List[str]]:
    """Group by sorted-string signature."""
    groups = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))  # canonical form of the anagram
        groups[key].append(s)
    return list(groups.values())


def groupAnagrams_count(strs: List[str]) -> List[List[str]]:
    """Group by character-count tuple (avoids sorting)."""
    groups = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for c in s:
            count[ord(c) - ord('a')] += 1
        groups[tuple(count)].append(s)  # tuples are hashable
    return list(groups.values())


# === TEST CASES ===
if __name__ == "__main__":
    def normalize(groups):
        """Sort each group and the outer list for order-independent comparison."""
        return sorted([sorted(g) for g in groups])

    # Test 1: Classic example
    result = groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    expected = [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]
    assert normalize(result) == normalize(expected)
    # Test 2: Empty string
    assert groupAnagrams([""]) == [[""]]
    # Test 3: Single char
    assert groupAnagrams(["a"]) == [["a"]]
    # Test 4: All identical
    result = groupAnagrams(["abc", "abc", "abc"])
    assert normalize(result) == [["abc", "abc", "abc"]]
    # Test 5: No anagrams
    result = groupAnagrams(["abc", "def", "ghi"])
    assert normalize(result) == [["abc"], ["def"], ["ghi"]]
    print("All tests passed!")
