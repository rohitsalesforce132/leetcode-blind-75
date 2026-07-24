'''
CHAPTER 7: ERROR HANDLING & FILE I/O — THE COMPLETE DEEP DIVE
===============================================================

"In real software, things go wrong. Files don't exist, APIs timeout,
users enter bad data, networks fail. Error handling is how your program
SURVIVES these situations instead of crashing. File I/O is how your
program PERSISTS data to disk."

---

PART 1: EXCEPTIONS — WHAT ARE THEY AND WHY?
============================================

Real-world analogy: DRIVING A CAR.

    Normal flow: You drive to work. Easy.
    Exception: You get a flat tire.

    WITHOUT a spare tire: You're stranded. (Program crashes)
    WITH a spare tire: You change it and continue. (Exception handled)

In Python, when something goes wrong, an EXCEPTION is "raised" (thrown).
If nobody handles it, the program CRASHES with a traceback.

    >>> 10 / 0
    ZeroDivisionError: division by zero

    >>> "hello" + 5
    TypeError: can only concatenate str (not "int") to str

    >>> my_list[100]
    IndexError: list index out of range

    >>> undefined_variable
    NameError: name 'undefined_variable' is not defined
'''

# --- UNHANDLED EXCEPTION → CRASH ---
# Uncomment to see the crash:
# result = 10 / 0
# print("This never prints because the program crashed above")

# --- HANDLED EXCEPTION → CONTINUE ---
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Can't divide by zero! Using default.")
    result = 0
print(f"Result: {result}")           # Result: 0


'''
PART 2: TRY / EXCEPT / ELSE / FINALLY — THE COMPLETE STRUCTURE
================================================================

    try:
        # Code that MIGHT fail
    except SomeError as e:
        # Runs IF that specific error occurs
    except (ErrorA, ErrorB):
        # Handle multiple error types together
    except Exception as e:
        # Catch ALL errors (use sparingly — be specific!)
    else:
        # Runs ONLY if NO exception occurred in try block
    finally:
        # ALWAYS runs, regardless of success or failure

EXECUTION FLOW:
    1. try block runs
    2. If exception → matching except block runs → finally runs
    3. If NO exception → else block runs → finally runs
    4. finally ALWAYS executes (even if return/break/continue in try)
'''

# --- COMPLETE EXAMPLE ---
def safe_divide(a, b):
    """Divide a by b with full error handling."""
    try:
        result = a / b
    except ZeroDivisionError:
        return "Error: Cannot divide by zero"
    except TypeError as e:
        return f"Error: Wrong type — {e}"
    else:
        return f"Result: {result}"
    finally:
        print(f"  [debug] Attempted {a} / {b}")

print("\n--- Error Handling ---")
print(safe_divide(10, 2))         # Result: 5.0
print(safe_divide(10, 0))         # Error: Cannot divide by zero
print(safe_divide(10, "two"))     # Error: Wrong type


'''
PART 3: THE EXCEPTION HIERARCHY
================================

All exceptions in Python form a CLASS HIERARCHY:

    BaseException
    ├── SystemExit              (sys.exit())
    ├── KeyboardInterrupt       (Ctrl+C)
    └── Exception               ← Base class for ALL catchable errors
        ├── ValueError          (wrong value: int("abc"))
        ├── TypeError           (wrong type: "hello" + 5)
        ├── IndexError          (list index out of range)
        ├── KeyError            (dict key doesn't exist)
        ├── AttributeError      (method/attribute doesn't exist)
        ├── ZeroDivisionError   (division by zero)
        ├── FileNotFoundError   (file not found)
        ├── NameError           (variable not defined)
        ├── StopIteration       (iterator exhausted)
        ├── RuntimeError        (generic runtime error)
        ├── RecursionError      (too many recursive calls)
        ├── OverflowError       (number too large)
        └── OSError             (operating system errors)
            ├── FileNotFoundError
            ├── PermissionError
            ├── TimeoutError
            └── ConnectionError

KEY INSIGHT: Catching 'Exception' catches ALL the errors under it.
But it also catches errors you might not expect. BE SPECIFIC.
'''

# --- CATCHING MULTIPLE ERROR TYPES ---
def get_element(lst, index):
    """Safely get an element from a list."""
    try:
        return lst[index]
    except (IndexError, TypeError) as e:
        return f"Error: {type(e).__name__} — {e}"

print(get_element([1, 2, 3], 0))      # 1
print(get_element([1, 2, 3], 10))     # Error: IndexError
print(get_element([1, 2, 3], "x"))    # Error: TypeError


'''
PART 4: RAISING YOUR OWN EXCEPTIONS
====================================

You can RAISE exceptions to signal errors in your own code.
This is how you communicate "something went wrong" to the caller.
'''

# --- RAISE BASIC ---
def validate_age(age):
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    if age < 0 or age > 150:
        raise ValueError(f"Age must be between 0 and 150, got {age}")
    return True

try:
    validate_age(-5)
except ValueError as e:
    print(f"Validation error: {e}")

# --- RAISE FROM (EXCEPTION CHAINING) ---
def process_data(data):
    try:
        result = json.loads(data)     # May fail
    except json.JSONDecodeError as e:
        raise ValueError("Invalid data format") from e  # Chain the original

# --- RE-RAISING ---
def do_something():
    try:
        risky_operation()
    except SomeError:
        log_error()
        raise  # Re-raise the same exception


'''
PART 5: CUSTOM EXCEPTION CLASSES
=================================

For production code, define your OWN exception classes.
This makes error handling more precise and readable.
'''

class ValidationError(Exception):
    """Custom exception for data validation failures."""
    pass

class AuthenticationError(Exception):
    """Custom exception for authentication failures."""
    pass

class RateLimitError(Exception):
    """Custom exception for rate limiting."""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after  # Custom attribute!

def validate_email(email):
    if "@" not in email:
        raise ValidationError(f"Invalid email: {email}")

try:
    validate_email("not-an-email")
except ValidationError as e:
    print(f"Caught: {e}")


'''
PART 6: FILE I/O — READING AND WRITING FILES
==============================================

The 'with' statement automatically closes the file when done.
ALWAYS use 'with' for file operations — it guarantees cleanup even
if an exception occurs.

FILE MODES:
    'r'  → Read (default). File must exist.
    'w'  → Write. Creates or OVERWRITES.
    'a'  → Append. Creates or adds to end.
    'r+' → Read and write. File must exist.
    'b'  → Binary mode (e.g., 'rb', 'wb'). For images, audio, etc.
    'x'  → Exclusive creation. Fails if file already exists.
'''

import json
import csv

# --- WRITING TO A TEXT FILE ---
with open("/tmp/learning_test.txt", "w") as f:
    f.write("Hello, World!\n")
    f.write("This is line 2.\n")
    f.write("This is line 3.\n")

# Append mode (adds to end without overwriting)
with open("/tmp/learning_test.txt", "a") as f:
    f.writelines(["Line A\n", "Line B\n", "Line C\n"])

# --- READING FROM A TEXT FILE ---

# Read entire file as one string:
with open("/tmp/learning_test.txt", "r") as f:
    content = f.read()
    print(f"\n--- Full file ---\n{content}")

# Read line by line (memory-efficient for large files):
print("--- Line by line ---")
with open("/tmp/learning_test.txt", "r") as f:
    for line_num, line in enumerate(f, 1):
        print(f"  {line_num}: {line.strip()}")

# Read all lines into a list:
with open("/tmp/learning_test.txt", "r") as f:
    all_lines = f.readlines()
    print(f"Lines: {len(all_lines)}")

# --- JSON FILES (most common in APIs and config) ---
data = {
    "name": "Manav",
    "skills": ["Python", "Azure", "DevOps"],
    "employed": True,
    "salary": None
}

# Write JSON:
with open("/tmp/learning_data.json", "w") as f:
    json.dump(data, f, indent=2)

# Read JSON:
with open("/tmp/learning_data.json", "r") as f:
    loaded = json.load(f)
    print(f"\n--- JSON ---")
    print(f"Name: {loaded['name']}")
    print(f"Skills: {loaded['skills']}")

# JSON string ↔ Python dict (for API calls):
json_string = json.dumps(data, indent=2)
parsed = json.loads(json_string)

# --- CSV FILES ---
with open("/tmp/learning_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Age", "City"])
    writer.writerow(["Alice", 30, "NYC"])
    writer.writerow(["Bob", 25, "LA"])

with open("/tmp/learning_data.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(f"  {row}")

# DictReader (column names become keys):
with open("/tmp/learning_data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"  {row['Name']} is {row['Age']} from {row['City']}")


'''
PART 7: PATHLIB — MODERN PATH HANDLING
========================================
'''

from pathlib import Path

# Create paths (cross-platform — works on Windows, Mac, Linux):
p = Path("/tmp/learning_test.txt")
print(f"\n--- Pathlib ---")
print(f"Exists: {p.exists()}")
print(f"Name: {p.name}")               # learning_test.txt
print(f"Stem: {p.stem}")               # learning_test (name without extension)
print(f"Suffix: {p.suffix}")           # .txt
print(f"Parent: {p.parent}")           # /tmp

# Build paths with / operator (cleaner than os.path.join):
dir_path = Path("/tmp") / "my_project" / "data" / "config.json"
print(f"Built path: {dir_path}")

# Read a file in one line:
content = p.read_text()
print(f"First line: {content.split(chr(10))[0]}")

# List files in a directory:
for file in Path("/tmp").glob("learning_*"):
    print(f"Found: {file.name}")

# Create directories:
Path("/tmp/learning_dir").mkdir(exist_ok=True)


'''
PART 8: THE CONTEXT MANAGER PROTOCOL
======================================

The 'with' statement works with any object that implements
__enter__ and __exit__ methods. You can create your own!
'''

class FileManager:
    """Custom context manager for file handling."""
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        # Return False to propagate exceptions, True to suppress
        return False

with FileManager("/tmp/learning_test.txt", "r") as f:
    content = f.read()
    print(f"\nCustom manager read: {len(content)} chars")

# Using contextlib for a simpler approach:
from contextlib import contextmanager

@contextmanager
def open_file(filename, mode):
    """Simpler context manager using a generator."""
    f = open(filename, mode)
    try:
        yield f
    finally:
        f.close()

with open_file("/tmp/learning_test.txt", "r") as f:
    print(f"contextlib read: {f.readline().strip()}")


'''
PART 9: COMMON PITFALLS
========================
'''

# --- PITFALL 1: BARE EXCEPT (catching everything) ---
# BAD: Catches even KeyboardInterrupt (Ctrl+C) and SystemExit
# try:
#     something()
# except:           # ← Bare except catches EVERYTHING
#     pass

# GOOD: Catch specific exceptions
# try:
#     something()
# except (ValueError, TypeError) as e:
#     handle_error(e)

# --- PITFALL 2: SWALLOWING EXCEPTIONS ---
# BAD: Silently ignoring errors
# try:
#     important_operation()
# except Exception:
#     pass           # ← Error is swallowed! Nobody knows it happened.

# GOOD: At least log the error
# try:
#     important_operation()
# except Exception as e:
#     logger.error(f"Operation failed: {e}")
#     raise          # Re-raise if the caller should handle it

# --- PITFALL 3: NOT CLOSING FILES ---
# BAD: File might not close if exception occurs
# f = open("file.txt", "w")
# f.write("data")
# something_that_might_crash()  # If this crashes, file stays open!
# f.close()

# GOOD: Use 'with' (closes automatically even on exception)
# with open("file.txt", "w") as f:
#     f.write("data")
#     something_that_might_crash()  # File still closes!

# --- PITFALL 4: FORGETTING ENCODING ---
# BAD: May fail on non-UTF-8 systems
# with open("file.txt", "r") as f:    # Uses system default encoding
#     content = f.read()

# GOOD: Always specify encoding for text files
# with open("file.txt", "r", encoding="utf-8") as f:
#     content = f.read()

# --- PITFALL 5: EXCEPTION ORDER MATTERS ---
# BAD: Never-reaching specific handler
# try:
#     ...
# except Exception:          # ← Catches everything first!
#     print("generic")
# except ValueError:         # ← NEVER reached (Exception already caught it)
#     print("specific")

# GOOD: Specific FIRST, general LAST
# try:
#     ...
# except ValueError:         # Specific first
#     print("value error")
# except Exception:          # General last
#     print("generic")


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 7 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. try/except/else/finally: Handle errors without crashing.
2. 'finally' ALWAYS runs (use for cleanup, closing resources).
3. Be SPECIFIC with except clauses (avoid bare 'except:').
4. raise: Throw your own exceptions. Create custom exception classes.
5. ALWAYS use 'with open(...) as f:' for file I/O.
6. Modes: 'r' read, 'w' write (overwrite), 'a' append, 'b' binary.
7. json.dump/load for JSON files. json.dumps/loads for strings.
8. csv.writer/reader for CSV. DictReader for header-based access.
9. pathlib.Path for modern, cross-platform path handling.
10. Create custom context managers with __enter__/__exit__ or @contextmanager.

Next: Chapter 8 — Modules, Iterators, Generators & Decorators
""")
