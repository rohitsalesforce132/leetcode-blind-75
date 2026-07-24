# Pattern Recognition Cheat Sheet

> **The goal:** When you read a problem, you should instantly know which pattern to use.
> This sheet maps **"If the problem says X → use pattern Y"**.

---

## THE 15 PATTERNS THAT SOLVE 75 PROBLEMS

### 1. Hash Map Lookup ("Seen it before?")
> **Signal:** "Find two things that add up to..." / "Check if something appeared before"
> **Use:** Hash map (dict). Store first pass, lookup on second.
> **Time:** O(n)
> **Problems:** Two Sum (#1), Contains Duplicate (#217), Valid Anagram (#242)

```
PATTERN:
    seen = {}
    for item in array:
        if complement in seen: return answer
        seen[item] = True
```

### 2. Frequency Counter
> **Signal:** "Count how many times..." / "Group by..." / "Top K frequent"
> **Use:** Hash map as counter, then sort or heap.
> **Problems:** Group Anagrams (#49), Top K Frequent (#347)

### 3. Two Pointers — Opposite Ends
> **Signal:** Array is SORTED + "find pair" / "palindrome" / "container"
> **Use:** left=0, right=n-1. Move based on comparison.
> **Time:** O(n)
> **Problems:** Two Sum II (#167), 3Sum (#15), Container With Most Water (#11)

### 4. Two Pointers — Same Direction (Fast/Slow)
> **Signal:** "Remove duplicates" / "detect cycle" / "in-place modify"
> **Use:** slow writes, fast scans.
> **Problems:** Remove Duplicates, Linked List Cycle (#141)

### 5. Sliding Window — Fixed Size
> **Signal:** "Subarray of size K" / "Max/min sum of K consecutive"
> **Use:** Maintain sum/count. Add new element, subtract old.
> **Time:** O(n)

```
PATTERN:
    window_sum = sum(arr[:k])
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i-k]   # add new, drop old
```

### 6. Sliding Window — Dynamic Size
> **Signal:** "Longest/shortest subarray where..." / condition to maintain
> **Use:** Expand right. Shrink left when condition violated.
> **Problems:** Longest Substring (#3), Min Window Substring (#76)

### 7. Binary Search
> **Signal:** Array is SORTED + "find" / "search"
> **Use:** Cut search space in half each step.
> **Time:** O(log n)
> **Problems:** Binary Search (#704), Search in Rotated Array (#33)

### 8. Binary Search on Answer
> **Signal:** "Find minimum X such that condition(X) is true"
> **Use:** Binary search the ANSWER SPACE (not the array).
> **Problems:** Koko Eating Bananas (#875), Median of Two Arrays (#4)

### 9. Stack — Matching
> **Signal:** Brackets/parentheses matching / "valid sequence"
> **Use:** Push opening, pop on closing, check match.
> **Problems:** Valid Parentheses (#20)

### 10. Monotonic Stack
> **Signal:** "Next greater/smaller element" / "span" / "temperatures"
> **Use:** Stack that's always increasing/decreasing. Pop when violated.
> **Problems:** Daily Temperatures (#739), Largest Rectangle (#84)

### 11. BFS (Level-by-Level)
> **Signal:** "Shortest path" / "nearest" / "minimum steps" / "level order"
> **Use:** Queue. Process all neighbors before going deeper.
> **Time:** O(V+E)
> **Problems:** Number of Islands (#200, BFS variant), Level Order (#102)

### 12. DFS (Go Deep)
> **Signal:** "All possible paths" / "count components" / "flood fill"
> **Use:** Recursion. Visit node, recurse on all unvisited neighbors.
> **Problems:** Number of Islands (#200), Course Schedule (#207), Word Search (#79)

### 13. Backtracking (DFS + Undo)
> **Signal:** "Generate all combinations/permutations" / "find all solutions"
> **Use:** Try a choice → recurse → UNDO the choice (backtrack).
> **Time:** O(2^n) or O(n!)
> **Problems:** Subsets (#78), Permutations (#46), Combination Sum (#39), N-Queens (#51)

```
PATTERN:
    def backtrack(choices, state):
        if is_complete(state):
            result.append(state[:])
            return
        for choice in choices:
            state.append(choice)      # Make choice
            backtrack(choices, state) # Explore
            state.pop()               # UNDO choice (backtrack)
```

### 14. Dynamic Programming (Overlapping Subproblems)
> **Signal:** "Maximum/minimum/number of ways" + problem can be broken into subproblems
> **Use:** Store results of subproblems so you don't recompute them.
> **Three approaches:**
>   1. Top-Down (Memoization): recursion + cache
>   2. Bottom-Up (Tabulation): build a table iteratively
>   3. Space-optimized: if DP[i] only depends on DP[i-1], use O(1) space

```
PATTERN (Bottom-Up):
    dp = [0] * (n + 1)
    dp[0] = base_case
    for i in range(1, n + 1):
        dp[i] = f(dp[i-1], dp[i-2], ...)  # recurrence relation
    return dp[n]
```

> **Problems:** Climbing Stairs (#70), Coin Change (#322), House Robber (#198), LIS (#300)

### 15. Top-K with Heap
> **Signal:** "K largest/smallest/most frequent"
> **Use:** Maintain heap of size K. Push/pop to keep only top K.
> **Time:** O(n log k)
> **Problems:** Top K Frequent (#347), Kth Largest (#703), K Closest (#973)

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
├── "Matching / nesting"
│   └── Stack
│
├── "Next greater/smaller"
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

## BIG-O QUICK REFERENCE

| Data Structure | Access | Search | Insert | Delete |
|---------------|--------|--------|--------|--------|
| Array | O(1) | O(n) | O(n) | O(n) |
| Hash Map | N/A | O(1) | O(1) | O(1) |
| Linked List | O(n) | O(n) | O(1)* | O(1)* |
| BST (balanced) | O(log n) | O(log n) | O(log n) | O(log n) |
| Heap | O(1)** | O(n) | O(log n) | O(log n) |

\* At known position (e.g., head)
\** Peek at root only

| Algorithm | Time | Space |
|-----------|------|-------|
| Binary Search | O(log n) | O(1) |
| BFS / DFS | O(V + E) | O(V) |
| Merge Sort | O(n log n) | O(n) |
| Quick Sort | O(n log n) avg | O(log n) |
| Backtracking | O(2^n) or O(n!) | O(n) |
| DP (tabulation) | O(n) to O(n²) | O(n) to O(n²) |

---

## INTERVIEW STRATEGY (5 STEPS)

1. **Clarify** (2 min): Ask about input size, duplicates, sorted/unsorted, edge cases
2. **Brute force** (2 min): State the O(n²) solution out loud. Shows you can solve it.
3. **Optimize** (5 min): "Can I use a hash map? Two pointers? Binary search?"
4. **Code** (15 min): Write clean code. Comment as you go.
5. **Test** (5 min): Dry-run with a small example. Check edge cases.

**IF YOU'RE STUCK:**
- "Can I sort it first?" (enables binary search + two pointers)
- "Can I use extra memory?" (hash map for O(n) → O(1) lookup)
- "What would the brute force look like?" (start there, then optimize)
- "Is there a subproblem?" (dynamic programming)

---

> **You now have the foundation. Go to the Blind 75 solutions, read the Intuition
> and Approach sections, and you'll recognize the patterns from this sheet.
> Practice 3-5 problems per category. You've got this.** 🔥
