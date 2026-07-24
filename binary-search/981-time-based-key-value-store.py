'''
LEETCODE #981: Time Based Key-Value Store
DIFFICULTY: Medium
TOPIC: Binary Search

=== PROBLEM STATEMENT ===
Design a time-based key-value store that can store a value for a key at a
given timestamp and retrieve the most recent value for a key at or before a
given timestamp.

Implement the TimeMap class:
- TimeMap() Initializes the object.
- void set(key, value, timestamp) Stores the key with the value at the
  given timestamp.
- string get(key, timestamp) Returns the most recent value for the key at
  or before the given timestamp. If there are no values, return "".

Values for the same key will be stored with strictly increasing timestamps.

=== INTUITION ===
Since set() calls for a given key always have strictly increasing timestamps,
the list of (timestamp, value) pairs for each key is naturally sorted by
timestamp. This means we can use binary search for the get() operation to
find the value with the largest timestamp <= the target timestamp.

Data structure: a dictionary mapping key -> list of (timestamp, value).

=== APPROACHES ===
Approach 1: Brute Force — Linear Search
- Idea: For get(), iterate backwards through the list and return the first
  value with timestamp <= target.
- Time: set O(1), get O(n)
- Space: O(n) for storage

Approach 2: Optimal — Binary Search (bisect_right)
- Idea: Use binary search (bisect_right on timestamps) to find the position.
- Time: set O(1), get O(log n)
- Space: O(n) for storage

=== DRY RUN ===
Operations:
set("foo", "bar", 1)  -> store["foo"] = [(1, "bar")]
set("foo", "bar2", 4) -> store["foo"] = [(1, "bar"), (4, "bar2")]
set("foo", "bar3", 7) -> store["foo"] = [(1, "bar"), (4, "bar2"), (7, "bar3")]

get("foo", 3):
  timestamps = [1, 4, 7], target = 3
  bisect_right([1, 4, 7], 3) = 1 (insertion point after index 0)
  index = 1 - 1 = 0
  return store["foo"][0][1] = "bar"

get("foo", 6):
  bisect_right([1, 4, 7], 6) = 2
  index = 2 - 1 = 1
  return store["foo"][1][1] = "bar2"

get("foo", 0):
  bisect_right([1, 4, 7], 0) = 0
  index = 0 - 1 = -1 => invalid, return ""

=== COMPLEXITY ANALYSIS ===
Time: set O(1) amortized (append to list), get O(log n)
Space: O(total number of set operations)

=== EDGE CASES ===
- get() with timestamp before the first stored timestamp -> return ""
- get() for a key that was never set -> return ""
- get() with exact timestamp match
- Multiple set() calls with increasing timestamps (guaranteed by problem)

=== INTERVIEW TIPS ===
- Mention the invariant: timestamps are strictly increasing per key, which
  guarantees the list is sorted — a prerequisite for binary search.
- Using `bisect_right` instead of `bisect_left` is important because we want
  "at or before" (<=), not "strictly before."
- Alternative: store parallel lists of timestamps and values (instead of
  tuples) for slightly better cache performance — good talking point.
- Follow-up: What if timestamps weren't strictly increasing? (You'd need to
  sort or insert in sorted position, changing set() to O(log n) or O(n).)
'''

# === SOLUTION ===
from typing import List, Tuple
import bisect


class TimeMap:
    """Time-based key-value store with binary search retrieval."""

    def __init__(self):
        # key -> list of (timestamp, value), sorted by timestamp.
        self.store: dict = {}

    def set(self, key: str, value: str, timestamp: int) -> None:
        """Store value for key at the given timestamp."""
        if key not in self.store:
            self.store[key] = []
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        """Return most recent value at or before the given timestamp."""
        if key not in self.store:
            return ""

        entries = self.store[key]
        # Extract timestamps for bisect.
        times = [t for t, _ in entries]

        # bisect_right gives insertion point AFTER any equal elements.
        # So index - 1 gives us the rightmost entry with timestamp <= target.
        idx = bisect.bisect_right(times, timestamp)

        if idx == 0:
            # All timestamps are greater than target.
            return ""

        return entries[idx - 1][1]


# === TEST CASES ===
if __name__ == "__main__":
    tm = TimeMap()
    tm.set("foo", "bar", 1)
    tm.set("foo", "bar2", 4)
    tm.set("foo", "bar3", 7)

    # Test 1: before any entry
    assert tm.get("foo", 0) == ""
    # Test 2: exact first timestamp
    assert tm.get("foo", 1) == "bar"
    # Test 3: between first and second
    assert tm.get("foo", 3) == "bar"
    # Test 4: exact second timestamp
    assert tm.get("foo", 4) == "list2".replace("list", "bar")  # "bar2"
    # Test 5: between second and third
    assert tm.get("foo", 6) == "bar2"
    # Test 6: exact third timestamp
    assert tm.get("foo", 7) == "bar3"
    # Test 7: after all entries
    assert tm.get("foo", 100) == "bar3"
    # Test 8: unknown key
    assert tm.get("unknown", 1) == ""
    print("All tests passed!")
