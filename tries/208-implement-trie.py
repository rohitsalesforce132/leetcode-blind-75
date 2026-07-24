'''
LEETCODE #208: Implement Trie (Prefix Tree)
DIFFICULTY: Medium
TOPIC: Tries

=== PROBLEM STATEMENT ===
A trie (pronounced as "try") or prefix tree is a tree data structure used
to efficiently store and retrieve keys in a dataset of strings. There are
various applications of this data structure, such as autocomplete and
spellchecker.

Implement the Trie class:
- Trie(): Initializes the trie object.
- void insert(word): Inserts the string word into the trie.
- boolean search(word): Returns true if word is in the trie.
- boolean startsWith(prefix): Returns true if a previously inserted word
  starts with the given prefix.

=== INTUITION ===
A trie stores characters along paths from the root. Each node has:
- A dictionary/map of children (character -> child node).
- A boolean flag indicating whether this node completes a word.

To insert: walk/create nodes for each character, mark the last node as a word end.
To search: walk nodes for each character; return True only if the final node
exists AND is marked as a word end.
To startsWith: same walk, but return True if the path exists (regardless of
word-end flag).

=== APPROACHES ===
Approach 1: Brute Force — Hash Set
- Idea: Store all words in a set. For startsWith, scan all words for prefix
  matches.
- Time: insert O(L), search O(1), startsWith O(N*L) where N = number of words
- Space: O(total characters)

Approach 2: Optimal — Trie
- Idea: Tree of characters with word-end markers.
- Time: insert O(L), search O(L), startsWith O(L), where L = word length.
- Space: O(total characters across all words)

=== DRY RUN ===
trie = Trie()
trie.insert("apple")

After insert: root -> 'a' -> 'p' -> 'p' -> 'l' -> 'e'(is_word=True)

trie.search("apple"):
  root -> 'a'(exists) -> 'p' -> 'p' -> 'l' -> 'e'(exists, is_word=True)
  => True

trie.search("app"):
  root -> 'a' -> 'p' -> 'p' (exists, but is_word=False)
  => False

trie.startsWith("app"):
  root -> 'a' -> 'p' -> 'p' (path exists)
  => True

trie.insert("app"):
  Walk 'a'->'p'->'p' (all exist), mark 'p' node as is_word=True
  Now: root -> 'a' -> 'p' -> 'p'(is_word=True) -> 'l' -> 'e'(is_word=True)

trie.search("app"): Now returns True.

=== COMPLEXITY ANALYSIS ===
Time: insert O(L), search O(L), startsWith O(L), where L = word/prefix length.
Space: O(A * N) where A = alphabet size, N = total nodes. In practice, the
       trie compresses shared prefixes.

=== EDGE CASES ===
- Empty string
- Inserting the same word twice (idempotent for search)
- Searching for a word that is a prefix of another inserted word
- Searching for a word that extends beyond an inserted word
- startsWith on empty prefix (should return True if trie non-empty)

=== INTERVIEW TIPS ===
- A trie is also called a "prefix tree" or "digital tree."
- Clarify: are inputs only lowercase English letters? If so, you can use a
  fixed-size array [26] instead of a dict for children (slightly faster).
- The word-end flag is the crucial distinction between search() and
  startsWith().
- Common applications: autocomplete, spell check, IP routing tables,
  T9 predictive text.
- Follow-up: How to support deletion? (Remove word-end flag; optionally prune
  nodes that are no longer part of any word.)
'''

# === SOLUTION ===


class TrieNode:
    """A node in the trie."""
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.is_end = False  # True if this node completes a word


class Trie:
    """Prefix tree supporting insert, search, and startsWith."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word: str) -> bool:
        """Return True if the exact word was inserted."""
        node = self._find(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        """Return True if any inserted word starts with the prefix."""
        return self._find(prefix) is not None

    def _find(self, s: str):
        """Walk the trie following s; return the final node or None."""
        node = self.root
        for char in s:
            if char not in node.children:
                return None
            node = node.children[char]
        return node


# === TEST CASES ===
if __name__ == "__main__":
    trie = Trie()

    # Test 1: insert and search
    trie.insert("apple")
    assert trie.search("apple") is True
    # Test 2: search for prefix (not a full word)
    assert trie.search("app") is False
    # Test 3: startsWith
    assert trie.startsWith("app") is True
    # Test 4: insert prefix as word
    trie.insert("app")
    assert trie.search("app") is True
    # Test 5: search nonexistent
    assert trie.search("apricot") is False
    # Test 6: startsWith nonexistent
    assert trie.startsWith("b") is False
    # Test 7: empty string
    trie.insert("")
    assert trie.search("") is True
    print("All tests passed!")
