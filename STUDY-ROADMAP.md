# The Zero-to-Hero Roadmap — From "Dummy" to Clears Every Coding Interview

> **Built for:** Rohit (Manav) — Azure DevOps Engineer transitioning to AI/ML engineering.
> **Timeline:** 16 weeks (4 months) at 2 hours/day. Compress to 10 weeks at 4 hours/day.
> **Philosophy:** You don't need to be a genius. You need **pattern recognition + muscle memory**.
> 80% of interview problems reuse the same 15 patterns. Master them and you don't *think* during an interview — you *recognize* and *execute*.

---

## THE BIG PICTURE — 5 PHASES

```
Phase 0          Phase 1           Phase 2          Phase 3              Phase 4
Python           DS&A              Pattern          Blind 75             Mock
Foundations      Fundamentals      Recognition      by Category          Interviews
(Week 1-2)       (Week 3-5)        (Week 6)         (Week 7-14)          (Week 15-16)
   │                │                 │                 │                    │
   ▼                ▼                 ▼                 ▼                    ▼
Variables,      Big-O, Arrays,    "If problem      Solve all 75         Timed practice,
Loops,          Hash Maps,        says X → use      in difficulty        whiteboarding,
Functions,      Trees, Graphs     pattern Y"        order, NOT random    behavioral prep
OOP, Lists      (THE mental       (Decision        order
                 models)           tree)
```

**Golden Rule:** Never solve a problem you haven't seen the pattern for. Always learn the pattern FIRST, then solve 3-5 problems using it. This is how you build *intuition*, not *memorization*.

---

## HOW YOUR REPO MAPS TO THIS ROADMAP

Everything below already lives in your repo. The roadmap tells you **when** to read each file:

```
leetcode-blind-75/
├── python-basics/           ← Phase 0 (if you need Python refresher)
│   ├── 01-variables-and-types.py
│   ├── 02-control-flow.py
│   ├── 03-functions-and-scope.py
│   ├── 04-data-structures.py      ← lists, dicts, sets, tuples
│   ├── 05-strings.py
│   ├── 06-oop.py
│   ├── 07-errors-and-files.py
│   └── 08-advanced.py
│
├── fundamentals/            ← Phase 1 (THE most important phase)
│   ├── 00-big-o-notation.py      ← Read FIRST, before anything else
│   ├── 01-arrays-and-hash-maps.py
│   ├── 02-pointers-windows-search.py
│   ├── 03-stacks-queues-linked-lists.py
│   ├── 04-trees-heaps-trie.py
│   ├── 05-graphs.py
│   └── 06-patterns-cheat-sheet.md ← Phase 2: memorize this
│
├── khamies-algorithm-guide.md  ← Phase 2: the 8-step process
│
├── arrays-hashing/          ← Phase 3: Blind 75 (easiest first)
├── two-pointers/
├── sliding-window/
├── stack/
├── binary-search/
├── linked-list/
├── trees/
├── tries/
├── heap-priority-queue/
├── backtracking/
├── graphs/
├── dynamic-programming/     ← Phase 3: Blind 75 (hardest last)
│
└── fde-interview-battle-plan.md  ← Phase 4: interview strategy
```

---

## PHASE 0: PYTHON FOUNDATIONS (Week 1-2)

> **Skip this phase if** you can already write a function, use a list/dict, and understand classes.
> **Do this phase if** your Python is rusty or you learned by copying without understanding.

### Goal
Be comfortable writing Python from scratch — no Googling basic syntax.

### Week 1: Core Python

| Day | Read & Code | Time | What You Should Be Able to Do After |
|-----|-------------|------|--------------------------------------|
| 1 | `python-basics/01-variables-and-types.py` | 2h | Explain int, float, str, bool. Convert between types. |
| 2 | `python-basics/02-control-flow.py` | 2h | Write if/elif/else, for loops, while loops from memory |
| 3 | `python-basics/03-functions-and-scope.py` | 2h | Write functions with params, defaults, return values |
| 4 | `python-basics/04-data-structures.py` | 2h | Create list, dict, set, tuple. Know when to use each. |
| 5 | `python-basics/05-strings.py` | 2h | Slice strings, use .split(), .join(), f-strings |
| 6 | Review + practice | 2h | Write 5 small programs from scratch (no reference) |
| 7 | **REST** | — | Let it sink in |

### Week 2: Advanced Python + OOP

| Day | Read & Code | Time | What You Should Be Able to Do After |
|-----|-------------|------|--------------------------------------|
| 8 | `python-basics/06-oop.py` | 2h | Write a class with __init__, methods, inheritance |
| 9 | `python-basics/07-errors-and-files.py` | 2h | try/except, read/write files |
| 10 | `python-basics/08-advanced.py` | 2h | List comprehensions, lambda, map/filter, generators |
| 11-14 | **Practice writing small programs** | 2h/day | Build a contact book (CRUD), a simple calculator, a file parser |

### Phase 0 Exit Checklist

- [ ] I can write a Python function with type hints without looking anything up
- [ ] I know the difference between a list, dict, set, and tuple — and when to use each
- [ ] I can write a class with `__init__`, instance methods, and a class method
- [ ] I can use list comprehensions: `[x*2 for x in range(10) if x % 2 == 0]`
- [ ] I can debug a Python error message and fix it

---

## PHASE 1: DS&A FUNDAMENTALS — THE MENTAL MODELS (Week 3-5)

> **This is the most important phase.** If you understand these 7 chapters deeply,
> the Blind 75 becomes pattern-matching instead of puzzle-solving.
>
> **Do NOT skip to the Blind 75.** 90% of people who fail interviews skipped this phase.

### How to Read Each Chapter (The 4-Pass Method)

```
PASS 1: SKIM (15 min)
   Read the intro and section headers. Get the shape of the topic.
   Don't try to understand everything. Just see the landscape.

PASS 2: READ DEEPLY (45 min)
   Read every section. Understand every analogy. When you see code,
   PREDICT what it outputs before running it.

PASS 3: CODE ALONG (45 min)
   Open the .py file. Run it: python3 00-big-o-notation.py
   Modify examples. Break things. Change inputs. See what happens.

PASS 4: EXPLAIN IT (15 min)
   Close the file. Explain the topic out loud as if teaching a junior dev.
   If you can't explain it, you don't know it. Go back.
```

### Week 3: Complexity + Linear Structures

| Day | Chapter | Core Mental Model | Time |
|-----|---------|-------------------|------|
| 8 | `fundamentals/00-big-o-notation.py` | **"How does runtime GROW as input grows?"** O(1) > O(log n) > O(n) > O(n²) | 2h |
| 9 | `fundamentals/00-big-o-notation.py` (again) | Re-read. Do the exercises. Big-O is THE most tested concept. | 2h |
| 10 | `fundamentals/01-arrays-and-hash-maps.py` | Arrays = contiguous memory, O(1) index access. Hash maps = O(1) lookup via hash function. | 2h |
| 11 | `fundamentals/01-arrays-and-hash-maps.py` (cont.) | Finish the chapter. Practice the patterns. | 2h |
| 12 | `fundamentals/02-pointers-windows-search.py` | Two pointers = O(n) on sorted data. Sliding window = track a range. Binary search = halve the search space. | 2h |
| 13 | Continue + review | Run all code examples. Draw diagrams on paper. | 2h |
| 14 | **REST** | — | — |

### Week 4: Non-Linear Structures

| Day | Chapter | Core Mental Model | Time |
|-----|---------|-------------------|------|
| 15 | `fundamentals/03-stacks-queues-linked-lists.py` (Part 1: Stack & Queue) | Stack = LIFO (last in, first out). Queue = FIFO. Think: stack of plates vs. line at Starbucks. | 2h |
| 16 | `fundamentals/03-stacks-queues-linked-lists.py` (Part 2: Linked Lists) | Linked list = nodes with pointers. Not contiguous. O(1) insert/delete if you have the node. | 2h |
| 17 | Continue linked lists | Draw pointer manipulations on paper. This is the #1 place people get confused. | 2h |
| 18 | `fundamentals/04-trees-heaps-trie.py` (Part 1: Trees & BST) | Tree = hierarchy. BST: left < node < right. Enables O(log n) search. | 2h |
| 19 | `fundamentals/04-trees-heaps-trie.py` (Part 2: Heaps & Trie) | Heap = priority queue (min/max at top). Trie = prefix tree for strings. | 2h |
| 20 | Review all structures | Draw each structure from memory on blank paper | 2h |
| 21 | **REST** | — | — |

### Week 5: Graphs + Integration

| Day | Chapter | Core Mental Model | Time |
|-----|---------|-------------------|------|
| 22 | `fundamentals/05-graphs.py` (Part 1: BFS) | BFS = level-by-level exploration. Uses a queue. Finds shortest path in unweighted graph. | 2h |
| 23 | `fundamentals/05-graphs.py` (Part 2: DFS) | DFS = go deep, backtrack. Uses recursion/stack. Good for connectivity, cycles, paths. | 2h |
| 24 | Continue graphs | Practice BFS/DFS on paper. Trace through the code. | 2h |
| 25 | RE-READ `fundamentals/00-big-o-notation.py` | Now that you know all structures, Big-O for each should click. | 2h |
| 26 | Review ALL fundamentals chapters | Self-test: can you explain each structure to an imaginary junior dev? | 2h |
| 27 | Write each structure from scratch | Implement: Stack, Queue, LinkedList, BST, Heap — without looking at reference | 2h |
| 28 | **REST** | — | — |

### Phase 1 Exit Checklist

- [ ] I can explain Big-O for all major data structure operations from memory
- [ ] I can implement a hash map lookup pattern in under 60 seconds
- [ ] I can trace a two-pointer algorithm on paper with correct variable states
- [ ] I can draw a binary search tree and perform search, insert, and all 3 traversals
- [ ] I can explain BFS vs DFS and when to use each, with examples
- [ ] I can implement a stack and queue from scratch using a Python list
- [ ] I can reverse a linked list on paper (the classic interview question)
- [ ] I know the time/space complexity of: dict lookup, list append, set add, heap push

---

## PHASE 2: PATTERN RECOGNITION (Week 6)

> **This phase changes everything.** Instead of seeing 75 separate problems,
> you'll see 15 patterns with 5 problems each. That's the difference between
> memorization and mastery.

### Week 6: The Decision Tree

| Day | What to Do | Time | Outcome |
|-----|------------|------|---------|
| 29 | Read `fundamentals/06-patterns-cheat-sheet.md` (full) | 2h | Understand all 15 patterns at a high level |
| 30 | Read it AGAIN. Make flashcards for each pattern. | 2h | Memorize: Signal words → Pattern → Time/Space |
| 31 | Read `khamies-algorithm-guide.md` — the 8-step process | 2h | Internalize: Understand → Formalize → Examples → Brute → Optimize → Code → Test → Communicate |
| 32 | Read Khamies FGCC framework + KSum family | 2h | Understand how patterns group problems |
| 33 | Practice: take 10 random Blind 75 problems. DON'T solve them. Just identify the pattern. | 2h | Train your brain to recognize patterns |
| 34 | Practice: take 10 more. Identify pattern + write pseudo-code only. | 2h | Bridge recognition → execution |
| 35 | **REST** | — | — |

### The 15 Patterns (Memorize This Table)

```
┌─────────────────────────────────────┬──────────────────────────────────────────────┐
│ PATTERN                             │ SIGNAL WORDS IN THE PROBLEM                  │
├─────────────────────────────────────┼──────────────────────────────────────────────┤
│ 1. Hash Map Lookup                  │ "Find two elements that...", "complement"    │
│ 2. Frequency Counter                │ "Count occurrences", "most frequent", "top K"│
│ 3. Two Pointers (Opposite Ends)     │ "Sorted array" + "find pair" / "palindrome"  │
│ 4. Two Pointers (Same Direction)    │ "Remove duplicates", "in-place modification" │
│ 5. Sliding Window (Fixed)           │ "Subarray of size K", "max sum of K consec." │
│ 6. Sliding Window (Variable)        │ "Longest/shortest substring that..."          │
│ 7. Binary Search                    │ "Sorted" + "find", "minimum/maximum that..." │
│ 8. BFS (Level Order)                │ "Shortest path", "level by level", "nearest" │
│ 9. DFS (Recursive)                  │ "All paths", "islands", "connected", "cycle" │
│ 10. Topological Sort                │ "Dependency", "ordering", "prerequisites"    │
│ 11. Monotonic Stack                 │ "Next greater/smaller element", "temperatures"│
│ 12. Heap / Priority Queue           │ "Top K", "Kth largest/smallest", "merge K"   │
│ 13. Backtracking (DFS + Choices)    │ "All combinations", "permutations", "subsets"│
│ 14. Dynamic Programming             │ "Maximum/minimum", "count ways", "optimal"   │
│ 15. Trie                            │ "Prefix", "word dictionary", "autocomplete"  │
└─────────────────────────────────────┴──────────────────────────────────────────────┘
```

### Phase 2 Exit Checklist

- [ ] I can identify the correct pattern for a problem within 30 seconds of reading it
- [ ] I have memorized the signal words → pattern mapping
- [ ] I know the Khamies 8-step process and can apply it to any problem
- [ ] I can write pseudo-code for a hash map, two-pointer, and sliding window problem from memory
- [ ] I can explain the difference between BFS and DFS as a pattern choice

---

## PHASE 3: BLIND 75 BY CATEGORY — DIFFICULTY LADDER (Week 7-14)

> **CRITICAL:** Solve in this order — easiest patterns first, hardest last.
> Each category builds on the previous. Do NOT jump to DP before you've mastered arrays.
>
> **How to solve each problem (the 45-minute method):**
> ```
> Minutes 0-5:   Read the problem. Identify the pattern. Write the approach in English.
> Minutes 5-15:  Code the solution. If stuck after 10 minutes, read the Intuition section.
> Minutes 15-25: Dry run your code by hand on the example input. Fix bugs.
> Minutes 25-30: Check the solution file. Compare approaches. What did you miss?
> Minutes 30-40: Re-code from memory without looking. This builds muscle memory.
> Minutes 40-45: Read Edge Cases + Interview Tips. Add notes to your flashcards.
> ```

### Solving Order — From Easiest to Hardest Pattern

```
Tier 1 — Beginner Friendly (Week 7-8)
   arrays-hashing → two-pointers → sliding-window → binary-search

Tier 2 — Intermediate (Week 9-11)
   stack → linked-list → trees → heap-priority-queue

Tier 3 — Advanced (Week 12-13)
   tries → graphs → backtracking

Tier 4 — Expert (Week 14)
   dynamic-programming
```

---

### Tier 1: BEGINNER PATTERNS (Week 7-8) — 25 problems

#### Week 7: Arrays & Hashing + Two Pointers (12 problems)

| Day | Category | Problems | Focus |
|-----|----------|----------|-------|
| 36 | arrays-hashing | #217 Contains Duplicate, #242 Valid Anagram | Hash map lookup pattern — warmup |
| 37 | arrays-hashing | #1 Two Sum, #49 Group Anagrams | Complement lookup + frequency counter |
| 38 | arrays-hashing | #347 Top K Frequent, #238 Product Except Self | Frequency + prefix/suffix arrays |
| 39 | arrays-hashing | #36 Valid Sudoku | Hash set validation |
| 40 | two-pointers | #125 Valid Palindrome, #704 Binary Search (easy) | Two pointers opposite ends |
| 41 | two-pointers | #167 Two Sum II, #15 3Sum | Sorted array → two pointers |
| 42 | two-pointers | #11 Container With Most Water | Greedy two pointers |

#### Week 8: Sliding Window + Binary Search (13 problems)

| Day | Category | Problems | Focus |
|-----|----------|----------|-------|
| 43 | sliding-window | #121 Best Time to Buy/Sell Stock | Single pass tracking min/max |
| 44 | sliding-window | #3 Longest Substring Without Repeating | Variable sliding window + set |
| 45 | sliding-window | #424 Longest Repeating Character Replacement | Variable window + frequency map |
| 46 | sliding-window | #76 Minimum Window Substring (HARD) | Hardest sliding window — take your time |
| 47 | sliding-window | #239 Sliding Window Maximum (HARD) | Deque-based window |
| 48 | binary-search | #704 Binary Search, #35 Search Insert Position | Standard binary search |
| 49 | binary-search | #33 Search in Rotated Sorted Array, #153 Find Minimum | Modified binary search |
| 50 | binary-search | #875 Koko Eating Bananas, #981 Time Based KV Store | Binary search on answer space |
| 51 | binary-search | #4 Median of Two Sorted Arrays (HARD) | The hardest binary search on Blind 75 |

**Tier 1 Exit Checklist:**
- [ ] I can solve any hash map problem in under 15 minutes
- [ ] I can set up a two-pointer solution without thinking
- [ ] I can identify when to use a fixed vs variable sliding window
- [ ] I can write a correct binary search from memory (off-by-one errors are gone)
- [ ] I can identify the "binary search on answer" pattern (e.g., Koko Eating Bananas)

---

### Tier 2: INTERMEDIATE PATTERNS (Week 9-11) — 34 problems

#### Week 9: Stack + Linked List (18 problems)

| Day | Category | Problems | Focus |
|-----|----------|----------|-------|
| 52 | stack | #20 Valid Parentheses | Stack for matching pairs |
| 53 | stack | #155 Min Stack | Auxiliary stack for tracking state |
| 54 | stack | #150 Evaluate Reverse Polish Notation | Stack as computation |
| 55 | stack | #22 Generate Parentheses | Stack + backtracking |
| 56 | stack | #739 Daily Temperatures | Monotonic stack pattern |
| 57 | stack | #853 Car Fleet, #402 Remove K Digits | Monotonic stack (harder) |
| 58 | linked-list | #206 Reverse Linked List | THE classic. Draw pointers on paper. |
| 59 | linked-list | #21 Merge Two Sorted Lists | Dummy node pattern |
| 60 | linked-list | #143 Reorder List | Slow/fast pointer + reverse + merge |
| 61 | linked-list | #19 Remove Nth Node From End | Two-pass → one-pass with offset |
| 62 | linked-list | #141 Linked List Cycle, #287 Find Duplicate Number | Floyd's cycle detection (tortoise & hare) |
| 63 | linked-list | #2 Add Two Numbers, #23 Merge K Sorted Lists (HARD) | Dummy node + heap |

#### Week 10: Trees (13 problems)

| Day | Category | Problems | Focus |
|-----|----------|----------|-------|
| 64 | trees | #226 Invert Binary Tree, #104 Maximum Depth | Basic tree recursion — THE foundation |
| 65 | trees | #100 Same Tree, #572 Subtree of Another Tree | Tree comparison patterns |
| 66 | trees | #235 LCA of BST, #98 Validate BST | BST property utilization |
| 67 | trees | #102 Binary Tree Level Order Traversal | BFS on trees |
| 68 | trees | #199 Binary Tree Right Side View | BFS variation |
| 69 | trees | #105 Construct Binary Tree from Preorder + Inorder | THE hardest tree construction problem |
| 70 | trees | #124 Binary Tree Maximum Path Sum (HARD) | Post-order + global max tracking |
| 71 | trees | #230 Kth Smallest Element in BST | In-order traversal = sorted order |

#### Week 11: Heap / Priority Queue (3 problems) + Buffer Week

| Day | Category | Problems | Focus |
|-----|----------|----------|-------|
| 72 | heap-priority-queue | #703 Kth Largest Element in Stream | Min-heap basics |
| 73 | heap-priority-queue | #1046 Last Stone Weight | Max-heap simulation |
| 74 | heap-priority-queue | #295 Find Median from Data Stream (HARD) | Two heaps: max-heap (lower half) + min-heap (upper half) |
| 75-77 | **BUFFER WEEK** | Re-solve any problems you struggled with | The goal is mastery, not speed |

**Tier 2 Exit Checklist:**
- [ ] I can reverse a linked list in under 5 minutes
- [ ] I can detect a cycle using Floyd's algorithm and explain WHY it works
- [ ] I can write tree BFS (level order) and DFS (pre/in/post-order) from memory
- [ ] I understand the monotonic stack pattern and can identify when to use it
- [ ] I can implement a min-heap and max-heap using Python's `heapq`
- [ ] I can construct a tree from traversal arrays

---

### Tier 3: ADVANCED PATTERNS (Week 12-13) — 16 problems

#### Week 12: Tries + Graphs (7 problems)

| Day | Category | Problems | Focus |
|-----|----------|----------|-------|
| 78 | tries | #208 Implement Trie, #212 Word Search II | Trie construction + DFS |
| 79 | tries | #211 Design Add and Search Words | Trie with wildcard support |
| 80 | graphs | #200 Number of Islands | DFS/BFS on a grid |
| 81 | graphs | #133 Clone Graph | HashMap + BFS/DFS |
| 82 | graphs | #207 Course Schedule, #210 Course Schedule II | Topological sort (cycle detection) |

#### Week 13: Backtracking (9 problems)

| Day | Category | Problems | Focus |
|-----|----------|----------|-------|
| 83 | backtracking | #78 Subsets, #90 Subsets II | Generate all subsets (with/without duplicates) |
| 84 | backtracking | #39 Combination Sum, #40 Combination Sum II | Generate combinations with target sum |
| 85 | backtracking | #46 Permutations, #17 Letter Combinations | Generate all orderings |
| 86 | backtracking | #131 Palindrome Partitioning | Backtracking + palindrome check |
| 87 | backtracking | #79 Word Search, #51 N-Queens (HARD) | Grid backtracking + the classic hard problem |

**Tier 3 Exit Checklist:**
- [ ] I can implement a Trie from scratch with insert, search, startsWith
- [ ] I can convert a 2D grid into a graph problem and apply BFS/DFS
- [ ] I can detect a cycle in a directed graph using Kahn's algorithm or DFS
- [ ] I can write a backtracking template from memory (choose → explore → un-choose)
- [ ] I can solve N-Queens and explain the backtracking approach

---

### Tier 4: EXPERT — DYNAMIC PROGRAMMING (Week 14) — 11 problems

> **DP is where most candidates fail.** It's also where you can set yourself apart.
> The key insight: **every DP problem is "memoize the recursive solution."**
> Start with the recursive approach, add caching, then convert to bottom-up.

| Day | Category | Problems | Focus |
|-----|----------|----------|-------|
| 88 | dynamic-programming | #70 Climbing Stairs, #198 House Robber | 1D DP — Fibonacci-like. Start here. |
| 89 | dynamic-programming | #213 House Robber II, #91 Decode Ways | Circular DP + string DP |
| 90 | dynamic-programming | #322 Coin Change, #152 Maximum Product Subarray | Classic DP patterns |
| 91 | dynamic-programming | #300 Longest Increasing Subsequence | O(n²) → O(n log n) with binary search |
| 92 | dynamic-programming | #139 Word Break, #55 Jump Game | String DP + greedy alternative |
| 93 | dynamic-programming | #45 Jump Game II, #64 Minimum Path Sum | Greedy DP + 2D grid DP |
| 94 | dynamic-programming | #5 Longest Palindromic Substring | Center expansion vs DP table |

**DP Problem-Solving Framework (Always Follow This):**
```
Step 1: Write the RECURSIVE solution first (brute force)
        → What's the decision at each step? What are the base cases?

Step 2: Draw the recursion tree on paper
        → Do you see repeated subproblems? That's your signal for DP.

Step 3: Add MEMOIZATION (top-down DP)
        → Cache results of recursive calls. This is still recursion + a dict.

Step 4: Convert to TABULATION (bottom-up DP)
        → Build a table from base cases up. Usually O(n) space or better.

Step 5: Optimize space if possible
        → Can you replace the table with 2-3 variables? (e.g., Fibonacci → O(1) space)
```

**Tier 4 Exit Checklist:**
- [ ] I can identify a DP problem (optimal substructure + overlapping subproblems)
- [ ] I can write the recursive brute force, then add memoization, then convert to tabulation
- [ ] I can reduce a 1D DP table to O(1) space when possible
- [ ] I can solve Coin Change and explain the recurrence relation
- [ ] I can explain why House Robber is DP and not greedy

---

## PHASE 4: MOCK INTERVIEWS & SPEED (Week 15-16)

> You know the patterns. You've solved the problems. Now: **can you do it
> under pressure, out loud, with someone watching?**

### Week 15: Speed + Communication

| Day | Activity | Time | Goal |
|-----|----------|------|------|
| 95 | Re-solve 5 Easy problems TIMED (15 min each) | 2h | Verify you can solve easy problems fast |
| 96 | Re-solve 5 Medium problems TIMED (25 min each) | 2h | Medium problems in under 25 minutes |
| 97 | Re-solve 3 Hard problems TIMED (35 min each) | 2h | Hard problems in under 35 minutes |
| 98 | **Whiteboard practice** — solve on paper, no computer | 2h | Write code by hand, narrate your thinking |
| 99 | **Communication practice** — explain solutions out loud | 2h | "Here's my approach..." "The time complexity is..." |
| 100 | Read `fde-interview-battle-plan.md` — full guide | 2h | Connect DS&A skills to your interview narrative |
| 101 | **REST** | — | — |

### Week 16: Full Mock Interviews

| Day | Activity | Time | Goal |
|-----|----------|------|------|
| 102 | Mock Interview 1: Pick 1 easy + 1 medium from random categories | 45m | Simulate real interview conditions |
| 103 | Mock Interview 2: Pick 1 medium + 1 hard from random categories | 45m | Handle pressure + unknown patterns |
| 104 | Mock Interview 3: Pick 2 mediums from your weakest category | 45m | Strengthen weaknesses |
| 105 | Mock Interview 4: Full 45-min session (1 hard or 2 mediums) | 45m | Endurance + communication |
| 106 | Review ALL mistakes from mock interviews | 2h | Create a "mistake journal" |
| 107 | Final review: re-read patterns cheat sheet + Big-O | 2h | Lock in the fundamentals |
| 108 | **REST. You're ready.** | — | — |

### Phase 4 Exit Checklist

- [ ] I can solve any Easy Blind 75 problem in under 15 minutes
- [ ] I can solve any Medium Blind 75 problem in under 25 minutes
- [ ] I can communicate my approach clearly before coding
- [ ] I can analyze time/space complexity without hesitation
- [ ] I can handle "what if the input was..." follow-up questions
- [ ] I have a mistake journal and I've reviewed it

---

## THE DAILY ROUTINE (Non-Negotiable)

Every day you study, follow this structure:

```
┌──────────────────────────────────────────────────────────────┐
│                    THE 2-HOUR DAILY BLOCK                     │
│                                                              │
│  Minutes 0-10:   WARMUP                                      │
│    Re-solve yesterday's problem from memory. No reference.   │
│    This is spaced repetition — the secret to retention.      │
│                                                              │
│  Minutes 10-55:  NEW LEARNING (45 min)                       │
│    Read a fundamentals chapter OR solve a new problem.       │
│    Use the 45-minute method described in Phase 3.            │
│                                                              │
│  Minutes 55-65:  BREAK (10 min)                              │
│    Walk around. Let your brain process.                     │
│                                                              │
│  Minutes 65-115: DEEP PRACTICE (50 min)                      │
│    Solve 1-2 more problems using today's pattern.            │
│    OR re-solve problems from 2 days ago (spaced repetition). │
│                                                              │
│  Minutes 115-120: JOURNAL (5 min)                            │
│    Write down: What pattern did I learn? What tripped me up? │
│    What should I review tomorrow?                            │
└──────────────────────────────────────────────────────────────┘
```

### The Spaced Repetition Schedule

To actually REMEMBER what you learn, review on this schedule:

```
Day 1:   Learn problem A
Day 2:   Re-solve A from memory (warmup) + Learn B
Day 4:   Re-solve A again (should be faster now) + Learn C
Day 7:   Re-solve A one final time (should be effortless) + Learn D
Day 14:  A is permanently in your muscle memory
```

**This is why re-solving is more important than solving new problems.**
A problem you've solved once and forgotten is worth nothing.
A problem you've solved 4 times is a permanent weapon.

---

## THE MISTAKE JOURNAL

Keep a running document (or a section in each category's README) tracking:

```markdown
## Mistake Journal

### Pattern: Two Pointers
- [ ] 3Sum: Forgot to skip duplicates. Added `while nums[i] == nums[i-1]: i += 1`
- [ ] Container With Most Water: Initially tried brute force. Should recognize greedy two-pointer.

### Pattern: Sliding Window
- [ ] Longest Substring Without Repeating: Used a list instead of a set for lookup. O(n) → O(n²).

### Pattern: Binary Search
- [ ] Search in Rotated Array: Off-by-one error on mid calculation. Remember: `mid = left + (right - left) // 2`
```

Review this journal every Sunday. Patterns of mistakes reveal your blind spots.

---

## INTERVIEW CHEAT SHEET — THE FIRST 60 SECONDS

When the interviewer gives you a problem, do this IN ORDER:

```
1. (0-30 sec)  READ the problem twice. Don't touch the keyboard.

2. (30-60 sec) ASK CLARIFYING QUESTIONS:
   • "Can the input be empty?" "Are there negative numbers?"
   • "Is the array sorted?" "Can there be duplicates?"
   • "Should I optimize for time or space?"

3. (60-120 sec) IDENTIFY THE PATTERN (out loud):
   • "I see this is a two-sum variant, so I'm thinking hash map..."
   • "The array is sorted and we're searching, so binary search..."
   • "We need all combinations, so backtracking..."

4. (2-5 min)   DESCRIBE YOUR APPROACH in English before coding:
   • "I'll iterate through the array, maintaining a hash map of..."
   • "The time complexity will be O(n), space O(n)..."
   • "Let me walk through an example..." (dry run on the whiteboard)

5. (5-30 min)  CODE IT. Narrate as you write. Think out loud.

6. (30-35 min) DRY RUN. Trace through your code with the example input.

7. (35-40 min) DISCUSS: complexity, edge cases, trade-offs, follow-ups.
```

**Never start coding within the first 2 minutes.** Interviewers want to see your THINKING, not your typing speed.

---

## CATEGORY DIFFICULTY MAP

Not all categories are equal. Here's how much time to budget per problem:

```
┌──────────────────────┬─────────────┬─────────────────────────────────────┐
│ Category             │ Avg Time    │ Why                                 │
├──────────────────────┼─────────────┼─────────────────────────────────────┤
│ Arrays & Hashing     │ 15-20 min   │ Straightforward pattern recognition │
│ Two Pointers         │ 15-25 min   │ Need to get pointer movement right  │
│ Sliding Window       │ 20-30 min   │ Edge cases in window bounds         │
│ Binary Search        │ 20-30 min   │ Off-by-one errors are deadly        │
│ Stack                │ 15-25 min   │ Usually straightforward once known  │
│ Linked List          │ 20-30 min   │ Pointer manipulation needs care     │
│ Trees                │ 20-35 min   │ Recursion can be tricky to get right│
│ Heap / Priority Q    │ 25-35 min   │ Heap operations + problem logic     │
│ Tries                │ 25-35 min   │ Building the Trie takes time        │
│ Graphs               │ 25-40 min   │ BFS/DFS setup + visited tracking    │
│ Backtracking         │ 30-45 min   │ Many recursive paths to manage      │
│ Dynamic Programming  │ 30-45 min   │ Getting the recurrence is the crux  │
└──────────────────────┴─────────────┴─────────────────────────────────────┘
```

---

## TRACKING YOUR PROGRESS

Use this tracker. Print it. Check boxes as you go.

### Fundamentals Progress

```
[ ] Big-O Notation              (fundamentals/00)
[ ] Arrays & Hash Maps          (fundamentals/01)
[ ] Pointers, Windows, Search   (fundamentals/02)
[ ] Stacks, Queues, Linked Lists(fundamentals/03)
[ ] Trees, Heaps, Trie          (fundamentals/04)
[ ] Graphs                      (fundamentals/05)
[ ] Patterns Cheat Sheet        (fundamentals/06)
```

### Blind 75 Progress

```
TIER 1 — Beginner
[ ] [E] #217 Contains Duplicate          (arrays-hashing)
[ ] [E] #242 Valid Anagram               (arrays-hashing)
[ ] [E] #1   Two Sum                     (arrays-hashing)
[ ] [M] #49  Group Anagrams              (arrays-hashing)
[ ] [M] #347 Top K Frequent Elements     (arrays-hashing)
[ ] [M] #238 Product of Array Except Self(arrays-hashing)
[ ] [M] #36  Valid Sudoku                (arrays-hashing)
[ ] [E] #125 Valid Palindrome            (two-pointers)
[ ] [E] #704 Binary Search               (binary-search) *
[ ] [M] #167 Two Sum II                  (two-pointers)
[ ] [M] #15  3Sum                        (two-pointers)
[ ] [M] #11  Container With Most Water   (two-pointers)
[ ] [E] #121 Best Time Buy/Sell Stock    (sliding-window)
[ ] [M] #3   Longest Substring No Repeat (sliding-window)
[ ] [M] #424 Longest Repeating Char Repl.(sliding-window)
[ ] [H] #76  Minimum Window Substring    (sliding-window)
[ ] [H] #239 Sliding Window Maximum      (sliding-window)
[ ] [E] #35  Search Insert Position      (binary-search)
[ ] [M] #33  Search in Rotated Sorted    (binary-search)
[ ] [M] #153 Find Minimum in Rotated     (binary-search)
[ ] [M] #875 Koko Eating Bananas         (binary-search)
[ ] [M] #981 Time Based Key-Value Store  (binary-search)
[ ] [H] #4   Median of Two Sorted Arrays (binary-search)

TIER 2 — Intermediate
[ ] [E] #20  Valid Parentheses           (stack)
[ ] [M] #155 Min Stack                   (stack)
[ ] [M] #150 Evaluate Reverse Polish     (stack)
[ ] [M] #22  Generate Parentheses        (stack)
[ ] [M] #739 Daily Temperatures          (stack)
[ ] [M] #853 Car Fleet                   (stack)
[ ] [M] #402 Remove K Digits             (stack)
[ ] [E] #206 Reverse Linked List         (linked-list)
[ ] [E] #21  Merge Two Sorted Lists      (linked-list)
[ ] [M] #143 Reorder List               (linked-list)
[ ] [M] #19  Remove Nth Node From End    (linked-list)
[ ] [E] #141 Linked List Cycle           (linked-list)
[ ] [M] #287 Find the Duplicate Number   (linked-list)
[ ] [M] #2   Add Two Numbers             (linked-list)
[ ] [H] #23  Merge K Sorted Lists        (linked-list)
[ ] [E] #226 Invert Binary Tree          (trees)
[ ] [E] #104 Maximum Depth of Binary Tree(trees)
[ ] [E] #100 Same Tree                   (trees)
[ ] [E] #572 Subtree of Another Tree     (trees)
[ ] [M] #235 Lowest Common Ancestor BST  (trees)
[ ] [M] #98  Validate BST                (trees)
[ ] [M] #102 Binary Tree Level Order     (trees)
[ ] [M] #199 Binary Tree Right Side View (trees)
[ ] [M] #105 Construct BT Preorder+Inord (trees)
[ ] [H] #124 Binary Tree Maximum Path Sum(trees)
[ ] [M] #230 Kth Smallest in BST         (trees)
[ ] [E] #703 Kth Largest in Stream        (heap-priority-queue)
[ ] [E] #1046 Last Stone Weight          (heap-priority-queue)
[ ] [H] #295 Find Median Data Stream     (heap-priority-queue)

TIER 3 — Advanced
[ ] [M] #208 Implement Trie              (tries)
[ ] [M] #211 Design Add/Search Words     (tries)
[ ] [H] #212 Word Search II              (tries)
[ ] [M] #200 Number of Islands           (graphs)
[ ] [M] #133 Clone Graph                 (graphs)
[ ] [M] #207 Course Schedule             (graphs)
[ ] [M] #210 Course Schedule II          (graphs)
[ ] [M] #78  Subsets                     (backtracking)
[ ] [M] #90  Subsets II                  (backtracking)
[ ] [M] #39  Combination Sum             (backtracking)
[ ] [M] #40  Combination Sum II          (backtracking)
[ ] [M] #46  Permutations                (backtracking)
[ ] [M] #17  Letter Combos of Phone      (backtracking)
[ ] [M] #131 Palindrome Partitioning     (backtracking)
[ ] [M] #79  Word Search                 (backtracking)
[ ] [H] #51  N-Queens                    (backtracking)

TIER 4 — Expert
[ ] [E] #70  Climbing Stairs             (dynamic-programming)
[ ] [M] #198 House Robber                (dynamic-programming)
[ ] [M] #213 House Robber II             (dynamic-programming)
[ ] [M] #91  Decode Ways                 (dynamic-programming)
[ ] [M] #322 Coin Change                 (dynamic-programming)
[ ] [M] #152 Maximum Product Subarray    (dynamic-programming)
[ ] [M] #300 Longest Increasing Subseq   (dynamic-programming)
[ ] [M] #139 Word Break                  (dynamic-programming)
[ ] [M] #55  Jump Game                   (dynamic-programming)
[ ] [M] #45  Jump Game II                (dynamic-programming)
[ ] [M] #64  Minimum Path Sum            (dynamic-programming)
[ ] [M] #5   Longest Palindromic Substr  (dynamic-programming)
```

---

## COMMON PITFALLS — READ THIS BEFORE YOU START

### Pitfall 1: "I'll just memorize the solutions"
**Why it fails:** Interviewers change one word in the problem and your memorized solution breaks.
**Fix:** Focus on the PATTERN, not the code. If you know "this is a sliding window problem," you can re-derive the code.

### Pitfall 2: "I'll watch YouTube videos instead of coding"
**Why it falls:** Watching feels like learning but it's passive. You can't code by watching.
**Fix:** For every 30 minutes of watching, spend 30 minutes coding. Reading docs > watching videos.

### Pitfall 3: "I'll solve problems in random order"
**Why it fails:** You never build mastery in any pattern. Each problem feels new and scary.
**Fix:** Solve by category (all array problems together, then all tree problems, etc.). Patterns compound.

### Pitfall 4: "Easy problems are beneath me"
**Why it fails:** Easy problems contain the CORE PATTERNS that hard problems build on.
**Fix:** Do ALL easy problems first. They take 10 minutes each and teach you the pattern fast.

### Pitfall 5: "I don't need to write tests"
**Why it fails:** In interviews, you must verify your own code. If you can't find your own bugs, you fail.
**Write test cases for EVERY solution.** Include: empty input, single element, duplicates, negative numbers.

### Pitfall 6: "I understand it, so I don't need to re-solve it"
**Why it falls:** Understanding ≠ recall. You'll forget a solution in 3 days if you don't review.
**Fix:** Spaced repetition (see above). Re-solve after 1 day, 3 days, 7 days.

### Pitfall 7: "Dynamic programming is impossible, I'll skip it"
**Why it fails:** DP is ~15% of the Blind 75 and appears in nearly every FAANG interview.
**Fix:** Start with Climbing Stairs (it's literally Fibonacci). Then House Robber. Build up slowly. Every DP problem is "memoize the recursion."

---

## THE 3 RULES OF INTERVIEW CODING

### Rule 1: ALWAYS Brute Force First
Even if you know the optimal solution, state the brute force approach first.
```
"The brute force approach would be to check every pair, which is O(n²)..."
"But we can optimize using a hash map to get O(n)..."
```
This shows the interviewer you can solve problems AND optimize.

### Rule 2: THINK OUT LOUD
Silence is death in an interview. Narrate everything:
```
"I'm looking at this problem and I see the array is sorted, which makes me think
binary search... let me think about what we're searching for... we want the
minimum value that satisfies the condition, so I'll binary search on the answer..."
```

### Rule 3: IF STUCK, DRAW ON PAPER
If you're stuck for more than 2 minutes:
1. Draw the input on paper
2. Manually solve it by hand (no code)
3. Observe YOUR thought process — that IS the algorithm
```
"The algorithm is just whatever your brain does to solve it by hand.
You just need to formalize it into code." — Every CS professor ever
```

---

## AFTER THE BLIND 75 — WHAT'S NEXT?

Once you've completed the Blind 75, you're interview-ready for most companies.
To go further:

1. **NeetCode 150** — 75 more problems for deeper coverage (neetcode.io)
2. **Company-specific lists** — LeetCode has "Top Facebook Questions," "Top Google Questions," etc.
3. **System Design** — You already have this in `system-design/` folder. Pair it with LeetCode.
4. **Behavioral** — Use your `fde-interview-battle-plan.md` for the narrative.
5. **Speed runs** — Re-solve all 75 problems in 2 weeks. By the end, patterns are automatic.

---

## SUMMARY: THE ONE-PAGE VERSION

```
WHAT TO DO (in order):

1.  Learn Python basics (if needed)              → python-basics/
2.  Master DS&A fundamentals                      → fundamentals/ (7 chapters)
3.  Memorize the 15 patterns                      → fundamentals/06-patterns-cheat-sheet.md
4.  Learn the 8-step problem-solving process      → khamies-algorithm-guide.md
5.  Solve Blind 75 in difficulty order            → Tier 1 → Tier 2 → Tier 3 → Tier 4
6.  Re-solve every problem 3x (spaced repetition) → 1 day, 3 days, 7 days apart
7.  Keep a mistake journal                        → Review every Sunday
8.  Practice timed + on whiteboard                → Phase 4
9.  Do mock interviews                            → Simulate real conditions
10. Walk in confident                             → You earned it

WHAT NOT TO DO:

✗ Don't skip fundamentals to jump into problems
✗ Don't solve in random order
✗ Don't memorize solutions (learn patterns)
✗ Don't skip easy problems
✗ Don't skip DP
✗ Don't skip writing tests
✗ Don't skip re-solving (spaced repetition)
✗ Don't stay silent in interviews
```

---

> **Remember:** Every senior engineer was once a beginner who didn't know what a hash map was.
> The difference between those who pass and those who fail isn't talent — it's **deliberate practice**.
> You have the materials. You have the roadmap. Now execute.
>
> **Start today with `fundamentals/00-big-o-notation.py`. Everything else flows from there.**
