# Pattern Recognition Cheat Sheet — The Complete Interview Decision Guide

> **The goal:** When you read a problem, you should instantly know which pattern to use.
> This sheet maps **"If the problem says X → use pattern Y"** with detailed explanations.

---

## HOW TO USE THIS SHEET

1. **Before the interview:** Read this 3 times. Memorize the decision tree.
2. **During the interview:** When you read the problem, identify the SIGNAL WORDS.
3. **When stuck:** Go through the patterns in order. One of them will unlock the problem.

---

## THE 15 PATTERNS THAT SOLVE 75+ PROBLEMS

### Pattern 1: Hash Map Lookup ("Seen it before?")

**Signal words:** "Find two elements that...", "Check if X appeared before", "Complement"
**Core idea:** Store elements in a hash map as you iterate. For each new element, check if its "partner" is already in the map.

```
SIGNAL: "Find two numbers that add up to target"
        "Check if array has duplicates"
        "Group items by a common property"

PATTERN:
    seen = {}
    for item in array:
        complement = target - item
        if complement in seen: return answer
        seen[item] = index
```

**Time:** O(n) | **Space:** O(n)
**Solves:** Two Sum (#1), Contains Duplicate (#217), Valid Anagram (#242), Group Anagrams (#49)

---

### Pattern 2: Frequency Counter

**Signal words:** "Count how many times...", "Most frequent", "Top K"
**Core idea:** Use a hash map (or Counter) to count occurrences, then process the counts.

```
SIGNAL: "Find the most frequent element"
        "Top K frequent elements"

PATTERN:
    from collections import Counter
    counts = Counter(array)
    # Then sort, heap, or bucket sort the counts
```

**Solves:** Top K Frequent Elements (#347), Group Anagrams (#49)

---

### Pattern 3: Two Pointers — Opposite Ends

**Signal words:** "Sorted array" + "find pair" / "palindrome" / "container"
**Core idea:** Start one pointer at each end. Move them toward each other based on comparison.

```
SIGNAL: "Two sum in a SORTED array"
        "Is this string a palindrome?"
        "Container with most water"

PATTERN:
    left = 0
    right = len(arr) - 1
    while left < right:
        if arr[left] + arr[right] == target: return [left, right]
        elif arr[left] + arr[right] < target: left += 1
        else: right -= 1
```

**Why it works:** In a sorted array, moving left increases the sum, moving right decreases it. This guides you to the target.
**Time:** O(n) | **Space:** O(1)
**Solves:** Two Sum II (#167), 3Sum (#15), Container With Most Water (#11), Trapping Rain Water (#42)

---

### Pattern 4: Two Pointers — Same Direction (Fast/Slow)

**Signal words:** "Remove duplicates", "detect cycle", "in-place modification"
**Core idea:** Slow pointer tracks where to write. Fast pointer scans ahead.

```
SIGNAL: "Remove duplicates from sorted array (in-place)"
        "Linked list cycle detection"

PATTERN:
    slow = 0
    for fast in range(1, len(arr)):
        if arr[fast] != arr[slow]:
            slow += 1
            arr[slow] = arr[fast]
```

**Solves:** Remove Duplicates, Linked List Cycle (#141), Middle of Linked List

---

### Pattern 5: Sliding Window — Fixed Size

**Signal words:** "Subarray of size K", "Max/min sum of K consecutive elements"
**Core idea:** Maintain a window of exactly K elements. When it slides, add the new element and subtract the old one.

```
SIGNAL: "Maximum sum subarray of size K"
        "Average of K consecutive elements"

PATTERN:
    window_sum = sum(arr[:k])
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]  # Add new, drop old
        max_sum = max(max_sum, window_sum)
```

**Why O(n):** You never recalculate the sum from scratch. Each step is O(1).
**Solves:** Max Sum Subarray of Size K, various fixed-window problems

---

### Pattern 6: Sliding Window — Dynamic Size

**Signal words:** "Longest/shortest subarray where...", "Substring with condition"
**Core idea:** Expand the window to the right. When the condition is violated, shrink from the left.

```
SIGNAL: "Longest substring without repeating characters"
        "Minimum window substring"
        "Longest subarray with sum K"

PATTERN:
    left = 0
    max_len = 0
    state = {}  # Track window contents
    for right in range(len(arr)):
        # Add arr[right] to state
        while condition_violated(state):
            # Remove arr[left] from state
            left += 1
        max_len = max(max_len, right - left + 1)
```

**Why O(n):** Each element enters the window once (right pointer) and leaves once (left pointer). Total: 2n operations.
**Solves:** Longest Substring Without Repeating (#3), Min Window Substring (#76), Longest Repeating Character Replacement (#424)

---

### Pattern 7: Binary Search — Standard

**Signal words:** "Sorted array" + "find/search"
**Core idea:** Cut the search space in half each step. Only works on sorted data.

```
SIGNAL: "Search in a sorted array"
        "Find the index where X would be inserted"

PATTERN:
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: left = mid + 1
        else: right = mid - 1
```

**Time:** O(log n) | **Space:** O(1)
**Solves:** Binary Search (#704), Search Insert Position (#35), Search in Rotated Sorted Array (#33)

---

### Pattern 8: Binary Search on Answer

**Signal words:** "Find the minimum X such that condition(X) is true", "minimum capacity", "minimum speed"
**Core idea:** Binary search the ANSWER SPACE (not the array). For each candidate answer, check if the condition holds.

```
SIGNAL: "Koko eating bananas at minimum speed to finish in H hours"
        "Minimum ship capacity to deliver in D days"
        "Split array into M subarrays minimizing the largest sum"

PATTERN:
    left, right = min_possible, max_possible
    while left < right:
        mid = (left + right) // 2
        if condition(mid):  # Can we achieve the goal with 'mid'?
            right = mid     # Try smaller
        else:
            left = mid + 1  # Need bigger
    return left
```

**Solves:** Koko Eating Bananas (#875), Split Array Largest Sum, Median of Two Sorted Arrays (#4)

---

### Pattern 9: Stack — Matching

**Signal words:** "Valid parentheses", "matching brackets", "balanced expression"
**Core idea:** Push opening brackets. Pop on closing brackets. Check if they match.

```
SIGNAL: "Is this string of parentheses valid?"
        "Evaluate reverse Polish notation"

PATTERN:
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in '([{': stack.append(char)
        elif char in ')]}':
            if not stack or stack[-1] != matching[char]: return False
            stack.pop()
    return len(stack) == 0
```

**Solves:** Valid Parentheses (#20), Evaluate RPN (#150), Min Stack (#155)

---

### Pattern 10: Monotonic Stack

**Signal words:** "Next greater element", "span", "daily temperatures", "largest rectangle"
**Core idea:** Maintain a stack that's always increasing (or decreasing). Pop elements when the order is violated — the current element is their "next greater."

```
SIGNAL: "For each day, how many days until a warmer temperature?"
        "Next greater element"
        "Largest rectangle in histogram"

PATTERN:
    stack = []  # Stores indices, values are monotonic
    for i in range(len(arr)):
        while stack and arr[i] > arr[stack[-1]]:
            prev = stack.pop()
            result[prev] = i - prev  # Found next greater for prev
        stack.append(i)
```

**Solves:** Daily Temperatures (#739), Largest Rectangle in Histogram (#84), Car Fleet (#853)

---

### Pattern 11: BFS (Level-by-Level)

**Signal words:** "Shortest path", "nearest", "minimum steps", "level order", "BFS"
**Core idea:** Process nodes level by level using a queue. First time you reach a node = shortest path.

```
SIGNAL: "Shortest path in unweighted graph"
        "Binary tree level order traversal"
        "Minimum steps to reach target"

PATTERN:
    queue = deque([start])
    visited = {start}
    while queue:
        node = queue.popleft()
        for neighbor in get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

**Solves:** Binary Tree Level Order (#102), Number of Islands (#200, BFS variant), Shortest Path

---

### Pattern 12: DFS (Go Deep)

**Signal words:** "All possible paths", "count components", "flood fill", "connected"
**Core idea:** Go as deep as possible, then backtrack. Use recursion or explicit stack.

```
SIGNAL: "Count connected components"
        "Flood fill / paint bucket"
        "Can you reach all nodes?"

PATTERN:
    def dfs(node, visited):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, visited)

    for node in all_nodes:
        if node not in visited:
            dfs(node, visited)
            count += 1  # New component
```

**Solves:** Number of Islands (#200), Course Schedule (#207), Word Search (#79), Clone Graph (#133)

---

### Pattern 13: Backtracking (DFS + Undo)

**Signal words:** "Generate all combinations/permutations", "find all solutions", "N-Queens"
**Core idea:** Try a choice → recurse → UNDO the choice (backtrack). Explore the entire decision tree.

```
SIGNAL: "Generate all subsets"
        "All permutations of a list"
        "N-Queens"
        "Combination sum"

PATTERN:
    def backtrack(path, choices):
        if is_complete(path):
            result.append(path[:])  # COPY the path!
            return
        for choice in choices:
            if is_valid(choice):
                path.append(choice)       # Make choice
                backtrack(path, updated_choices)  # Explore
                path.pop()                # UNDO choice (backtrack!)

    result = []
    backtrack([], all_choices)
```

**Solves:** Subsets (#78), Permutations (#46), Combination Sum (#39), N-Queens (#51), Word Search (#79), Palindrome Partitioning (#131)

---

### Pattern 14: Dynamic Programming (Overlapping Subproblems)

**Signal words:** "Maximum/minimum/number of ways" + problem has optimal substructure
**Core idea:** Store results of subproblems so you don't recompute them.

```
SIGNAL: "Maximum sum of non-adjacent elements" (House Robber)
        "Number of ways to climb stairs"
        "Minimum coins to make amount" (Coin Change)
        "Longest increasing subsequence"

PATTERN (Bottom-Up Tabulation):
    dp = [0] * (n + 1)
    dp[0] = base_case
    for i in range(1, n + 1):
        dp[i] = f(dp[i-1], dp[i-2], ...)  # Recurrence relation
    return dp[n]

PATTERN (Top-Down Memoization):
    @lru_cache(maxsize=None)
    def solve(state):
        if base_case(state): return base_value
        return min(solve(smaller_state) + cost)
```

**Three steps to solve any DP:**
1. Define the state: `dp[i]` = what does it represent?
2. Write the recurrence: `dp[i] = f(dp[i-1], ...)`
3. Set base cases: `dp[0] = ?`

**Solves:** Climbing Stairs (#70), Coin Change (#322), House Robber (#198), LIS (#300), Word Break (#139), Decode Ways (#91)

---

### Pattern 15: Top-K with Heap

**Signal words:** "K largest/smallest", "K most frequent", "K closest"
**Core idea:** Maintain a heap of size K. Push/pop to keep only the top K elements.

```
SIGNAL: "Find the K largest elements"
        "Kth largest element in array"
        "K closest points to origin"

PATTERN (for K LARGEST — use MIN-heap of size K):
    import heapq
    min_heap = []
    for num in arr:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)  # Remove smallest, keep top K
    return min_heap  # Contains K largest elements
```

**Why O(n log k) instead of O(n log n):** Heap operations are O(log k) because the heap never exceeds size k.
**Solves:** Top K Frequent (#347), Kth Largest Element (#703), K Closest Points (#973), Last Stone Weight (#1046)

---

## QUICK DECISION TREE

```
Read the problem. What is it asking?

├── "Find pair / check existence"
│   ├── Array unsorted → Hash Map (O(n))
│   └── Array sorted → Two Pointers (O(n))
│
├── "Subarray / substring with condition"
│   ├── Fixed size K → Sliding Window (fixed)
│   └── Variable size → Sliding Window (dynamic)
│
├── "Find / search in sorted data"
│   ├── Search in array → Binary Search
│   └── Search in answer space → Binary Search on Answer
│
├── "Matching / nesting / undo"
│   └── Stack
│
├── "Next greater/smaller element"
│   └── Monotonic Stack
│
├── "Generate all possibilities"
│   └── Backtracking (DFS + undo)
│
├── "Shortest path / nearest / level order"
│   └── BFS (Queue)
│
├── "Connected components / flood fill / cycle"
│   └── DFS (Recursion)
│
├── "Max/min/ways with subproblems"
│   └── Dynamic Programming
│
├── "Top K / K largest / K most frequent"
│   └── Heap of size K
│
└── "Prefix matching / autocomplete"
    └── Trie
```

---

## THE "I'M STUCK" CHECKLIST

When you can't figure out the approach, go through these in order:

### 1. Can I SORT it first?
Sorting enables: binary search, two pointers, merging, deduplication.
Cost: O(n log n) upfront, but unlocks O(n) or O(log n) solutions.

### 2. Can I use a HASH MAP?
Hash maps turn O(n) searches into O(1) lookups.
Ask: "Am I searching for something repeatedly?" → Hash map.

### 3. Is the data SORTED?
If yes → binary search (O(log n)) or two pointers (O(n)).

### 4. Is there a SUBPROBLEM?
"Can I solve this for n-1 and extend to n?" → Dynamic Programming.
Ask: "Does the solution for n depend on the solution for smaller n?"

### 5. Can I try ALL POSSIBILITIES?
If the input is small (n ≤ 20) → Backtracking.
Generate all combinations/permutations and filter.

### 6. Can I process from BOTH ENDS?
Two pointers from left and right. Good for palindromes, containers, sorted arrays.

### 7. Is there a MONOTONIC pattern?
"Next greater element", "span", "temperatures" → Monotonic stack.

### 8. Can I model it as a GRAPH?
Grids, networks, dependencies → Graph traversal (BFS/DFS).

---

## BIG-O QUICK REFERENCE CARD

### Data Structure Operations

| Data Structure | Access | Search | Insert | Delete | Space |
|---------------|--------|--------|--------|--------|-------|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| Hash Map | N/A | O(1) | O(1) | O(1) | O(n) |
| Linked List | O(n) | O(n) | O(1)* | O(1)* | O(n) |
| BST (balanced) | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| Heap | O(1)** | O(n) | O(log n) | O(log n) | O(n) |
| Stack/Queue | O(1)*** | O(n) | O(1) | O(1) | O(n) |

\* At known position (head) | \*\* Peek at root | \*\*\* Top/front only

### Algorithm Complexities

| Algorithm | Time | Space | When to Use |
|-----------|------|-------|-------------|
| Binary Search | O(log n) | O(1) | Searching sorted data |
| BFS | O(V + E) | O(V) | Shortest path, level order |
| DFS | O(V + E) | O(V) | Components, cycles, flood fill |
| Merge Sort | O(n log n) | O(n) | Stable sorting |
| Quick Sort | O(n log n) avg | O(log n) | In-place sorting |
| Backtracking | O(2^n) or O(n!) | O(n) | Generate all possibilities |
| DP (tabulation) | O(n) to O(n²) | O(n) to O(n²) | Optimization problems |
| Heap operations | O(log n) | O(1) peek | Priority queue, Top K |

### "What Complexity Do I Need?" Guide

| n Constraint | Max Acceptable | Typical Pattern |
|-------------|----------------|-----------------|
| n ≤ 10 | O(n!) or O(2^n) | Backtracking |
| n ≤ 100 | O(n³) | Triple nested loop |
| n ≤ 1,000 | O(n²) | Nested loop, DP |
| n ≤ 100,000 | O(n log n) | Sort + process |
| n ≤ 1,000,000 | O(n) | Single pass, hash map |
| n > 10⁹ | O(log n) or O(1) | Binary search, math |

---

## INTERVIEW STRATEGY (5 STEPS)

### Step 1: CLARIFY (2 min)
Ask about:
- Input size (n = ?)
- Duplicates? Sorted? Negative numbers?
- Edge cases (empty input, single element)
- Output format (return index? value? list?)

### Step 2: BRUTE FORCE (2 min)
State the obvious O(n²) solution OUT LOUD.
"I could check every pair — that's O(n²). Can I do better?"
Shows: you can solve it, and you know it's not optimal.

### Step 3: OPTIMIZE (5 min)
Think: "What pattern does this signal?"
- "Seen before?" → Hash map
- "Sorted?" → Two pointers or binary search
- "Subarray with condition?" → Sliding window
- "All possibilities?" → Backtracking
- "Optimal substructure?" → DP

### Step 4: CODE (15 min)
- Write clean code with meaningful variable names
- Comment your logic
- Handle edge cases at the top (empty input, etc.)

### Step 5: TEST (5 min)
- Dry-run with a small example
- Check edge cases: empty array, single element, all same, etc.
- State the final time and space complexity

---

## THE FINAL RULES

1. **Pattern recognition > memorization.** Don't memorize solutions. Learn the patterns.
2. **Always state complexity.** Before and after coding. "This is O(n) time, O(n) space because..."
3. **Start with brute force.** Never stare at a blank screen. Write the O(n²) version first, then optimize.
4. **Hash maps are your default weapon.** When in doubt, "Can a hash map help?" → usually YES.
5. **Sorting unlocks patterns.** If the array isn't sorted, ask "Would sorting help?" (enables binary search + two pointers).
6. **Communication > correctness.** A wrong solution with great reasoning beats a correct solution with no explanation.
7. **Edge cases get you hired.** Always check: empty input, single element, negative numbers, duplicates.

---

> **You now have the complete pattern recognition system. Go solve problems.**
