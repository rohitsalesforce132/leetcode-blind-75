'''
CHAPTER 5: STRINGS — THE DEEP GUIDE
====================================

"Strings are everywhere in coding. Almost every interview has at least
one string problem. Python's string methods are incredibly powerful —
master them and you'll solve problems in 1 line that take 20 in other languages."

---

PART 1: STRING FUNDAMENTALS
============================

A string is an IMMUTABLE sequence of characters.
    - IMMUTABLE means: once created, you CANNOT change individual characters.
    - Any "modification" creates a NEW string.

    word = "Hello"
    word[0] = "J"          # ✗ ERROR! Strings are immutable.
    word = "J" + word[1:]  # ✓ Creates a new string "Jello"
'''

# --- CREATING STRINGS ---
s1 = 'single quotes'
s2 = "double quotes"
s3 = """triple quotes
can span
multiple lines"""
s4 = 'It\'s a test'       # Escape apostrophe with backslash

# --- STRING LENGTH ---
print(len("Hello"))       # 5

# --- CONCATENATION ---
first = "Hello"
last = "World"
full = first + " " + last
print(full)               # Hello World

# --- REPETITION ---
print("ab" * 3)           # ababab


'''
PART 1.5: WHY ARE STRINGS IMMUTABLE? (DEEP DIVE)
=================================================

You'll hear "strings are immutable" a lot. But WHY did Python choose this?
Understanding the reasoning helps you write better code and debug faster.

REASON 1: HASHABILITY (dict/set keys)
--------------------------------------
Immutable objects have a FIXED hash value for their entire lifetime.
This means strings can be used as dictionary keys and set members.

    my_dict = {"name": "Alice"}    # "name" must be hashable
    my_set = {"apple", "banana"}   # works because strings don't change

If strings were mutable, changing "name" to "Name" would silently corrupt
every dictionary that used it as a key. Hash tables would break.

REASON 2: MEMORY EFFICIENCY (string interning)
----------------------------------------------
Python REUSES identical short strings automatically (called "interning").

    a = "hello"
    b = "hello"
    # a and b may point to the SAME memory location!

This is only SAFE because strings can't change. If you could mutate `a`,
you'd accidentally mutate `b` too. Immutability makes sharing safe.

REASON 3: THREAD SAFETY
------------------------
Immutable objects are inherently safe to share between threads.
No lock is needed when reading a string — nobody can modify it under you.
This matters in concurrent code and web servers.

REASON 4: PREDICTABLE SEMANTICS
-------------------------------
When you pass a string to a function, you KNOW it won't be changed.
No defensive copies. No "who modified my string?" bugs.

    def add_exclamation(text):
        return text + "!"      # original `text` is untouched

THE COST: Every "modification" allocates a new string. That's why building
a big string with `+=` in a loop is O(n²). Use `''.join(list)` instead.

PROOF OF IMMUTABILITY:
'''
# Demonstrate that "modifying" creates a new object
original = "hello"
modified = original.replace("h", "H")

print(f"original id: {id(original)}")
print(f"modified id: {id(modified)}")
print(f"Same object? {original is modified}")   # False — different objects!
print(f"original unchanged: {original}")         # still "hello"


'''
PART 2: INDEXING & SLICING (CRITICAL FOR INTERVIEWS)
=====================================================

Each character has an INDEX (position number), starting from 0.

    String:  H  e  l  l  o
    Index:   0  1  2  3  4
    Neg:    -5 -4 -3 -2 -1

ASCII DIAGRAM — Positive vs Negative Indexing:

     char:   P   y   t   h   o   n
             ↓   ↓   ↓   ↓   ↓   ↓
       (+):   0   1   2   3   4   5      ← left to right, starts at 0
       (-):  -6  -5  -4  -3  -2  -1     ← right to left, starts at -1

SLICING SYNTAX: string[start:stop:step]
    - start: beginning index (INCLUSIVE). Default: 0
    - stop: ending index (EXCLUSIVE). Default: len(string)
    - step: how to move. Default: 1. Negative = go backwards.

ASCII DIAGRAM — How slicing works:

    s[1:4] on "Python"

     P   y   t   h   o   n
     0   1   2   3   4   5
         [========>       ← from index 1 (inclusive) to 4 (exclusive)
         y   t   h        ← result: "yth"

STEP DIAGRAM — s[::2] takes every other character:

     P   y   t   h   o   n
     ✓   ✗   ✓   ✗   ✓   ✗    ← step=2 picks every 2nd
     P       t       o       ← result: "Pto"

NEGATIVE STEP — s[::-1] reverses:

     P   y   t   h   o   n
     ←   ←   ←   ←   ←   ←    ← step=-1 walks right to left
     n   o   h   t   y   P    ← result: "nohtyP"
'''

s = "Hello World"

# --- BASIC INDEXING ---
print(s[0])              # 'H'   first character
print(s[-1])             # 'd'   last character
print(s[6])              # 'W'

# --- SLICING ---
print(s[0:5])            # "Hello"     chars 0,1,2,3,4
print(s[6:])             # "World"     from index 6 to end
print(s[:5])             # "Hello"     from start to index 4
print(s[::2])            # "HloWrd"    every 2nd character
print(s[::-1])           # "dlroW olleH"  REVERSED!

# --- PRACTICAL SLICING PATTERNS ---
# Remove first character
print(s[1:])             # "ello World"

# Remove last character
print(s[:-1])            # "Hello Worl"

# Get last N characters
print(s[-3:])            # "rld"  last 3

# Check if palindrome
word = "racecar"
is_palindrome = word == word[::-1]
print(f"'{word}' is palindrome: {is_palindrome}")   # True

# --- SLICING EDGE CASES ---
# Out-of-range indices in slices are handled gracefully (no error)
print("abc"[0:100])      # "abc" — stop clamped to length
print("abc"[-100:100])   # "abc" — both clamped
# But indexing out of range DOES raise an error:
# print("abc"[5])        # ✗ IndexError: string index out of range


'''
PART 3: STRING METHODS — YOUR TOOLBOX
======================================

Python has 40+ string methods. Here is the complete reference, grouped
by what they do. You don't need to memorize all — bookmark this section.
'''

# --- CASE METHODS ---
text = "Hello World"
print(text.upper())           # "HELLO WORLD"
print(text.lower())           # "hello world"
print(text.capitalize())      # "Hello world" (first letter only)
print(text.title())           # "Hello World" (every word capitalized)
print(text.swapcase())        # "hELLO wORLD"
print("hello world".casefold())  # "hello world" — aggressive lowercase
# casefold() is for Unicode-safe comparison (handles ß → ss, etc.)

# --- STRIP (remove whitespace) ---
messy = "   Hello World   "
print(messy.strip())          # "Hello World"   (both ends)
print(messy.lstrip())         # "Hello World   " (left only)
print(messy.rstrip())         # "   Hello World" (right only)

# Remove specific characters
print("...Hello...".strip("."))   # "Hello"
print("xxHelloxx".strip("x"))     # "Hello"
# strip removes ANY of the characters in the argument set (not a prefix):
print("abcHelloabc".strip("abc")) # "Hello" — strips a/b/c from both ends

# --- SPLIT (string → list) ---
csv_data = "Alice,25,Pune"
parts = csv_data.split(",")
print(parts)                  # ['Alice', '25', 'Pune']

sentence = "The quick brown fox"
words = sentence.split()      # Default: split on whitespace
print(words)                  # ['The', 'quick', 'brown', 'fox']

# Limit number of splits
print("a,b,c,d".split(",", 2))  # ['a', 'b', 'c,d'] — max 2 splits

# Split on newlines
multiline = "line1\nline2\nline3"
print(multiline.splitlines())  # ['line1', 'line2', 'line3']

# rsplit splits from the right
print("a.b.c.d".rsplit(".", 1))  # ['a.b.c', 'd']

# --- JOIN (list → string) ---
word_list = ["Hello", "World"]
print(" ".join(word_list))    # "Hello World"
print("-".join(word_list))    # "Hello-World"
print("".join(word_list))     # "HelloWorld"

# --- REPLACE ---
greeting = "Hello World"
print(greeting.replace("World", "Python"))    # "Hello Python"
print(greeting.replace("l", "L"))             # "HeLLo WorLd"
print(greeting.replace("l", "L", 1))          # "HeLlo World" — only first

# --- FIND / INDEX / RINDEX ---
text = "Hello World"
print(text.find("World"))     # 6   (index where "World" starts)
print(text.find("xyz"))       # -1  (not found → returns -1)
print(text.rfind("l"))        # 9   (last occurrence of 'l')
print(text.index("World"))    # 6   (same as find, but raises ValueError if missing)
# print(text.index("xyz"))    # ✗ ValueError — use find() if not sure
print(text.count("l"))        # 3   (how many 'l' characters)

# --- STARTSWITH / ENDSWITH ---
filename = "report.pdf"
print(filename.endswith(".pdf"))    # True
print(filename.endswith(".docx"))   # False
print(filename.startswith("report")) # True
# Tuple of suffixes: matches ANY
print("file.tar.gz".endswith((".gz", ".zip")))  # True

# --- CHECK METHODS (all return True/False) ---
print("hello".isalpha())      # True   (all alphabetic)
print("12345".isdigit())      # True   (all digits)
print("hello123".isalnum())   # True   (alphabetic or digit)
print("   ".isspace())        # True   (all whitespace)
print("hello".islower())      # True
print("HELLO".isupper())      # True
print("Hello World".istitle()) # True  (each word capitalized)
print("42".isnumeric())       # True
print("Ⅷ".isnumeric())        # True   (Unicode numerics too)

# --- PARTITION / RPARTITION (split into exactly 3 parts) ---
print("key=value".partition("="))     # ('key', '=', 'value')
print("no-separator".partition("="))  # ('no-separator', '', '')
print("a@b@c".rpartition("@"))        # ('a@b', '@', 'c') — split on LAST

# --- CENTER / LJUST / RJUST / ZFILL (padding) ---
print("hi".center(10, "-"))   # "----hi----"
print("hi".ljust(10, "."))    # "hi........"
print("hi".rjust(10))         # "        hi" (space padding default)
print("42".zfill(5))          # "00042" — zero-fill (great for IDs)

# --- EXPANDTABS ---
print("a\tb".expandtabs(4))   # "a   b" — tabs → spaces

# --- REMOVEPREFIX / REMOVESUFFIX (Python 3.9+) ---
url = "https://example.com"
print(url.removeprefix("https://"))  # "example.com"
print(url.removesuffix(".com"))      # "https://example"

# --- FORMAT_MAP / MAKETRANS / TRANSLATE (advanced) ---
# maketrans + translate: character-level substitution in one pass
table = str.maketrans("aeiou", "12345")
print("hello world".translate(table))  # "h2ll4 w4rld"

# encode — see Part 9 (Unicode) for details
print("hello".encode("utf-8"))  # b'hello' (bytes object)


'''
PART 4: STRING FORMATTING — THE THREE WAYS
==========================================

Python has THREE ways to format strings. Know all three — you'll see
each in legacy code, tutorials, and different codebases.

TIMELINE:
    % formatting   — Python 1.x (1990s), inherited from C's printf
    .format()      — Python 2.6 (2008)
    f-strings      — Python 3.6 (2016) ← USE THIS
'''

name = "Manav"
age = 25
score = 95.6789

# --- F-STRINGS (Python 3.6+, RECOMMENDED) ---
print(f"Name: {name}, Age: {age}")
print(f"Score: {score:.2f}")              # 2 decimal places → 95.68
print(f"Score: {score:>10.2f}")           # Right-aligned, width 10
print(f"Score: {score:<10.2f}")           # Left-aligned, width 10
print(f"Score: {score:^10.2f}")           # Centered, width 10
print(f"Score: {score:+.2f}")             # Always show sign → +95.68

# Debug mode (Python 3.8+): shows variable name AND value
x = 42
print(f"{x = }")                          # x = 42
print(f"{x = :#b}")                       # x = 0b101010 (binary)

# Expressions inside f-strings
print(f"{'Hello':>20}")                   # right-pad string
print(f"2 + 2 = {2 + 2}")                 # 2 + 2 = 4
print(f"Upper: {name.upper()}")           # Upper: MANAV

# Multi-line f-string
report = f"""
Student Report
==============
Name:  {name}
Age:   {age}
Score: {score:.1f}/100
"""
print(report)

# --- FORMAT METHOD (older style) ---
print("Name: {}, Age: {}".format(name, age))
print("Name: {n}, Age: {a}".format(n=name, a=age))
print("{0} and {0}".format("repeat"))     # "repeat and repeat" (positional)
print("{:>10}".format("hi"))              # "        hi" (right-align)
print("{:.2f}".format(3.14159))           # "3.14"

# --- PERCENT FORMATTING (oldest, from C) ---
print("Name: %s, Age: %d" % (name, age))
print("Score: %.2f" % score)              # "95.68"
print("%-10s|" % "left")                  # "left      |" (left-align)
print("%05d" % 42)                        # "00042" (zero-pad)

# --- COMPARISON TABLE ---
'''
┌──────────────┬─────────────────────────┬────────────────────────────────────┐
│   Method     │      Example            │   Notes                            │
├──────────────┼─────────────────────────┼────────────────────────────────────┤
│ f-string     │ f"{name}"               │ ✓ Fastest, most readable (3.6+)    │
│ .format()    │ "{}".format(name)       │ Slower, verbose. Use in old code.  │
│ % formatting │ "%s" % name             │ Legacy. Avoid in new code.         │
└──────────────┴─────────────────────────┴────────────────────────────────────┘

RULE OF THUMB: Use f-strings for everything in new code.
               Recognize % and .format() when reading old code.
'''


'''
PART 5: STRING-BASED INTERVIEW PATTERNS
========================================

These patterns appear CONSTANTLY in coding interviews. Memorize the
one-liner versions and understand the manual implementations.
'''

# --- PATTERN 1: REVERSING ---
# Reverse entire string
print("hello"[::-1])             # "olleh"

# Reverse words in a sentence (WORD ORDER reversed)
sentence = "Hello World Foo"
reversed_words = " ".join(sentence.split()[::-1])
print(reversed_words)            # "Foo World Hello"

# Reverse each word individually (keep word order)
words = "Hello World".split()
reversed_each = " ".join(w[::-1] for w in words)
print(reversed_each)             # "olleH dlroW"

# Reverse words WITHOUT using split (manual, for interviews)
def reverse_words_manual(s):
    """Reverse word order without built-in split."""
    words = []
    current = []
    for char in s:
        if char == " ":
            if current:
                words.append("".join(current))
                current = []
        else:
            current.append(char)
    if current:
        words.append("".join(current))
    return " ".join(words[::-1])

print(reverse_words_manual("Hello World Foo"))  # "Foo World Hello"

# --- PATTERN 2: CHARACTER FREQUENCY ---
from collections import Counter

def char_frequency(s):
    """Count occurrences of each character."""
    return dict(Counter(s))

print(char_frequency("hello"))   # {'h': 1, 'e': 1, 'l': 2, 'o': 1}

# Manual frequency count (no Counter) — for interviews
def char_frequency_manual(s):
    freq = {}
    for char in s:
        freq[char] = freq.get(char, 0) + 1
    return freq

print(char_frequency_manual("hello"))  # {'h': 1, 'e': 1, 'l': 2, 'o': 1}

# --- PATTERN 3: ANAGRAM CHECK ---
def is_anagram(s1, s2):
    """Two strings are anagrams if they have the same character counts."""
    # Remove spaces, lowercase, sort
    s1_clean = s1.replace(" ", "").lower()
    s2_clean = s2.replace(" ", "").lower()
    return sorted(s1_clean) == sorted(s2_clean)

print(is_anagram("listen", "silent"))    # True
print(is_anagram("hello", "world"))      # False
# Better O(n) approach using Counter:
print(Counter("listen") == Counter("silent"))  # True

# --- PATTERN 4: PALINDROME CHECK ---
def is_palindrome(s):
    """Check if string reads the same forwards and backwards."""
    # Clean the string: remove non-alphanumeric, lowercase
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]

print(is_palindrome("A man, a plan, a canal: Panama"))   # True
print(is_palindrome("race a car"))                       # False

# Two-pointer palindrome check (O(n) time, O(1) space — no reversed copy)
def is_palindrome_two_pointer(s):
    """Check palindrome using two pointers — no extra memory."""
    left, right = 0, len(s) - 1
    while left < right:
        # Skip non-alphanumeric from left
        while left < right and not s[left].isalnum():
            left += 1
        # Skip non-alphanumeric from right
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True

print(is_palindrome_two_pointer("A man, a plan, a canal: Panama"))  # True

# --- PATTERN 5: STRING BUILDER ---
# When building a large string piece by piece, DON'T use + concatenation.
# Each + creates a new string → O(n²) total.
# Instead, append to a list and join at the end → O(n).

# BAD (O(n²)):
# result = ""
# for word in lots_of_words:
#     result += word  # Creates new string every time!

# GOOD (O(n)):
parts = []
for word in ["Hello", " ", "World", "!"]:
    parts.append(word)
result = "".join(parts)
print(result)                    # Hello World!

# --- PATTERN 6: FIRST UNIQUE CHARACTER ---
def first_unique_char(s):
    """Return index of first non-repeating character, or -1."""
    freq = Counter(s)
    for i, char in enumerate(s):
        if freq[char] == 1:
            return i
    return -1

print(first_unique_char("leetcode"))     # 0  (l is unique)
print(first_unique_char("loveleetcode")) # 2  (v is unique)
print(first_unique_char("aabb"))         # -1 (no unique char)

# --- PATTERN 7: VALID PALINDROME SUBSEQUENCE ---
def has_palindrome_subsequence(s):
    """Check if a palindromic subsequence of length 3 exists."""
    # Any string with a duplicate char has a 3-length palindromic subseq
    return len(set(s)) < len(s)

print(has_palindrome_subsequence("abcba"))  # True
print(has_palindrome_subsequence("abc"))    # False


'''
PART 6: ASCII AND CHARACTER MANIPULATION
=========================================
'''

# --- ord() and chr() ---
# Every character has a numeric ASCII/Unicode value.
# ord(char) → number.  chr(number) → char.

print(ord('a'))              # 97
print(ord('A'))              # 65
print(ord('0'))              # 48
print(chr(97))               # 'a'
print(chr(65))               # 'A'

# ASCII TABLE QUICK REFERENCE:
'''
    Range    Characters
    -----    --------------------------------
    48-57    Digits: 0 1 2 ... 9
    65-90    Uppercase: A B C ... Z
    97-122   Lowercase: a b c ... z
    32       Space

    ASCII DIAGRAM:

    '0'=48   'A'=65   'a'=97
       |        |        |
       |<--19-->|<--32-->|
       digits   gap     lowercase after uppercase

    Note: lowercase = uppercase + 32 (the "case gap")
'''

# --- CONVERT BETWEEN CASES USING ASCII ---
# Lowercase letters: 97-122. Uppercase: 65-90. Difference = 32.
print(chr(ord('a') - 32))   # 'A' (lowercase → uppercase manually)
print(chr(ord('A') + 32))   # 'a' (uppercase → lowercase manually)

# --- CHECK IF CHARACTER IS A LETTER/DIGIT ---
def is_vowel(c):
    return c.lower() in 'aeiou'

print(is_vowel('A'))         # True
print(is_vowel('b'))         # False

# --- CAESAR CIPHER (shift letters by N) ---
def caesar_cipher(text, shift):
    result = []
    for char in text:
        if char.isalpha():
            base = ord('a') if char.islower() else ord('A')
            shifted = (ord(char) - base + shift) % 26 + base
            result.append(chr(shifted))
        else:
            result.append(char)
    return ''.join(result)

print(caesar_cipher("Hello, World!", 3))    # "Khoor, Zruog!"
print(caesar_cipher("Khoor, Zruog!", -3))   # "Hello, World!"


'''
PART 7: REGEX (REGULAR EXPRESSIONS) — BASICS
==============================================
Regex is a mini-language for matching patterns in text.
'''

import re

# --- BASIC MATCHING ---
text = "My phone number is 9876543210 and email is manav@test.com"

# Find all digits
phone = re.search(r'\d{10}', text)
if phone:
    print(f"Phone: {phone.group()}")       # 9876543210

# Find email
email = re.search(r'\S+@\S+', text)
if email:
    print(f"Email: {email.group()}")       # manav@test.com

# Find ALL matches
all_digits = re.findall(r'\d+', text)
print(f"All digit groups: {all_digits}")   # ['9876543210']

# --- REPLACE WITH REGEX ---
# Replace digits with X
redacted = re.sub(r'\d', 'X', text)
print(f"Redacted: {redacted}")
# My phone number is XXXXXXXXXX and email is manav@test.com

# --- COMMON REGEX CHEAT SHEET ---
# \d  = digit (0-9)
# \w  = word character (a-z, A-Z, 0-9, _)
# \s  = whitespace (space, tab, newline)
# .   = any character except newline
# +   = one or more
# *   = zero or more
# ?   = zero or one (optional)
# {n} = exactly n times
# {n,m} = between n and m times
# ^   = start of string
# $   = end of string
# [...] = any character inside brackets
# [^...] = any character NOT inside brackets


'''
PART 8: COMMON PITFALLS — DON'T MAKE THESE MISTAKES
====================================================

These are the bugs that waste hours in interviews and production.
Recognize them instantly.
'''

# --- PITFALL 1: OFF-BY-ONE IN SLICING ---
# Remember: slicing is [start:stop] where stop is EXCLUSIVE.
name = "Python"
print(name[0:3])    # "Pyt" — indices 0,1,2 (NOT 0,1,2,3!)
print(name[:3])     # "Pyt" — same thing
print(name[3:])     # "hon" — the REST after index 2

# Common mistake: thinking [0:3] gives 4 characters.
# It gives 3 characters (stop - start = 3 - 0 = 3).

# Off-by-one with negative indices:
print(name[-3:])    # "hon" — last 3 chars (len-3 to end)
print(name[:-3])    # "Pyt" — everything EXCEPT last 3 chars

# --- PITFALL 2: == vs is FOR STRINGS ---
# == compares VALUES (do the strings contain the same text?)
# is compares IDENTITY (are they the same object in memory?)

a = "hello"
b = "hello"
print(a == b)       # True — same value
print(a is b)       # True — CPython interns short literal strings!

# BUT — not all strings are interned:
c = "hello!"
d = "hello!"
# These MAY or MAY NOT be the same object depending on Python version,
# interning rules, and how they were created. NEVER rely on `is`.

# The safe rule: ALWAYS use == to compare string values.
# Use `is` ONLY for singleton objects like None, True, False.

long_a = "hello world " * 10
long_b = "hello world " * 10
print(long_a == long_a)   # True — values equal (correct check)
print(long_a is long_a)   # True — same object
# print(long_a is long_b) # MAY be False even though values are equal!

# --- PITFALL 3: STRING CONCATENATION PERFORMANCE ---
# Using += in a loop is O(n²). Each += copies the ENTIRE old string.

# ❌ BAD — O(n²) time:
# result = ""
# for i in range(100000):
#     result += str(i)    # copies result every iteration!

# ✓ GOOD — O(n) time:
# parts = []
# for i in range(100000):
#     parts.append(str(i))
# result = "".join(parts)

# Demonstration of the difference:
import time

def slow_concat(n):
    result = ""
    for i in range(n):
        result += str(i)
    return result

def fast_join(n):
    parts = []
    for i in range(n):
        parts.append(str(i))
    return "".join(parts)

# (Commented out to keep output clean — uncomment to see the difference)
# start = time.time(); slow_concat(50000); slow_time = time.time() - start
# start = time.time(); fast_join(50000); fast_time = time.time() - start
# print(f"Slow (+=): {slow_time:.3f}s, Fast (join): {fast_time:.3f}s")

# --- PITFALL 4: CHAINED REPLACE() CALLS ---
# Multiple .replace() calls create intermediate strings. For complex
# transformations, use str.translate() or regex instead.
clean = "  Hello   World  ".strip().replace("  ", " ")
# Better: use regex to collapse multiple spaces
clean_better = re.sub(r'\s+', ' ', "  Hello   World  ").strip()
print(f"Clean: '{clean}'")            # 'Hello World'
print(f"Better: '{clean_better}'")    # 'Hello World'

# --- PITFALL 5: MODifying A STRING YOU'RE ITERATING OVER ---
# You can't actually modify a string (it's immutable), but people try
# logic like "remove all vowels" and get confused:
text_vowels = "Hello World"
# WRONG approach (doesn't work on immutable strings):
# for char in text_vowels:
#     if char in 'aeiou':
#         text_vowels.remove(char)  # ✗ strings have no .remove()!
# RIGHT approach — build a new string:
no_vowels = ''.join(c for c in text_vowels if c.lower() not in 'aeiou')
print(no_vowels)  # "Hll Wrld"

# --- PITFALL 6: EMPTY STRING IS FALSY ---
# An empty string "" is falsy in boolean context. This is useful but surprising.
empty = ""
if not empty:
    print("Empty string is falsy!")  # this prints

# But "0" (string) is TRUTHY — only "" is falsy:
if "0":
    print("String '0' is truthy!")   # this prints

# --- PITFALL 7: STRING MULTIPLICATION GOTCHA ---
# Multiplying a string by a negative or zero gives empty string:
print("abc" * 0)    # ""
print("abc" * -1)   # "" (no error!)
print("abc" * 3)    # "abcabcabc"

# Mutable-default-argument-style gotcha with string * list:
# print(["x"] * 3)  # ['x', 'x', 'x'] — but each element is same object
# (Not a string pitfall, but related — be careful with * on mutable objects)


'''
PART 9: UNICODE AND ENCODING — STRINGS IN THE MODERN WORLD
===========================================================

ASCII only covers 128 characters (English letters, digits, basic symbols).
Unicode covers EVERY character from EVERY language — over 150,000 of them.

Python 3 strings are Unicode by default. This is a BIG deal.
'''

# --- UNICODE BASICS ---
# Each character has a "code point" — a number identifying it.
print(ord('A'))       # 65       (ASCII)
print(ord('€'))       # 8364     (Euro sign — beyond ASCII)
print(ord('€'))       # 8364
print(ord('😀'))      # 128512   (emoji — way beyond ASCII!)

# chr() works for any valid code point:
print(chr(8364))      # '€'
print(chr(128512))    # '😀'

# Unicode code points are often written as U+XXXX:
#   'A'   = U+0041
#   '€'   = U+20AC
#   '😀'  = U+1F600
print("\u20AC")       # '€'   — \u followed by 4 hex digits
print("\U0001F600")   # '😀'  — \U followed by 8 hex digits

# --- ENCODING: str → bytes ---
# A string is a sequence of code points. To save it to a file or send it
# over a network, you must ENCODE it into bytes.
text_unicode = "Héllo World €"

# UTF-8 is the dominant encoding (variable-length, ASCII-compatible):
encoded = text_unicode.encode("utf-8")
print(encoded)        # b'H\xc3\xa9llo World \xe2\x82\xac'
# ASCII characters stay 1 byte; others use 2-4 bytes.

# Other encodings (know they exist, mostly use UTF-8):
print("café".encode("utf-8"))     # b'caf\xc3\xa9'  (2 bytes for é)
# print("café".encode("ascii"))   # ✗ UnicodeEncodeError — é not in ASCII!
print("café".encode("ascii", "replace"))   # b'caf?' — replace unknown
print("café".encode("ascii", "ignore"))    # b'caf' — drop unknown

# --- DECODING: bytes → str ---
# To read bytes back into a string, DECODE them.
raw_bytes = b'H\xc3\xa9llo'
decoded = raw_bytes.decode("utf-8")
print(decoded)        # "Héllo"

# ENCODING MISMATCH is the #1 cause of Unicode errors:
# raw_bytes.decode("ascii")      # ✗ UnicodeDecodeError
# raw_bytes.decode("latin-1")    # "HÃ©llo" — wrong but no error (mojibake)

# --- THE GOLDEN RULE OF ENCODING ---
# Decode bytes → str at the INPUT boundary (reading files, network).
# Encode str → bytes at the OUTPUT boundary (writing files, network).
# Work with str everywhere in between.

# --- STRING LENGTH vs BYTE LENGTH ---
emoji_str = "😀"       # 1 character...
print(len(emoji_str))               # 1 — Python counts code points
print(len(emoji_str.encode("utf-8")))  # 4 — but 4 bytes in UTF-8!
# A single emoji can be 4 bytes even though it's "1 character".

# --- NORMALIZATION (advanced) ---
# Some characters can be represented MULTIPLE ways in Unicode.
#   'é' = U+00E9 (precomposed)
#   'é' = 'e' + U+0301 (decomposed: 'e' + combining accent)
# These look identical but are NOT equal:
import unicodedata
e_precomposed = "é"                           # 1 code point
e_decomposed = "e\u0301"                       # 2 code points
print(e_precomposed == e_decomposed)           # False!
print(len(e_precomposed), len(e_decomposed))   # 1 2

# Normalize to compare them correctly:
nfc_a = unicodedata.normalize("NFC", e_precomposed)
nfc_b = unicodedata.normalize("NFC", e_decomposed)
print(nfc_a == nfc_b)                          # True after normalization

# --- COMMON ENCODING PITFALL ---
# Reading a file with the wrong encoding → mojibake (garbled text).
# ALWAYS specify encoding when opening files:
# with open("file.txt", encoding="utf-8") as f:   # ✓ explicit
#     data = f.read()
# On Windows, the default might be cp1252 — specify utf-8 to be safe.


'''
PART 10: RAW STRINGS AND ESCAPE SEQUENCES — DEEP DIVE
======================================================

Escape sequences let you put "special" characters in strings using backslash.
Raw strings (r"...") treat backslashes literally — no escaping.
'''

# --- COMMON ESCAPE SEQUENCES ---
print("Tab:\there")          # Tab:    here
print("Newline:\nhere")      # Newline:
                              # here
print("Backslash: \\")       # Backslash: \
print("Quote: \"")           # Quote: "
print("Apostrophe: \'")      # Apostrophe: '
print("Carriage return:\rX") # X (overwrites start of line)
print("Null char: \0")       # Null char:  (invisible)
print("Hex escape: \x41")    # Hex escape: A   (\x41 = 65 = 'A')
print("Unicode: \u20AC")     # Unicode: €
print("Octal: \101")         # Octal: A   (\101 = 65 = 'A')

# FULL ESCAPE SEQUENCE TABLE:
r'''
    Sequence   Meaning                  Example
    ---------  -----------------------  ----------------------
    \\         Backslash (\)            "C:\\path"
    \'         Single quote (')         'It\'s'
    \"         Double quote (")         "Say \"hi\""
    \n         Newline                  "line1\nline2"
    \t         Tab                      "col1\tcol2"
    \r         Carriage return          "abc\rxyz"
    \b         Backspace                "abc\b"   → "ab"
    \f         Form feed                (page break)
    \v         Vertical tab             (rare)
    \a         Bell/alert               (makes a sound)
    \0         Null character           "data\0end"
    \xHH       Hex value (2 digits)     "\x41" → "A"
    \uHHHH     Unicode (4 hex digits)   "\u20AC" → "€"
    \UHHHHHHHH Unicode (8 hex digits)   "\U0001F600" → "😀"
    \ooo       Octal value              "\101" → "A"
'''

# --- RAW STRINGS (r"...") ---
# Raw strings treat backslashes as LITERAL characters.
# Crucial for regex and Windows file paths.

# WITHOUT raw string — backslashes are escape characters:
# path = "C:\new\folder"     # ✗ \n becomes newline!
# print(path)                # "C:
#                              ew\folder" (garbled)

# WITH raw string — backslashes are literal:
path = r"C:\new\folder"
print(path)                  # C:\new\folder  (correct!)

# Regex WITHOUT raw string — painful:
# re.search("\\\\d+", text)  # have to double-escape!
# Regex WITH raw string — clean:
re.search(r"\d+", "abc123")  # matches "123"

# --- RAW STRING GOTCHA ---
# A raw string CANNOT end with an odd number of backslashes.
# r"test\"    # ✗ SyntaxError — the \" escapes the quote
# r"test\\"   # ✓ "test\\" (2 literal backslashes)
# Workaround: r"test" + "\\" or use regular string "test\\".

# Raw strings are still subject to quote escaping for the DELIMITER:
# r"It's a test"  # ✓ single quote inside double-quoted string
# r"Say \"hi\""   # ✗ SyntaxError — \" is not valid even in raw string


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 5 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Strings are IMMUTABLE. Any change creates a new string.
   - Enables hashing (dict keys), interning, thread safety.
   - Cost: += in a loop is O(n²) — use ''.join(list) instead.
2. Slicing: s[start:stop:step]. s[::-1] reverses. stop is EXCLUSIVE.
3. split() → list. join() → string. These convert between list and string.
4. strip(), replace(), find(), count() — the essential methods.
5. Use list + join() for building strings (NOT += concatenation).
6. ord(char) ↔ chr(num) for character/number conversion.
7. Regex: pattern matching for text. re.search(), re.findall(), re.sub().
8. String formatting: f-strings (best), .format() (legacy), % (oldest).
9. Unicode: Python 3 strings are Unicode. encode() → bytes, decode() → str.
   - UTF-8 is the dominant encoding. Always specify encoding="utf-8".
10. Compare string VALUES with ==, never with is (interning is unreliable).
11. Raw strings r"..." treat backslashes literally — use for regex & paths.

Interview Patterns:
- Reverse words: " ".join(s.split()[::-1])
- Anagram: Counter(s1) == Counter(s2)
- Palindrome: cleaned == cleaned[::-1]  (or two-pointer for O(1) space)
- First unique char: Counter + enumerate
- Frequency count: Counter(s) or manual dict with .get(char, 0) + 1

Next: Chapter 6 — Object-Oriented Programming
""")
