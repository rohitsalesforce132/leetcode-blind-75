'''
CHAPTER 7: ERROR HANDLING & FILE I/O
=====================================

"In real software, things go wrong. Files don't exist, APIs timeout,
users enter bad data. Error handling is how your program survives."

---

PART 1: EXCEPTIONS — WHAT ARE THEY?
====================================

Real-world analogy: DRIVING A CAR.

    Normal flow: You drive to work. Easy.
    Exception: You get a flat tire.

    WITHOUT error handling: You crash. (Program terminates)
    WITH error handling: You pull over, change the tire, continue.

In Python, when something goes wrong, an EXCEPTION is "raised" (thrown).
If you don't handle it, the program CRASHES with a traceback.

    >>> 10 / 0
    ZeroDivisionError: division by zero
    >>> "hello" + 5
    TypeError: can only concatenate str (not "int") to str
    >>> my_list[100]
    IndexError: list index out of range
'''

# --- UNHANDLED EXCEPTION → CRASH ---
# Uncomment to see the crash:
# print(10 / 0)  # ZeroDivisionError — program stops here

# --- HANDLED EXCEPTION → CONTINUE ---
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Can't divide by zero! Using default.")
    result = 0
print(f"Result: {result}")           # Result: 0


'''
PART 2: TRY / EXCEPT / ELSE / FINALLY
======================================

The complete error handling structure:

    try:
        # Code that MIGHT fail
    except SomeError as e:
        # Code that runs IF that specific error occurs
    except (ErrorA, ErrorB):
        # Handle multiple error types
    except Exception as e:
        # Catch ALL errors (use sparingly — be specific!)
    else:
        # Runs ONLY if NO exception occurred
    finally:
        # ALWAYS runs, regardless of success or failure
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


# --- CATCHING MULTIPLE ERROR TYPES ---
def get_element(lst, index):
    """Safely get an element from a list."""
    try:
        return lst[index]
    except (IndexError, TypeError) as e:
        return f"Error: {type(e).__name__} — {e}"

print(get_element([1, 2, 3], 0))      # 1
print(get_element([1, 2, 3], 10))     # Error: IndexError — list index out of range
print(get_element([1, 2, 3], "x"))    # Error: TypeError — list indices must be...


# --- RAISING YOUR OWN EXCEPTIONS ---
def withdraw(balance, amount):
    """Withdraw money, raising error if insufficient funds."""
    if amount < 0:
        raise ValueError("Cannot withdraw negative amount")
    if amount > balance:
        raise ValueError(f"Insufficient funds: have ${balance}, need ${amount}")
    return balance - amount

try:
    new_balance = withdraw(100, 150)
except ValueError as e:
    print(f"Transaction failed: {e}")
else:
    print(f"New balance: ${new_balance}")


# --- CUSTOM EXCEPTION CLASSES ---
class ValidationError(Exception):
    """Custom exception for data validation."""
    pass

def validate_age(age):
    if not isinstance(age, int):
        raise ValidationError("Age must be an integer")
    if age < 0 or age > 150:
        raise ValidationError("Age must be between 0 and 150")
    return True

try:
    validate_age(-5)
except ValidationError as e:
    print(f"Validation error: {e}")


# --- FINALLY IS ALWAYS EXECUTED ---
# Common use: closing files, releasing resources
def read_config():
    try:
        # Simulate reading config
        data = {"port": 8080}
        return data
    except Exception:
        print("Failed to read config")
        return {}
    finally:
        print("[debug] Config read attempt finished")

print(read_config())


'''
COMMON PYTHON EXCEPTIONS (MEMORIZE THESE):
    ValueError         Wrong value (e.g., int("abc"))
    TypeError          Wrong type (e.g., "hello" + 5)
    IndexError         List index out of range
    KeyError           Dict key doesn't exist
    AttributeError     Calling non-existent method/attribute
    ZeroDivisionError  Dividing by zero
    FileNotFoundError  File doesn't exist
    NameError          Variable not defined
    StopIteration      Iterator exhausted (used internally by for loops)
    RuntimeError       Generic runtime error
    Exception          Base class for ALL exceptions


---

PART 3: FILE I/O — READING AND WRITING FILES
==============================================
'''

# --- WRITING TO A FILE ---
# 'with' statement automatically closes the file when done.
# ALWAYS use 'with' for file operations!

# Write mode 'w' (overwrites if file exists)
with open("/tmp/test_file.txt", "w") as f:
    f.write("Hello, World!\n")
    f.write("This is line 2.\n")
    f.write("This is line 3.\n")

# Write multiple lines at once
lines = ["Line A\n", "Line B\n", "Line C\n"]
with open("/tmp/test_file.txt", "a") as f:  # 'a' = append mode
    f.writelines(lines)

# --- READING FROM A FILE ---

# Read entire file as one string
with open("/tmp/test_file.txt", "r") as f:
    content = f.read()
    print(f"\n--- File Content (read all) ---\n{content}")

# Read line by line (memory-efficient for large files)
print("--- File Content (line by line) ---")
with open("/tmp/test_file.txt", "r") as f:
    for line_num, line in enumerate(f, 1):
        print(f"  Line {line_num}: {line.strip()}")

# Read all lines into a list
with open("/tmp/test_file.txt", "r") as f:
    all_lines = f.readlines()     # Each line includes \n
    print(f"\nLines as list: {len(all_lines)} lines")


'''
FILE MODES:
    'r'  → Read (default). File must exist.
    'w'  → Write. Creates or OVERWRITES.
    'a'  → Append. Creates or adds to end.
    'r+' → Read and write. File must exist.
    'b'  → Binary mode (e.g., 'rb', 'wb'). For images, audio, etc.
'''

# --- WORKING WITH JSON (most common interview/real-world format) ---
import json

data = {
    "name": "Manav",
    "skills": ["Python", "Azure", "DevOps"],
    "employed": True,
    "salary": None
}

# Write JSON to file
with open("/tmp/data.json", "w") as f:
    json.dump(data, f, indent=2)

# Read JSON from file
with open("/tmp/data.json", "r") as f:
    loaded = json.load(f)
    print(f"\n--- JSON ---\n{loaded}")
    print(f"Name: {loaded['name']}")
    print(f"Skills: {loaded['skills']}")

# JSON string ↔ Python dict (for API calls)
json_string = json.dumps(data, indent=2)     # dict → JSON string
parsed = json.loads(json_string)             # JSON string → dict


# --- WORKING WITH CSV ---
import csv

# Write CSV
with open("/tmp/data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Age", "City"])
    writer.writerow(["Alice", 30, "NYC"])
    writer.writerow(["Bob", 25, "LA"])
    writer.writerow(["Charlie", 35, "Chicago"])

# Read CSV
with open("/tmp/data.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(f"  {row}")

# DictReader (headers become keys)
with open("/tmp/data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"  {row['Name']} is {row['Age']} from {row['City']}")


'''
--- FILE I/O BEST PRACTICES ---
    1. ALWAYS use 'with open(...) as f:' — auto-closes the file
    2. Specify encoding for text files: open(path, 'r', encoding='utf-8')
    3. For large files, iterate line by line (not .read())
    4. Use os.path.join() for cross-platform paths:
       import os; path = os.path.join("dir", "file.txt")
    5. Use pathlib (modern Python):
       from pathlib import Path; p = Path("dir") / "file.txt"
'''

# --- PATHLIB (MODERN PATH HANDLING) ---
from pathlib import Path

p = Path("/tmp/test_file.txt")
print(f"\nFile exists: {p.exists()}")         # True
print(f"File name: {p.name}")                 # test_file.txt
print(f"File suffix: {p.suffix}")             # .txt
print(f"Parent dir: {p.parent}")              # /tmp

# Read file in one line with pathlib
content = p.read_text()
print(f"First 20 chars: {content[:20]}...")


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 7 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. try/except/else/finally: Handle errors without crashing.
2. 'finally' ALWAYS runs (use for cleanup/closing resources).
3. raise: Throw your own exceptions. Create custom exception classes.
4. ALWAYS use 'with open(...) as f:' for file I/O.
5. Modes: 'r' read, 'w' write (overwrite), 'a' append.
6. json.dump/load for JSON files. json.dumps/loads for strings.
7. csv.writer/reader for CSV files.
8. pathlib.Path for modern, cross-platform path handling.

Next: Chapter 8 — Modules, Iterators, Generators & Decorators
""")
