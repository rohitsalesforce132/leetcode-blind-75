'''
LEETCODE #211: Design Add and Search Words Data Structure
DIFFICULTY: Medium
TOPIC: Tries

=== PROBLEM STATEMENT ===
Design a data structure WordDictionary that supports the following operations:
- WordDictionary(): Initializes the object.
- void addWord(word): Adds word to the data structure.
- bool search(word): Returns true if any string in the data structure matches
  word. word can contain dots '.' where '.' can match any letter.

=== INTUITION ===
This extends a standard trie with wildcard matching. When we encounter a '.',
we must try ALL children of the current node (since '.' matches any letter).
This requires a recursive/DFS search at wildcard positions.

For exact characters, we follow a single child (O(1) per char).
For '.', we branch into all children, which is O(branching factor) per wildcard.

=== APPROACHES ===
Approach 1: Brute Force — Store All Words, Match with Regex
- Idea: Store words in a set. On search with wildcards, iterate all words and
  match using regex or character-by-character comparison.
- Time: addWord O(L), search O(N*L) (N = number of words)
- Space: O(total characters)

Approach 2: Optimal — Trie with Recursive Wildcard Search
- Idea: Use a trie. At '.', recursively search all children.
- Time: addWord O(L), search O(L) for exact, O(26^L) worst case for all-wildcard.
- Space: O(total characters)

=== DRY RUN ===
dict = WordDictionary()
dict.addWord("bad")
dict.addWord("dad")
dict.addWord("mad")

Trie structure:
  root -> 'b' -> 'a' -> 'd'(end)
       -> 'd' -> 'a' -> 'd'(end)
       -> 'm' -> 'a' -> 'd'(end)

dict.search("pad"):
  'p' not in root.children => False

dict.search("bad"):
  'b' -> 'a' -> 'd'(end) => True

dict.search(".ad"):
  '.' => try all children: 'b', 'd', 'm'
    From 'b': 'a' -> 'd'(end) => found! return True

dict.search("b.."):
  'b' -> '.' => try 'a' -> '.' => try 'd'(end) => True

=== COMPLEXITY ANALYSIS ===
Time:
  addWord: O(L)
  search (no wildcards): O(L)
  search (with wildcards): O(min(N, 26^L)) worst case — but typically much
  faster due to trie pruning.
Space: O(total characters across all words)

=== EDGE CASES ===
- Empty string add and search
- Search with all wildcards "..."
- Search for exact match after wildcard match
- No words in dictionary
- Word longer than any stored word
- Multiple wildcards in a row

=== INTERVIEW TIPS ===
- The key insight is that '.' forces a branch into all children, requiring
  recursion (or an explicit stack).
- Mention the worst-case complexity for all-wildcard searches: if the word is
  "..." of length L, we explore up to 26^L paths. In practice, trie structure
  prunes invalid paths early.
- Clarify: the alphabet is typically lowercase a-z (26 letters). If Unicode
  is allowed, the branching factor could be much larger.
- Follow-up: How to optimize repeated wildcard searches? (Caching results,
  or limiting wildcard positions.)
- The recursive search is essentially a DFS on the trie.
'''

# === SOLUTION ===


class TrieNode:
    """Trie node with children map and word-end flag."""
    def __init__(self):
        self.children = {}
        self.is_end = False


class WordDictionary:
    """Trie-based dictionary supporting '.' wildcard searches."""

    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        """Add a word to the dictionary."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word: str) -> bool:
        """Search for word; '.' matches any single character."""
        def dfs(node: TrieNode, i: int) -> bool:
            # Base case: processed all characters.
            if i == len(word):
                return node.is_end

            char = word[i]
            if char == '.':
                # Wildcard: try all children.
                for child in node.children.values():
                    if dfs(child, i + 1):
                        return True
                return False
            else:
                # Exact character match.
                if char not in node.children:
                    return False
                return dfs(node.children[char], i + 1)

        return dfs(self.root, 0)


# === TEST CASES ===
if __name__ == "__main__":
    wd = WordDictionary()
    wd.addWord("bad")
    wd.addWord("dad")
    wd.addWord("mad")

    # Test 1: exact match found
    assert wd.search("bad") is True
    # Test 2: exact match not found
    assert wd.search("pad") is False
    # Test 3: wildcard at start
    assert wd.search(".ad") is True
    # Test 4: wildcard in middle and end
    assert wd.search("b..") is True
    # Test 5: all wildcards
    assert wd.search("...") is True
    # Test 6: too many wildcards (length mismatch)
    assert wd.search("....") is False
    # Test 7: no match with wildcard
    assert wd.search(".xz") is False
    # Test 8: empty string
    wd.addWord("")
    assert wd.search("") is True
    print("All tests passed!")
