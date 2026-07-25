# How to Solve Algorithm Problems — Complete Deep-Dive Analysis

> **Source:** "How to Solve Algorithm Problems — Make Coding Interview Preparation Less Painful" by Waleed Khamies
> **Pages:** 121 | **Focus:** Systematic problem-solving framework, KSum family, FGCC framework, pattern recognition

---

## TABLE OF CONTENTS

1. [The Khamies 8-Step Problem-Solving Process](#step1)
2. [Interview Assessment Factors (What Interviewers Look For)](#step2)
3. [KSum Family Deep Dive (2Sum, 3Sum, KSum)](#step3)
4. [FGCC Framework (Focus, Group, Convert, Communicate)](#step4)
5. [Top 3 Algorithm Techniques](#step5)
6. [6 Supplement Problems with Full Solutions](#step6)
7. [The Complete Learning Roadmap](#step7)

---

## The Khamies 8-Step Problem-Solving Process

> This is the core methodology. Unlike most resources that say "just practice," Khamies gives you a **repeatable 8-step process** for EVERY problem.

```
┌──────────────────────────────────────────────────────────────────┐
│         THE 8-STEP ALGORITHM PROBLEM-SOLVING PROCESS             │
│                                                                  │
│  Step 1: UNDERSTAND THE PROBLEM                                  │
│    "Reading the question is half of the answer."                 │
│    Read carefully. Identify hidden information between lines.    │
│                                                                  │
│  Step 2: FORMALIZE THE PROBLEM                                   │
│    Convert to a clear input → output question.                   │
│    "Given X, return Y."                                          │
│                                                                  │
│  Step 3: REPEAT READING THE QUESTION                             │
│    Read it AGAIN. Did you miss:                                  │
│    • Is the array sorted? (enables binary search)               │
│    • Are elements unique? (affects deduplication)                │
│    • Can there be negative numbers?                              │
│                                                                  │
│  Step 4: BRING INPUT EXAMPLES (3 types)                          │
│    Example 1: EMPTY-CASE input (empty array, null, "")          │
│    Example 2: MEDIUM-CASE input (typical, general flow)         │
│    Example 3: CORNER-CASE input (duplicates, negatives, etc.)   │
│                                                                  │
│  Step 5: DEVELOP A BRUTE-FORCE SOLUTION                          │
│    Quick, dirty, not efficient — but CORRECT.                    │
│    Write the obvious nested-loop solution.                       │
│    This proves you can solve it.                                 │
│                                                                  │
│  Step 6: ANALYZE BRUTE-FORCE COMPLEXITY                          │
│    State time AND space complexity of the brute-force.           │
│    "This is O(n²) time, O(1) space."                             │
│    THIS IS CRITICAL: the bottleneck analysis guides optimization.│
│                                                                  │
│  Step 7: OPTIMIZE THE BRUTE-FORCE                                │
│    "This is the difference between a beginner and experienced    │
│     candidate."                                                  │
│    Go line-by-line. Find the bottleneck.                         │
│    Apply patterns: hash map, two pointers, sorting, etc.        │
│                                                                  │
│  Step 8: ANALYZE OPTIMIZED COMPLEXITY                            │
│    State the new time and space complexity.                      │
│    "Optimized to O(n) time, O(n) space using a hash map."       │
│                                                                  │
│  "If you reached this stage, congratulations! That means you     │
│   have passed your technical interview." — Khamies              │
└──────────────────────────────────────────────────────────────────┘
```

### Why the 8-Step Process Works

```
THE KEY INSIGHT: Optimization is not about being clever.
It's about SYSTEMATIC BOTTLENECK ELIMINATION.

Step 5 (Brute Force) gives you a WORKING solution.
Step 6 (Complexity Analysis) tells you WHERE the bottleneck is.
Step 7 (Optimize) removes the bottleneck using a known pattern.

Example bottleneck analysis:
┌────┬────────────────────────────────┬──────────┐
│ ID │ Operation                      │ Time     │
├────┼────────────────────────────────┼──────────┤
│ 1  │ n = len(nums)                  │ O(1)     │
│ 2  │ for i in range(n):             │ O(n)     │
│ 3  │   for j in range(i+1, n):      │ O(n)  ← BOTTLENECK
│ 4  │     if nums[i] + nums[j] == t: │ O(1)     │
│ 5  │       return [i, j]            │ O(1)     │
└────┴────────────────────────────────┴──────────┘

Operations 2+3 combine to O(n²). That's the bottleneck.
→ Replace the inner loop (operation 3) with a hash map lookup O(1).
→ Total: O(n) × O(1) = O(n). Done.
```

---

## Interview Assessment Factors

> Khamies identifies **8 factors** that interviewers evaluate. Most candidates only think about #1 (algorithms knowledge). The other 7 are what separate hired from rejected.

### The 8 Assessment Factors

```
┌────────────────────────────────────────────────────────────────────┐
│              WHAT INTERVIEWERS ACTUALLY EVALUATE                    │
│                                                                    │
│  1. ALGORITHM & DS KNOWLEDGE                                       │
│     Can you recognize which data structure/technique to use?       │
│     Test: "Can you optimize this?" after brute-force.              │
│                                                                    │
│  2. PROBLEM-SOLVING SKILLS                                         │
│     Can you break a vague problem into subproblems?                │
│     Can you handle edge cases?                                     │
│     Test: "What if the input is empty?"                            │
│                                                                    │
│  3. ATTENTION TO DETAIL                                            │
│     Do you read carefully? Did you notice "sorted array"?          │
│     Do you check boundary conditions?                              │
│     Test: Hidden constraints in the problem statement.             │
│                                                                    │
│  4. CODE EFFICIENCY                                                │
│     Is your code time AND space efficient?                         │
│     Test: "Can you do this with O(1) space?"                      │
│                                                                    │
│  5. TIME COMPLEXITY ANALYSIS                                       │
│     Can you accurately state Big-O?                                │
│     Test: "What's the time complexity of your solution?"          │
│                                                                    │
│  6. MODULAR CODE                                                   │
│     Do you write helper functions?                                 │
│     Is your code readable?                                         │
│     Test: "Can you refactor this into smaller functions?"         │
│                                                                    │
│  7. DEBUGGING                                                      │
│     Can you find and fix bugs in your code?                        │
│     Test: "Your code fails on this input. Can you debug?"         │
│                                                                    │
│  8. COMMUNICATION                                                  │
│     Can you explain your thinking clearly?                         │
│     Do you ask clarifying questions?                               │
│     Do you accept feedback constructively?                        │
│     Test: "Walk me through your approach."                        │
└────────────────────────────────────────────────────────────────────┘
```

### The 3-Phase Learning Cycle

```
┌──────────────────────────────────────────────────────────────────┐
│                 THE LEARNING CYCLE                                │
│                                                                  │
│  PHASE 1: BEGINNER                                               │
│  ─────────────────                                               │
│  • Comfortable with programming language                         │
│  • Can solve easy problems (takes 15+ min)                       │
│  • Focus: Practice 50 easy problems                              │
│    Distribution: Array(20), LinkedList(10), Tree(10), String(10)│
│                                                                  │
│  PHASE 2: EXPERIENCED                                            │
│  ────────────────                                                │
│  • Solves easy in <10 min                                        │
│  • Can solve medium (takes 20+ min)                              │
│  • Struggles to know WHEN to apply techniques                    │
│  • Focus: Practice 150 medium problems                           │
│    Distribution: Array(60), LL(40), Tree(40), String(40),       │
│                 Graph(20)                                        │
│  • KEY: Group problems by pattern (FGCC framework)               │
│                                                                  │
│  PHASE 3: SENIOR                                                 │
│  ────────────                                                    │
│  • Comfortable with all techniques                               │
│  • Transforms problem → solution in <30 min                      │
│  • Struggles with stacking multiple techniques                   │
│  • Focus: Practice 100 hard problems                             │
│    Distribution: Array(10), LL(10), Tree(20), String(20),       │
│                 Graph(40)                                        │
│  • KEY: Communicate patterns with others                         │
│                                                                  │
│  TOTAL: 300 problems (50 easy + 150 medium + 100 hard)          │
└──────────────────────────────────────────────────────────────────┘
```

---

## KSum Family Deep Dive (2Sum, 3Sum, KSum)

> Khamies uses the KSum family as his **master example** because it demonstrates how a single pattern scales from easy to hard.

### 2Sum — The Foundation

```
PROBLEM: Given an array of integers and a target, find two numbers
that add up to the target. Return their indices.

BRUTE-FORCE: Two nested loops
  for i in range(n):
    for j in range(i+1, n):
      if nums[i] + nums[j] == target: return [i, j]

  Time: O(n²)  ← TWO loops = quadratic
  Space: O(1)

BOTTLENECK ANALYSIS:
  The inner loop (j) searches the ENTIRE remaining array for a
  complement (target - nums[i]). This linear search is O(n).

OPTIMIZATION: Replace linear search with hash map lookup
  → Store all numbers in a hash map: {value: index}
  → For each number, check if complement exists in map: O(1)

OPTIMIZED CODE:
  def two_sum(nums, target):
      mapper = {}
      for i, num in enumerate(nums):
          complement = target - num
          if complement in mapper:
              return [mapper[complement], i]
          mapper[num] = i
      return []

  Time: O(n)  ← Single loop + O(1) hash lookup
  Space: O(n) ← Hash map stores n elements

THE TRADEOFF: We traded SPACE for TIME.
  Brute-force: O(n²) time, O(1) space
  Optimized:   O(n) time,   O(n) space
  This is the classic time-space tradeoff.
```

### 3Sum — Adding Complexity

```
PROBLEM: Find all unique triplets that sum to zero.

BRUTE-FORCE: Three nested loops
  for i in range(n):
    for j in range(i+1, n):
      for k in range(j+1, n):
        if nums[i] + nums[j] + nums[k] == 0:
          result.add(sorted((nums[i], nums[j], nums[k])))

  Time: O(n³)  ← THREE loops = cubic
  Space: O(n)   ← result set

OPTIMIZATION: Sort + Two Pointers
  Step 1: Sort the array → O(n log n)
  Step 2: Fix one element, use two pointers for the other two

  def three_sum(nums):
      nums.sort()
      result = []

      for i in range(len(nums) - 2):
          if i > 0 and nums[i] == nums[i - 1]:  # Skip duplicates
              continue

          left, right = i + 1, len(nums) - 1
          while left < right:
              total = nums[i] + nums[left] + nums[right]
              if total == 0:
                  result.append([nums[i], nums[left], nums[right]])
                  # Skip duplicates
                  while left < right and nums[left] == nums[left + 1]:
                      left += 1
                  while left < right and nums[right] == nums[right - 1]:
                      right -= 1
                  left += 1
                  right -= 1
              elif total < 0:
                  left += 1
              else:
                  right -= 1

      return result

  Time: O(n²)  ← Sort O(n log n) + Two-pointer O(n²) = O(n²)
  Space: O(1)  ← No extra data structures (ignoring output)

KEY INSIGHT: 3Sum = fix one + reduce to 2Sum (two pointers)
  This is the RECURSIVE PATTERN that leads to KSum.
```

### KSum — The General Pattern

```
PROBLEM: Find all unique k-element subsets that sum to target.

THE PATTERN:
  KSum = fix one element + (K-1)Sum on the remaining

  Base case: 2Sum → Two pointers on sorted array
  Recursive: KSum → for each element, call (K-1)Sum

  def k_sum(nums, target, k):
      nums.sort()
      result = []

      def solve(start, target, k, path):
          if k == 2:
              # Base case: two pointers
              left, right = start, len(nums) - 1
              while left < right:
                  s = nums[left] + nums[right]
                  if s == target:
                      result.append(path + [nums[left], nums[right]])
                      while left < right and nums[left] == nums[left + 1]:
                          left += 1
                      while left < right and nums[right] == nums[right - 1]:
                          right -= 1
                      left += 1
                      right -= 1
                  elif s < target:
                      left += 1
                  else:
                      right -= 1
          else:
              # Recursive case: fix one, reduce k
              for i in range(start, len(nums) - k + 1):
                  if i > start and nums[i] == nums[i - 1]:
                      continue  # Skip duplicates
                  solve(i + 1, target - nums[i], k - 1, path + [nums[i]])

      solve(0, target, k, [])
      return result

  Time: O(n^(k-1))
    2Sum: O(n), 3Sum: O(n²), 4Sum: O(n³)

THE INTERVIEW EXTENSION GAME:
  Interviewer: "Solve 2Sum."
  You solve it.
  Interviewer: "Now solve 3Sum."
  → Apply the SAME PATTERN: fix one + two pointers.
  Interviewer: "Now 4Sum."
  → Same pattern: fix one + 3Sum.

  Each extension tests whether you understand the PATTERN,
  not just the specific solution.
```

---

## FGCC Framework (Focus, Group, Convert, Communicate)

> This is Khamies's original contribution — a **mental framework** for interview preparation inspired by transfer learning in ML.

### The ML Analogy

```
IN MACHINE LEARNING:
  You don't train BERT from scratch.
  You take a pre-trained model (baseline) and fine-tune it.

IN CODING INTERVIEWS:
  You don't solve every problem from scratch.
  You recognize a PATTERN (baseline template) and adapt it.

FGCC FRAMEWORK:
  ┌──────────────────────────────────────────────────────────────┐
  │  F — FOCUS:    Recognize repetitive patterns in problems    │
  │  G — GROUP:    Group problems with similar patterns         │
  │  C — CONVERT:  Convert each group into a reusable template  │
  │  C — COMMUNICATE: Share patterns with others               │
  └──────────────────────────────────────────────────────────────┘

THE RESULT: You build a "mental model" of solution templates.
When you see a new problem, you:
  1. Identify which pattern it matches
  2. Apply the template
  3. Customize for the specific problem

This is EXACTLY like having a pre-trained model and fine-tuning.
```

### FGCC Applied: Backtracking Pattern

```
Khamies demonstrates FGCC with 3 backtracking problems that share
the SAME underlying pattern:

PROBLEM 1: PERMUTATIONS
  Input: [1,2,3]
  Output: All orderings [[1,2,3], [1,3,2], [2,1,3], ...]

PROBLEM 2: COMBINATIONS
  Input: [1,2,3,4], k=2
  Output: [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]

PROBLEM 3: LETTER COMBINATIONS OF A PHONE NUMBER
  Input: "23"
  Output: ["ad","ae","af","bd","be","bf","cd","ce","cf"]

PATTERN RECOGNITION (the "Focus" step):
  All three involve building all possible combinations by:
  1. Making a CHOICE at each step
  2. RECURSING with the remaining choices
  3. BACKTRACKING (undoing the choice) to try alternatives

THE UNIVERSAL TEMPLATE (the "Convert" step):

  def backtrack(path, choices):
      if is_complete(path):
          result.append(path[:])  # Copy the path!
          return
      for choice in choices:
          if is_valid(choice):
              path.append(choice)       # MAKE choice
              backtrack(path, updated_choices)  # EXPLORE
              path.pop()                # UNDO choice (backtrack!)

  This ONE template solves: Permutations, Combinations,
  Subsets, N-Queens, Word Search, Sudoku Solver, Palindrome
  Partitioning, and dozens more.
```

### The Tree Visualization

```
PERMUTATIONS OF [1,2,3] AS A DECISION TREE:

                    []
                   / | \
                 1   2   3
                /|   |   |\
               2 3   1 3  1 2
               | |   | |  | |
               3 2   3 1  2 1

  Each ROOT-TO-LEAF path = one permutation.
  DFS traversal visits all paths.

  At each node:
    → Choose one element (horizontal: loop)
    → Recurse with remaining elements (vertical: recursive call)
    → Backtrack (remove last element from path)
```

---

## Top 3 Algorithm Techniques

> Khamies argues that mastering just **3 techniques** unlocks the majority of interview problems.

### Technique 1: Two Pointers

```
WHEN TO USE:
  • Sorted array + find pair/triplet
  • Palindrome check
  • Remove duplicates from sorted array
  • Container with most water
  • Linked list cycle detection (fast/slow)

TEMPLATE:
  left = 0
  right = len(arr) - 1
  while left < right:
      if condition(arr[left], arr[right]):
          # Process
          left += 1
      else:
          right -= 1

CODE EXAMPLE (Two Sum on sorted array):
  def two_sum_sorted(arr, target):
      left, right = 0, len(arr) - 1
      while left < right:
          current = arr[left] + arr[right]
          if current == target:
              return [left, right]
          elif current < target:
              left += 1   # Need bigger sum
          else:
              right -= 1  # Need smaller sum
      return []

  Time: O(n), Space: O(1)
```

### Technique 2: Breadth-First Search (BFS)

```
WHEN TO USE:
  • Shortest path in unweighted graph
  • Level-order tree traversal
  • Nearest neighbors / closest distance
  • Flood fill (grid problems)
  • Word ladder (transform one word to another)

TEMPLATE:
  from collections import deque

  def bfs(start, graph):
      queue = deque([start])
      visited = {start}
      while queue:
          node = queue.popleft()
          for neighbor in graph[node]:
              if neighbor not in visited:
                  visited.add(neighbor)
                  queue.append(neighbor)

CODE EXAMPLE (Level-order traversal):
  def level_order(root):
      if not root:
          return []
      result = []
      queue = deque([root])
      while queue:
          level = []
          for _ in range(len(queue)):
              node = queue.popleft()
              level.append(node.val)
              if node.left:
                  queue.append(node.left)
              if node.right:
                  queue.append(node.right)
          result.append(level)
      return result

  Time: O(V + E), Space: O(V)
```

### Technique 3: Depth-First Search (DFS)

```
WHEN TO USE:
  • Tree traversals (inorder, preorder, postorder)
  • Connected components
  • Cycle detection
  • Topological sorting
  • Path finding (all paths, not shortest)
  • Backtracking (DFS + undo)

TEMPLATE:
  def dfs(node, visited):
      if node is None:
          return
      visited.add(node)
      # Process node
      for neighbor in graph[node]:
          if neighbor not in visited:
              dfs(neighbor, visited)

CODE EXAMPLE (Binary tree inorder):
  def inorder(root):
      result = []
      def dfs(node):
          if not node:
              return
          dfs(node.left)      # Left
          result.append(node.val)  # Root
          dfs(node.right)     # Right
      dfs(root)
      return result

  Time: O(V + E), Space: O(h) where h = height (call stack)
```

---

## 6 Supplement Problems with Full Solutions

### Problem 1: Detect Linked List Cycle

```
PROBLEM: Given a linked list, determine if it has a cycle.

BRUTE-FORCE: Store all visited nodes in a set. If we revisit one, cycle!
  Time: O(n), Space: O(n)

OPTIMIZED (Floyd's Tortoise and Hare):
  Slow pointer moves 1 step. Fast pointer moves 2 steps.
  If there's a cycle, fast will eventually catch slow.

  def has_cycle(head):
      slow = fast = head
      while fast and fast.next:
          slow = slow.next          # 1 step
          fast = fast.next.next     # 2 steps
          if slow == fast:
              return True
      return False

  Time: O(n), Space: O(1) ← No extra memory!

  VISUALIZATION:
  1 → 2 → 3 → 4 → 5 → (points back to 3)
            ↑              |
            └──────────────┘

  Slow: 1, 2, 3, 4, 5, 3, 4 ← MEETS FAST HERE
  Fast: 1, 3, 5, 4, 3, 5, 4 ← Catches slow
```

### Problem 2: Remove Nth Node From End

```
PROBLEM: Remove the nth node from the END of a linked list.

OPTIMIZED (Two Pointers with gap):
  Move fast pointer n steps ahead.
  Then move both slow and fast until fast reaches end.
  Slow will be just before the node to remove.

  def remove_nth_from_end(head, n):
      dummy = ListNode(0, head)  # Dummy handles edge cases
      slow = fast = dummy

      for _ in range(n):
          fast = fast.next       # Fast moves n ahead

      while fast.next:
          slow = slow.next       # Both move together
          fast = fast.next

      slow.next = slow.next.next  # Remove the node
      return dummy.next

  Time: O(n), Space: O(1)

  VISUALIZATION (remove 2nd from end):
  List: 1 → 2 → 3 → 4 → 5

  Step 1: Fast moves 2 ahead:  slow=1, fast=3
  Step 2: Move together:       slow=3, fast=5
  Step 3: Remove slow.next:    3 → 5 (skip 4)

  Result: 1 → 2 → 3 → 5
```

### Problem 3: Swap Linked List Pairs

```
PROBLEM: Swap every two adjacent nodes: 1→2→3→4 becomes 2→1→4→3

  def swap_pairs(head):
      dummy = ListNode(0, head)
      prev = dummy

      while prev.next and prev.next.next:
          first = prev.next
          second = first.next

          # Swap pointers
          first.next = second.next
          second.next = first
          prev.next = second

          prev = first  # Move to next pair

      return dummy.next

  Time: O(n), Space: O(1)

  VISUALIZATION:
  Before: dummy → 1 → 2 → 3 → 4
  After:  dummy → 2 → 1 → 4 → 3
```

### Problem 4: Validate Binary Search Tree

```
PROBLEM: Check if a binary tree is a valid BST.

KEY INSIGHT: A BST requires ALL nodes in left subtree < root
  AND ALL nodes in right subtree > root. Not just immediate children.

  APPROACH: Pass down the valid range (min, max) for each node.

  def is_valid_bst(root):
      def validate(node, low=float('-inf'), high=float('inf')):
          if not node:
              return True
          if not (low < node.val < high):
              return False
          return (validate(node.left, low, node.val) and
                  validate(node.right, node.val, high))

      return validate(root)

  Time: O(n), Space: O(h) where h = tree height

  VISUALIZATION:
        5
       / \
      1   7
         / \
        6   8

  Node 5: range (-inf, +inf) ✓
  Node 1: range (-inf, 5) ✓
  Node 7: range (5, +inf) ✓
  Node 6: range (5, 7) ✓
  Node 8: range (7, +inf) ✓
  → VALID BST
```

### Problem 5: Same Binary Tree

```
PROBLEM: Check if two binary trees are identical.

  def is_same_tree(p, q):
      if not p and not q:
          return True
      if not p or not q:
          return False
      if p.val != q.val:
          return False
      return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)

  Time: O(min(n, m)), Space: O(min(h1, h2))
```

### Problem 6: Symmetric Binary Tree

```
PROBLEM: Check if a binary tree is a mirror of itself.

  def is_symmetric(root):
      def is_mirror(left, right):
          if not left and not right:
              return True
          if not left or not right:
              return False
          return (left.val == right.val and
                  is_mirror(left.left, right.right) and
                  is_mirror(left.right, right.left))

      if not root:
          return True
      return is_mirror(root.left, root.right)

  Time: O(n), Space: O(h)
```

---

## The Complete Learning Roadmap

```
┌──────────────────────────────────────────────────────────────────┐
│              KHAMIES LEARNING ROADMAP                            │
│                                                                  │
│  TOTAL: 300 problems (50 easy + 150 medium + 100 hard)          │
│                                                                  │
│  BEGINNER (50 problems):                                         │
│    Array: 20, Linked List: 10, Binary Tree: 10, String: 10     │
│    Focus: Basic operations, comfort with language                │
│    Time per problem: 15-30 min                                   │
│                                                                  │
│  EXPERIENCED (150 problems):                                     │
│    Array: 60, LL: 40, Tree: 40, String: 40, Graph: 20          │
│    Focus: Pattern recognition, algorithm techniques              │
│    Time per problem: 10-20 min                                   │
│    APPLY FGCC: Group by pattern, build templates                 │
│                                                                  │
│  SENIOR (100 problems):                                          │
│    Array: 10, LL: 10, Tree: 20, String: 20, Graph: 40          │
│    Focus: Combining techniques, creative solutions               │
│    Time per problem: 20-30 min                                   │
│    APPLY: Communicate patterns with others                       │
│                                                                  │
│  KEY PRINCIPLE: "Practice makes perfect, but pattern             │
│   recognition makes practice EFFICIENT."                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## How This Complements Your Blind 75

```
YOUR LEARNING STACK:

  1. python-basics/         ← Learn Python syntax
  2. fundamentals/          ← Learn DS concepts (arrays, trees, graphs)
  3. THIS GUIDE             ← Learn HOW to approach problems ⭐
     - 8-step process for every problem
     - FGCC framework for pattern recognition
     - KSum family as the master pattern
  4. Blind 75 solutions     ← Apply the process to real problems
  5. Pattern cheat sheet    ← Quick reference for pattern recognition

  THE FLOW:
    fundamentals/ teaches you WHAT data structures are.
    This guide teaches you HOW to use them to solve problems.
    Blind 75 gives you PRACTICE applying the process.
```

---

> **Source file:** `/leetcode-blind-75/khamies-algorithm-guide.md`
