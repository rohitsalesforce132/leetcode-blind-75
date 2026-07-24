'''
LEETCODE #146: LRU Cache
DIFFICULTY: Medium
TOPIC: Linked List / Design

=== PROBLEM STATEMENT ===
Design a data structure that follows the constraints of a Least Recently
Used (LRU) cache. Evict the least recently used element when capacity is
exceeded.

Implement the LRUCache class:
- LRUCache(int capacity): Initialize the cache with positive size capacity.
- int get(int key): Return the value of the key if it exists, otherwise -1.
- void put(int key, int value): Update the value if the key exists.
  Otherwise, add the key-value pair to the cache. If inserting causes the
  number of keys to exceed capacity, evict the least recently used key.

The functions get and put must each run in O(1) average time complexity.

=== INTUITION ===
We need O(1) for both get and put, including moving elements to "most
recently used" position. This requires two data structures:
1. A hash map for O(1) key lookup.
2. A doubly linked list to maintain usage order (MRU at head, LRU at tail).

The hash map stores key -> node pointers. The doubly linked list lets us
move any node to the head in O(1) (since we have direct pointer access
and doubly-linked nodes allow O(1) removal).

=== APPROACHES ===
Approach 1: Brute Force — Ordered List / Array
- Idea: Store items in a list. On access, move to front. Evict from back.
- Time: get O(n), put O(n) — due to search and shifts.
- Space: O(capacity)

Approach 2: Optimal — Hash Map + Doubly Linked List
- Idea: Hash map for lookup, DLL for usage ordering.
- Time: get O(1), put O(1)
- Space: O(capacity)

Approach 3: Python OrderedDict
- Idea: Use collections.OrderedDict with move_to_end and popitem.
- Time: get O(1), put O(1)
- Space: O(capacity)
- NOTE: This is a great shortcut, but interviewers want to see the DLL version.

=== DRY RUN ===
capacity = 2

put(1, 1): cache = {1: node(1,1)}
           DLL: head <-> 1 <-> tail
put(2, 2): cache = {1: node(1,1), 2: node(2,2)}
           DLL: head <-> 2 <-> 1 <-> tail   (2 is MRU, 1 is LRU)
get(1):   return 1; move node(1) to head
           DLL: head <-> 1 <-> 2 <-> tail
put(3, 3): capacity exceeded, evict LRU (2)
           cache = {1: node(1,1), 3: node(3,3)}
           DLL: head <-> 3 <-> 1 <-> tail
get(2):   return -1 (evicted)
get(1):   return 1; move node(1) to head
           DLL: head <-> 1 <-> 3 <-> tail
put(4, 4): capacity exceeded, evict LRU (3)
           cache = {1: node(1,1), 4: node(4,4)}
           DLL: head <-> 4 <-> 1 <-> tail

=== COMPLEXITY ANALYSIS ===
Time: get O(1), put O(1)
Space: O(capacity)

=== EDGE CASES ===
- Capacity of 1
- Updating an existing key (should move to MRU, not add a new entry)
- get on a non-existent key
- Evicting the only element
- Sequence of puts that repeatedly evict

=== INTERVIEW TIPS ===
- The combination of hash map + doubly linked list is a classic design
  pattern worth memorizing.
- Using sentinel/dummy head and tail nodes eliminates all edge cases for
  insertion/deletion at boundaries.
- Explain why a SINGLY linked list won't work: we need O(1) removal of an
  arbitrary node, which requires backward pointers.
- Follow-up: LFU Cache (LeetCode 460) is the harder version — evict by
  frequency, then recency.
- In Python, using OrderedDict is acceptable for production code, but for
  interviews, implement the DLL version.
'''

# === SOLUTION ===
from typing import Optional


class Node:
    """Doubly linked list node storing a key-value pair."""
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """LRU cache using hash map + doubly linked list with sentinel nodes."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node

        # Sentinel nodes eliminate boundary edge cases.
        self.head = Node()  # Most recently used side.
        self.tail = Node()  # Least recently used side.
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Remove a node from the linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_head(self, node: Node) -> None:
        """Insert a node right after the head sentinel (MRU position)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        """Return value for key, or -1. Moves accessed node to MRU."""
        if key in self.cache:
            node = self.cache[key]
            # Move to head (most recently used).
            self._remove(node)
            self._add_to_head(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        """Insert or update key-value pair. Evicts LRU if over capacity."""
        if key in self.cache:
            # Update existing: remove old node, we'll re-insert at head.
            node = self.cache[key]
            self._remove(node)
            node.value = value
            self._add_to_head(node)
        else:
            # New key: check capacity.
            if len(self.cache) >= self.capacity:
                # Evict the LRU node (right before tail sentinel).
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]

            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)


# === TEST CASES ===
if __name__ == "__main__":
    # Test 1: basic operations
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1    # returns 1; 1 becomes MRU
    cache.put(3, 3)             # evicts key 2 (LRU)
    assert cache.get(2) == -1   # returns -1 (not found)
    cache.put(4, 4)             # evicts key 1 (LRU)
    assert cache.get(1) == -1   # returns -1 (not found)
    assert cache.get(3) == 3    # returns 3
    assert cache.get(4) == 4    # returns 4

    # Test 2: capacity 1
    cache = LRUCache(1)
    cache.put(1, 1)
    cache.put(2, 2)             # evicts 1
    assert cache.get(1) == -1
    assert cache.get(2) == 2

    # Test 3: update existing key
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(1, 10)            # update, not add
    assert cache.get(1) == 10
    assert cache.get(2) == 2    # 2 still there (update doesn't evict)

    # Test 4: get on empty cache
    cache = LRUCache(1)
    assert cache.get(1) == -1

    print("All tests passed!")
