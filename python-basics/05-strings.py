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
PART 2: INDEXING & SLICING (CRITICAL FOR INTERVIEWS)
=====================================================

Each character has an INDEX (position number), starting from 0.

    String:  H  e  l  l  o
    Index:   0  1  2  3  4
    Neg:    -5 -4 -3 -2 -1

SLICING SYNTAX: string[start:stop:step]
    - start: beginning index (INCLUSIVE). Default: 0
    - stop: ending index (EXCLUSIVE). Default: len(string)
    - step: how to move. Default: 1. Negative = go backwards.
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


'''
PART 3: STRING METHODS — YOUR TOOLBOX
======================================
'''

# --- CASE METHODS ---
text = "Hello World"
print(text.upper())           # "HELLO WORLD"
print(text.lower())           # "hello world"
print(text.capitalize())      # "Hello world" (first letter only)
print(text.title())           # "Hello World" (every word capitalized)
print(text.swapcase())        # "hELLO wORLD"

# --- STRIP (remove whitespace) ---
messy = "   Hello World   "
print(messy.strip())          # "Hello World"   (both ends)
print(messy.lstrip())         # "Hello World   " (left only)
print(messy.rstrip())         # "   Hello World" (right only)

# Remove specific characters
print("...Hello...".strip("."))   # "Hello"

# --- SPLIT (string → list) ---
csv_data = "Alice,25,Pune"
parts = csv_data.split(",")
print(parts)                  # ['Alice', '25', 'Pune']

sentence = "The quick brown fox"
words = sentence.split()      # Default: split on whitespace
print(words)                  # ['The', 'quick', 'brown', 'fox']

# --- JOIN (list → string) ---
word_list = ["Hello", "World"]
print(" ".join(word_list))    # "Hello World"
print("-".join(word_list))    # "Hello-World"
print("".join(word_list))     # "HelloWorld"

# --- REPLACE ---
greeting = "Hello World"
print(greeting.replace("World", "Python"))    # "Hello Python"
print(greeting.replace("l", "L"))             # "HeLLo WorLd"

# --- FIND / INDEX ---
text = "Hello World"
print(text.find("World"))     # 6   (index where "World" starts)
print(text.find("xyz"))       # -1  (not found)
print(text.index("World"))    # 6   (same, but raises ValueError if not found)
print(text.count("l"))        # 3   (how many 'l' characters)

# --- STARTSWITH / ENDSWITH ---
filename = "report.pdf"
print(filename.endswith(".pdf"))    # True
print(filename.endswith(".docx"))   # False
print(filename.startswith("report")) # True

# --- CHECK METHODS (all return True/False) ---
print("hello".isalpha())      # True   (all alphabetic)
print("12345".isdigit())      # True   (all digits)
print("hello123".isalnum())   # True   (alphabetic or digit)
print("   ".isspace())        # True   (all whitespace)
print("hello".islower())      # True
print("HELLO".isupper())      # True


'''
PART 4: STRING FORMATTING
==========================
'''

name = "Manav"
age = 25
score = 95.6789

# --- F-STRINGS (Python 3.6+, RECOMMENDED) ---
print(f"Name: {name}, Age: {age}")
print(f"Score: {score:.2f}")              # 2 decimal places → 95.68
print(f"Score: {score:>10.2f}")           # Right-aligned, width 10

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

# --- PERCENT FORMATTING (oldest, from C) ---
print("Name: %s, Age: %d" % (name, age))


'''
PART 5: STRING-BASED INTERVIEW PATTERNS
========================================
'''

# --- PATTERN 1: REVERSING ---
# Reverse entire string
print("hello"[::-1])             # "olleh"

# Reverse words in a sentence
sentence = "Hello World Foo"
reversed_words = " ".join(sentence.split()[::-1])
print(reversed_words)            # "Foo World Hello"

# --- PATTERN 2: CHARACTER FREQUENCY ---
from collections import Counter

def char_frequency(s):
    """Count occurrences of each character."""
    return dict(Counter(s))

print(char_frequency("hello"))   # {'h': 1, 'e': 1, 'l': 2, 'o': 1}

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

# --- CONVERT BETWEEN CASES USING ASCII ---
# Lowercase letters: 97-122. Uppercase: 65-90. Difference = 32.
print(chr(ord('a') - 32))   # 'A' (lowercase → uppercase manually)

# --- CHECK IF CHARACTER IS A LETTER/DIGIT ---
def is_vowel(c):
    return c.lower() in 'aeiou'

print(is_vowel('A'))         # True
print(is_vowel('b'))         # False

# --- CESAR CIPHER (shift letters by N) ---
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


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 5 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Strings are IMMUTABLE. Any change creates a new string.
2. Slicing: s[start:stop:step]. s[::-1] reverses.
3. split() → list. join() → string. These convert between list and string.
4. strip(), replace(), find(), count() — the essential methods.
5. Use list + join() for building strings (NOT += concatenation).
6. ord(char) ↔ chr(num) for character/number conversion.
7. Regex: pattern matching for text. re.search(), re.findall(), re.sub().

Next: Chapter 6 — Object-Oriented Programming
""")
