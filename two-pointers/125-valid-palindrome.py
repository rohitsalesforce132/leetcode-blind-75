'''
LEETCODE #125: Valid Palindrome
DIFFICULTY: Easy
TOPIC: Two Pointers

=== PROBLEM STATEMENT ===
A phrase is a palindrome if, after converting all uppercase letters into
lowercase letters and removing all non-alphanumeric characters, it reads the
same forward and backward. Alphanumeric characters include letters and numbers.

Given a string s, return true if it is a palindrome, or false otherwise.

Example 1: Input: s = "A man, a plan, a canal: Panama"  Output: true
Example 2: Input: s = "race a car"                      Output: false
Example 3: Input: s = " "                               Output: true

=== INTUITION ===
- A palindrome reads identically forward and backward.
- Two pointers from both ends, skipping non-alphanumeric chars, comparing lowercased.
- Move pointers inward; if at any point chars differ, not a palindrome.
- They meet in the middle -> palindrome confirmed.

=== APPROACHES ===
Approach 1: Two Pointers (in-place) - OPTIMAL
- Idea: left=0, right=len-1; skip non-alphanumeric; compare; move inward.
- Time: O(n)
- Space: O(1)

Approach 2: Clean and Compare
- Idea: Filter to alphanumeric lowercase, then compare string to its reverse.
- Time: O(n)
- Space: O(n) for the cleaned string

=== DRY RUN ===
s = "A man, a plan, a canal: Panama"

Cleaned mentally: "amanaplanacanalpanama" (a palindrome)

Two-pointer walk:
  L=0 ('a'), R=len-1 ('a')  -> match -> L++, R--
  L=1 (' '), skip -> L=2 ('m')
  R=len-2 ('m')  -> match -> ...
  ... continues until L >= R ...

All matched -> True

=== COMPLEXITY ANALYSIS ===
Time: O(n) - each character visited at most once.
Space: O(1) for the two-pointer approach (no extra string created).

=== EDGE CASES ===
- Empty string or whitespace-only -> True (vacuously a palindrome).
- Single character -> True.
- String with only non-alphanumeric chars (e.g., ".,!") -> True.
- Mixed case: "AbA" -> True (case-insensitive).
- Digits included: "1a2" -> False; "1a1" -> True.
- Very long string (efficiency of skipping matters).

=== INTERVIEW TIPS ===
- Use str.isalnum() to check alphanumeric; str.lower() for case-insensitivity.
- The two-pointer approach is preferred for its O(1) space.
- Clarify the definition of alphanumeric (letters AND digits).
- Follow-up: "Palindrome Number" (#9) - solve without converting to string.
- Follow-up: "Valid Palindrome II" (#680) - allow deleting at most one char.
- Be careful with index bounds when skipping non-alphanumeric chars.
'''

# === SOLUTION ===


def isPalindrome(s: str) -> bool:
    """Two-pointer approach: O(n) time, O(1) space."""
    left, right = 0, len(s) - 1
    while left < right:
        # Skip non-alphanumeric from the left
        while left < right and not s[left].isalnum():
            left += 1
        # Skip non-alphanumeric from the right
        while left < right and not s[right].isalnum():
            right -= 1
        # Compare (case-insensitive)
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True


def isPalindrome_clean(s: str) -> bool:
    """Clean-and-compare: O(n) time, O(n) space (simpler but uses extra memory)."""
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: Classic palindrome with punctuation
    assert isPalindrome("A man, a plan, a canal: Panama") is True
    # Test 2: Not a palindrome
    assert isPalindrome("race a car") is False
    # Test 3: Empty/whitespace
    assert isPalindrome(" ") is True
    # Test 4: Single character
    assert isPalindrome("a") is True
    # Test 5: Only punctuation
    assert isPalindrome(".,!") is True
    # Test 6: With digits, palindrome
    assert isPalindrome("1b1") is True
    # Test 7: Mixed case
    assert isPalindrome("AbBa") is True
    print("All tests passed!")
