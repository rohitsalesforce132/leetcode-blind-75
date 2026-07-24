'''
CHAPTER 6: OBJECT-ORIENTED PROGRAMMING (OOP)
=============================================

"OOP is how real software is built. It organizes code into OBJECTS
that combine data and behavior. Think of it as designing blueprints
(classes) and building things from them (objects)."

---

PART 1: WHAT IS OOP? — THE MENTAL MODEL
=========================================

Real-world analogy: A CAR FACTORY.

    BLUEPRINT (Class):
        "A Car has: color, brand, speed, fuel"
        "A Car can: drive(), brake(), honk()"

    OBJECTS (Instances):
        🚗 my_car = Car(color="red", brand="Tesla")
        🚙 your_car = Car(color="blue", brand="Honda")

    The blueprint (class) defines what a car IS and what it can DO.
    Each car (object) is built from the same blueprint but has different data.

    CLASS    = blueprint / template / recipe
    OBJECT   = instance / thing built from the blueprint
    ATTRIBUTES = data (what the object HAS) → variables
    METHODS  = behavior (what the object DOES) → functions

---

PART 2: DEFINING A CLASS
=========================
'''

class Car:
    """A blueprint for creating Car objects."""

    # --- CLASS ATTRIBUTE ---
    # Shared by ALL instances (same value for every Car)
    wheels = 4

    # --- CONSTRUCTOR ---
    # Called automatically when you create a new Car.
    # __init__ = "initialize". 'self' = the specific object being created.
    def __init__(self, brand, color, year=2024):
        # INSTANCE ATTRIBUTES (each Car has its own values)
        self.brand = brand        # "self.brand" = this specific car's brand
        self.color = color
        self.year = year
        self.speed = 0            # Starts at rest
        self._engine_on = False   # Protected attribute (convention: underscore)

    # --- INSTANCE METHOD ---
    # Something the object can DO. Always takes 'self' as first parameter.
    def start_engine(self):
        """Turn on the engine."""
        self._engine_on = True
        return f"{self.brand} engine started! 🚗💨"

    def accelerate(self, amount):
        """Increase speed by 'amount' mph."""
        if not self._engine_on:
            return f"Start the engine first!"
        self.speed += amount
        return f"{self.brand} is now going {self.speed} mph"

    def brake(self):
        """Reduce speed to 0."""
        self.speed = 0
        return f"{self.brand} stopped."

    def honk(self):
        """Make a sound."""
        return "Beep beep!"

    # --- STRING REPRESENTATION ---
    # What shows when you print the object
    def __str__(self):
        return f"{self.year} {self.brand} ({self.color})"

    # --- REPR (for debugging) ---
    def __repr__(self):
        return f"Car(brand='{self.brand}', color='{self.color}', year={self.year})"


# --- CREATING OBJECTS (INSTANTIATION) ---
my_car = Car("Tesla", "red", 2024)
your_car = Car("Honda", "blue", 2022)

# Each object has its OWN data (instance attributes)
print(my_car.brand)                 # Tesla
print(your_car.brand)               # Honda

# But they SHARE class attributes
print(f"My car has {my_car.wheels} wheels")     # 4
print(f"Your car has {your_car.wheels} wheels")  # 4

# Calling methods
print(my_car.start_engine())
print(my_car.accelerate(60))
print(my_car.accelerate(20))
print(my_car.brake())

# __str__ makes printing objects nice
print(my_car)                       # 2024 Tesla (red)
print(repr(my_car))                 # Car(brand='Tesla', color='red', year=2024)


'''
WHAT IS 'self'?
---------------
'self' is a reference to the CURRENT object. It's how an object refers
to its own attributes and methods.

    When you call:  my_car.accelerate(30)
    Python translates it to:  Car.accelerate(my_car, 30)
                                                  ↑
                                              'self' = my_car

    So inside the method: self.speed means my_car.speed
    You NEVER pass 'self' yourself — Python does it automatically.

---

PART 3: CLASS METHODS & STATIC METHODS
========================================
'''

class Temperature:
    """Demonstrates different method types."""

    def __init__(self, celsius):
        self.celsius = celsius

    # --- INSTANCE METHOD ---
    # Takes 'self'. Can access instance attributes.
    def to_fahrenheit(self):
        return self.celsius * 9/5 + 32

    # --- CLASS METHOD ---
    # Takes 'cls' (the class itself, not an instance).
    # Often used as ALTERNATIVE CONSTRUCTORS.
    @classmethod
    def from_fahrenheit(cls, fahrenheit):
        """Create a Temperature from Fahrenheit instead of Celsius."""
        celsius = (fahrenheit - 32) * 5/9
        return cls(celsius)          # cls = Temperature. Creates new instance.

    # --- STATIC METHOD ---
    # Takes neither 'self' nor 'cls'. Acts like a regular function
    # that just happens to live inside the class namespace.
    @staticmethod
    def water_boiling_point():
        """Return the boiling point of water in Celsius."""
        return 100


# Using each method type:
temp = Temperature(25)                           # Instance method
print(f"25°C = {temp.to_fahrenheit()}°F")        # 77.0°F

temp2 = Temperature.from_fahrenheit(100)         # Class method (alt constructor)
print(f"100°F = {temp2.celsius:.1f}°C")          # 37.8°C

print(f"Water boils at {Temperature.water_boiling_point()}°C")  # Static method


'''
METHOD TYPES SUMMARY:
    Instance method:  def method(self)          → accesses instance data
    Class method:     @classmethod              → alternative constructors
    Static method:    @staticmethod             → utility functions

---

PART 4: INHERITANCE — BUILDING ON WHAT EXISTS
==============================================

Real-world analogy: FAMILY INHERITANCE.

    Parent class: Animal (has: name, age; can: eat, sleep)
    Child class:  Dog (INHERITS everything from Animal, PLUS: bark, fetch)

    The child gets everything the parent has, for free.
    Then it can ADD new things or CHANGE (override) existing things.
'''

# --- PARENT CLASS (BASE CLASS) ---
class Animal:
    """Base class for all animals."""

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def eat(self):
        return f"{self.name} is eating. 🍖"

    def sleep(self):
        return f"{self.name} is sleeping. 😴"

    def make_sound(self):
        return f"{self.name} makes a sound."

# --- CHILD CLASS (DERIVED CLASS) ---
class Dog(Animal):
    """Dog inherits from Animal. Gets everything for free!"""

    def __init__(self, name, age, breed):
        super().__init__(name, age)     # Call parent's __init__
        self.breed = breed              # Add a new attribute

    def make_sound(self):               # OVERRIDE parent's method
        return f"{self.name} says Woof! 🐕"

    def fetch(self):                    # ADD a new method
        return f"{self.name} fetches the ball! 🎾"


# --- ANOTHER CHILD CLASS ---
class Cat(Animal):
    """Cat also inherits from Animal."""

    def make_sound(self):
        return f"{self.name} says Meow! 🐱"


# --- USING INHERITANCE ---
dog = Dog("Buddy", 3, "Golden Retriever")
cat = Cat("Whiskers", 2)

print(dog.eat())                # Inherited from Animal! → Buddy is eating.
print(dog.sleep())              # Inherited! → Buddy is sleeping.
print(dog.make_sound())         # OVERRIDDEN! → Buddy says Woof!
print(dog.fetch())              # NEW method → Buddy fetches the ball!
print(dog.breed)                # NEW attribute → Golden Retriever

print(cat.make_sound())         # OVERRIDDEN → Whiskers says Meow!


'''
INHERITANCE KEY CONCEPTS:
    1. class Child(Parent):  → Child inherits from Parent
    2. super().__init__(...) → Call the parent's constructor
    3. Override:             → Redefine a parent method in the child
    4. Extend:               → Add new methods/attributes in the child

    Dog IS an Animal. Cat IS an Animal. This is called the "IS-A" relationship.

---

PART 5: POLYMORPHISM — SAME INTERFACE, DIFFERENT BEHAVIOR
==========================================================

"Poly" = many, "morph" = forms. Polymorphism means the same method call
can behave differently depending on the object type.
'''

# --- POLYMORPHISM IN ACTION ---
animals = [Dog("Buddy", 3, "Lab"), Cat("Whiskers", 2), Animal("Bob", 5)]

for animal in animals:
    print(animal.make_sound())
# Buddy says Woof! 🐕
# Whiskers says Meow! 🐱
# Bob makes a sound.

# Same method name (make_sound), different behavior for each type!
# This is polymorphism. We don't need to know WHAT TYPE each animal is —
# we just call make_sound() and Python handles the rest.


'''
PART 6: DUNDER METHODS (MAGIC METHODS)
========================================

Dunder methods ("double underscore") let you define how objects behave
with built-in operations like +, ==, len(), printing, indexing.

    Operation     Dunder Method       Example
    -----------   ----------------    -------
    print(obj)    __str__             Human-readable string
    repr(obj)     __repr__            Debug representation
    len(obj)      __len__             Length of object
    obj1 + obj2   __add__             Addition of two objects
    obj == other  __eq__              Equality check
    obj[key]      __getitem__         Indexing access
    for x in obj  __iter__            Iteration
'''

class Vector:
    """A 2D vector with custom math operations."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):
        """Enable: v1 + v2"""
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        """Enable: v1 == v2"""
        return self.x == other.x and self.y == other.y

    def __len__(self):
        """Enable: len(v) — return magnitude as int"""
        return int((self.x ** 2 + self.y ** 2) ** 0.5)

    def __getitem__(self, index):
        """Enable: v[0] → x, v[1] → y"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Vector index out of range")

# --- USING DUNDER METHODS ---
v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(v1)                   # Vector(3, 4)        ← __str__
print(v1 + v2)              # Vector(4, 6)        ← __add__
print(v1 == v2)             # False               ← __eq__
print(len(v1))              # 5                   ← __len__ (3²+4²=25, √25=5)
print(v1[0], v1[1])         # 3 4                 ← __getitem__


'''
PART 7: ENCAPSULATION — CONTROLLING ACCESS
===========================================

Real-world analogy: A CAR'S ENGINE.

    You press the gas pedal (PUBLIC interface) → car moves
    You don't directly manipulate the fuel injection (PRIVATE internals)

    Encapsulation hides internal details and exposes only what's needed.
'''

class BankAccount:
    """A bank account with encapsulation."""

    def __init__(self, owner, balance=0):
        self.owner = owner           # PUBLIC: anyone can access
        self._type = "checking"      # PROTECTED: convention only (don't touch)
        self.__balance = balance     # PRIVATE: name-mangled, hard to access

    def deposit(self, amount):
        """PUBLIC method to add money (with validation)."""
        if amount > 0:
            self.__balance += amount
            return f"Deposited ${amount}. Balance: ${self.__balance}"
        return "Invalid amount"

    def withdraw(self, amount):
        """PUBLIC method to withdraw (with validation)."""
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            return f"Withdrew ${amount}. Balance: ${self.__balance}"
        return "Insufficient funds or invalid amount"

    def get_balance(self):
        """PUBLIC method to READ balance (can't set directly)."""
        return self.__balance


# --- ACCESS LEVELS ---
account = BankAccount("Manav", 1000)

print(account.owner)                 # ✓ PUBLIC — fine to access
# print(account.__balance)           # ✗ PRIVATE — AttributeError!
print(account.get_balance())         # ✓ Use the getter method instead
print(account.deposit(500))
print(account.withdraw(200))
print(f"Balance: ${account.get_balance()}")   # 1300


'''
ACCESS LEVELS IN PYTHON:
    public:      self.name        → Access from anywhere (default)
    protected:   self._name       → Convention: "please don't touch" (still accessible)
    private:     self.__name      → Name-mangled to self._ClassName__name

    Python's philosophy: "We're all consenting adults."
    Nothing is truly private — it's about CONVENTION, not enforcement.
    Use _ or __ to signal "don't touch this directly."

---

PART 8: REAL-WORLD OOP EXAMPLE
================================
'''

class Stack:
    """
    A Stack (LIFO) implemented as a class.
    This shows how OOP encapsulates data + behavior.
    """

    def __init__(self):
        self._items = []         # Private storage

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)

    def __str__(self):
        return f"Stack({self._items})"

    def __len__(self):
        return len(self._items)


# Using our Stack class
stack = Stack()
stack.push(10)
stack.push(20)
stack.push(30)
print(stack)                       # Stack([10, 20, 30])
print(f"Top: {stack.peek()}")      # 30
print(f"Pop: {stack.pop()}")       # 30
print(f"Size: {stack.size()}")     # 2
print(f"len(): {len(stack)}")      # 2


'''
--- (continued)

PART 9: __init__ IN DEPTH & MULTIPLE CONSTRUCTORS
===================================================

__init__ is the INITIALIZER (not really a "constructor" in the C++/Java sense).
The true constructor is __new__, which CREATES the object in memory.
__init__ then INITIALIZES it with values.

    __new__(cls, ...)   →  creates and returns a new object  (rarely overridden)
    __init__(self, ...) →  sets up attributes on that object

Why have MULTIPLE ways to construct an object?
    Users may want to build an object from different INPUT FORMATS:
        - From a string like "2024-01-15"
        - From a dict like {"year": 2024, "month": 1, "day": 15}
        - From an existing similar object (copy)
    Python's idiom: use @classmethod as ALTERNATIVE CONSTRUCTORS.
'''

from datetime import date


class Event:
    """An event with a date. Shows multiple constructors."""

    def __init__(self, title, year, month, day):
        self.title = title
        self.date = date(year, month, day)   # Store as a date object

    # --- ALTERNATIVE CONSTRUCTOR #1: from an ISO string ---
    @classmethod
    def from_iso(cls, title, iso_string):
        """Build an Event from 'YYYY-MM-DD' string."""
        y, m, d = iso_string.split("-")
        return cls(title, int(y), int(m), int(d))

    # --- ALTERNATIVE CONSTRUCTOR #2: from a dict ---
    @classmethod
    def from_dict(cls, title, data):
        """Build an Event from a dictionary."""
        return cls(title, data["year"], data["month"], data["day"])

    # --- ALTERNATIVE CONSTRUCTOR #3: from a timestamp ---
    @classmethod
    def from_timestamp(cls, title, ts):
        """Build an Event from a Unix timestamp."""
        d = date.fromtimestamp(ts)
        return cls(title, d.year, d.month, d.day)

    def __str__(self):
        return f"{self.title} on {self.date}"


# Three ways to create the same Event!
e1 = Event("Launch", 2024, 1, 15)                              # Direct
e2 = Event.from_iso("Launch", "2024-01-15")                    # From string
e3 = Event.from_dict("Launch", {"year": 2024, "month": 1, "day": 15})  # From dict

print(e1)   # Launch on 2024-01-15
print(e2)   # Launch on 2024-01-15
print(e3)   # Launch on 2024-01-15


'''
PART 10: @property — PYTHONIC GETTERS & SETTERS
=================================================

In other languages you write getX()/setX(). In Python, you often DON'T need
getters/setters at all — just use attributes directly.

But when you DO need validation or computed access, use @property.
It lets you keep attribute-like access (obj.x) while controlling what happens.

    @property        → defines the GETTER
    @x.setter        → defines the SETTER (optional)
    @x.deleter       → defines a DELETER (optional)

WHY USE IT?
    1. Add validation when setting a value
    2. Make a computed/derived value look like an attribute
    3. Change internals later WITHOUT breaking the public API
'''


class Temperature2:
    """A temperature that validates input via @property."""

    def __init__(self, celsius):
        # NOTE: we assign to the SETTER, not to a private attr directly.
        # This ensures validation runs even in __init__.
        self.celsius = celsius      # → calls the @celsius.setter

    @property
    def celsius(self):
        """Getter: returns the stored celsius value."""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        """Setter: VALIDATE before storing. Prevents nonsense like -1000°C."""
        if value < -273.15:
            raise ValueError(f"{value}°C is below absolute zero!")
        self._celsius = value

    @property
    def fahrenheit(self):
        """READ-ONLY computed property. No setter defined → can't assign."""
        return self._celsius * 9 / 5 + 32


# Using @property
t = Temperature2(25)
print(f"{t.celsius}°C = {t.fahrenheit}°F")    # 25°C = 77.0°F

t.celsius = 100                               # Uses the SETTER (valid)
print(f"Boiling: {t.fahrenheit}°F")           # 212.0°F

# t.celsius = -500                             # ✗ ValueError! (below absolute zero)
# t.fahrenheit = 50                            # ✗ AttributeError! (read-only property)


'''
@property SUMMARY:
    - Use @property when you need CONTROL over get/set.
    - Start with plain attributes. Add @property LATER only if needed.
    - This is "refactoring without breaking the API" — callers still use .celsius.
    - Common pattern: store _x privately, expose x via @property.

---

PART 11: DATA CLASSES (@dataclass) — MODERN PYTHON OOP
=========================================================

Introduced in Python 3.7. @dataclass auto-generates boilerplate:
    - __init__      (from your typed fields)
    - __repr__      (nice debug string)
    - __eq__        (compare by field values)
    - __hash__      (if frozen=True)

This eliminates 20+ lines of repetitive __init__ + __repr__ code.

    from dataclasses import dataclass, field

    @dataclass
    class Point:
        x: float
        y: float
        label: str = "origin"    # default value

KEY OPTIONS:
    frozen=True   → immutable (like a tuple). Can't change after creation.
    eq=True       → auto-generate __eq__ (default True)
    order=True    → auto-generate __lt__, __le__, __gt__, __ge__ (for sorting)
'''

from dataclasses import dataclass, field


@dataclass
class Product:
    """A product. @dataclass writes __init__, __repr__, __eq__ for us."""
    name: str
    price: float
    quantity: int = 0              # Fields with defaults go LAST

    def total_value(self):
        """Regular method — @dataclass doesn't stop you from adding those."""
        return self.price * self.quantity


# Auto-generated __init__:
p1 = Product("Laptop", 999.99, 5)
p2 = Product("Laptop", 999.99, 5)

# Auto-generated __repr__:
print(p1)                        # Product(name='Laptop', price=999.99, quantity=5)

# Auto-generated __eq__ (compares by ALL fields):
print(p1 == p2)                  # True (same values)

# Access like any object:
print(f"Total value: ${p1.total_value()}")    # $4999.95


# --- IMMUTABLE DATA CLASS (frozen) ---
@dataclass(frozen=True)
class Point:
    """An immutable point. Can't be changed after creation (like a tuple)."""
    x: float
    y: float


pt = Point(3.0, 4.0)
print(pt)                        # Point(x=3.0, y=4.0)
# pt.x = 10                      # ✗ FrozenInstanceError! Can't modify frozen dataclass.

# Frozen dataclasses are HASHABLE → can be used in sets and dict keys:
points = {Point(0, 0), Point(1, 1), Point(0, 0)}   # set dedupes → 2 items
print(len(points))               # 2


# --- COMPLEX DEFAULTS with field(default_factory=...) ---
@dataclass
class Student:
    name: str
    grades: list = field(default_factory=list)    # Mutable default → use factory!
    tags: set = field(default_factory=set)


s = Student("Manav")
s.grades.append(95)
s.tags.add("honors")
print(s)                         # Student(name='Manav', grades=[95], tags={'honors'})


'''
@dataclass vs REGULAR CLASS — WHEN TO USE WHICH:
    Use @dataclass when:
        - The class is mostly DATA (attributes) with little custom logic.
        - You want __init__, __repr__, __eq__ for free.
        - You have many simple "record" types (configs, DTOs, rows from a DB).
    Use a regular class when:
        - The class has lots of BEHAVIOR (methods) and a complex __init__.
        - You need full control over initialization.
        - Inheritance chains are deep and intricate.

---

PART 12: ABSTRACT BASE CLASSES (ABC) — ENFORCING INTERFACES
==============================================================

An ABC defines an INTERFACE that subclasses MUST implement.
If a subclass doesn't implement all abstract methods, Python RAISES an error
when you try to instantiate it.

Real-world analogy: A JOB DESCRIPTION.
    "Every Employee must have: work() and get_salary()."
    ABC = the job description. Subclasses = the actual people hired.
    If someone doesn't fulfill the requirements, they can't start (instantiate).

    from abc import ABC, abstractmethod
'''

from abc import ABC, abstractmethod


class Shape(ABC):
    """Abstract base class. You CANNOT instantiate Shape directly."""

    @abstractmethod
    def area(self):
        """Every shape MUST define how to compute area."""
        ...

    @abstractmethod
    def perimeter(self):
        """Every shape MUST define how to compute perimeter."""
        ...

    def describe(self):
        """Concrete method — inherited by all shapes as-is."""
        return f"{type(self).__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


# shape = Shape()                 # ✗ TypeError! Can't instantiate abstract class.


class Circle(Shape):
    """Circle fully implements the Shape interface."""
    def __init__(self, radius):
        self.radius = radius

    def area(self):               # MUST implement
        return 3.14159 * self.radius ** 2

    def perimeter(self):          # MUST implement
        return 2 * 3.14159 * self.radius


class Rectangle(Shape):
    """Rectangle fully implements the Shape interface."""
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


c = Circle(5)
r = Rectangle(4, 6)
print(c.describe())              # Circle: area=78.54, perimeter=31.42
print(r.describe())              # Rectangle: area=24.00, perimeter=20.00

# Polymorphism via ABC: any Shape is guaranteed to have area() and perimeter()
shapes = [Circle(3), Rectangle(2, 8), Circle(10)]
for sh in shapes:
    print(sh.describe())


'''
ABC KEY POINTS:
    - ABC = a CONTRACT. Subclasses MUST fulfill it.
    - @abstractmethod marks methods that MUST be overridden.
    - ABCs can have concrete methods too (shared by all subclasses).
    - Use ABC when you want to GUARANTEE an interface across many classes.
    - Example from the stdlib: collections.abc has Iterable, Sequence, Mapping, etc.

---

PART 13: DUNDER METHODS DEEP DIVE
===================================

Part 6 covered __str__, __add__, __eq__, __len__, __getitem__.
Here we go DEEPER into the most useful dunder methods.

    __eq__   → equality (==)
    __lt__   → less than (<), used for SORTING
    __hash__ → hashing (for sets, dict keys)
    __call__ → make an object callable like a function
    __len__  → len(obj)
    __bool__ → bool(obj), used in if/while
    __contains__ → `in` operator

KEY INSIGHT: __eq__ and __hash__ are LINKED.
    "If a == b, then hash(a) must == hash(b)." (The hash contract.)
    If you override __eq__, Python sets __hash__ = None (unhashable!)
    unless you ALSO override __hash__.
'''

import functools


@functools.total_ordering    # Fills in missing comparisons from __eq__ + __lt__
class Money:
    """Money with rich comparisons. Shows __eq__, __lt__, __hash__, __call__."""

    def __init__(self, amount, currency="USD"):
        self.amount = amount
        self.currency = currency

    # --- __eq__: equality based on amount ---
    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount

    # --- __lt__: less-than, enables SORTING ---
    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount

    # --- __hash__: required if you want Money in sets/dict keys ---
    # Must be consistent with __eq__: equal objects → equal hashes.
    def __hash__(self):
        return hash(self.amount)

    # --- __call__: makes the object callable like a function! ---
    def __call__(self, discount_percent):
        """Calling money(10) returns a new Money with a discount applied."""
        discounted = self.amount * (1 - discount_percent / 100)
        return Money(discounted, self.currency)

    def __str__(self):
        return f"{self.currency} {self.amount:.2f}"

    def __repr__(self):
        return f"Money({self.amount}, '{self.currency}')"


# --- __eq__ and __lt__ → rich comparisons ---
m1 = Money(50)
m2 = Money(50)
m3 = Money(30)

print(m1 == m2)                  # True       ← __eq__
print(m1 < m3)                   # False      ← __lt__
print(m1 > m3)                   # True       ← __gt__ (auto-filled by total_ordering)
print(m1 != m3)                  # True       ← __ne__ (auto-filled)

# --- SORTING works because __lt__ is defined ---
wallet = [Money(75), Money(10), Money(50), Money(30)]
wallet.sort()                    # Uses __lt__
print([str(m) for m in wallet])  # ['USD 10.00', 'USD 30.00', 'USD 50.00', 'USD 75.00']

# --- __hash__ → usable in sets and dict keys ---
unique_amounts = {Money(50), Money(50), Money(30)}
print(len(unique_amounts))       # 2 (equal Money objects hash the same → deduped)

# --- __call__ → object behaves like a function ---
price = Money(100)
sale_price = price(10)           # Calls price.__call__(10) → 10% discount
print(sale_price)                # USD 90.00


# --- __bool__ and __contains__ ---
class TaskList:
    """Shows __bool__ and __contains__."""

    def __init__(self):
        self.tasks = []

    def add(self, task):
        self.tasks.append(task)

    def __len__(self):
        return len(self.tasks)

    def __bool__(self):
        """An empty TaskList is falsy."""
        return len(self.tasks) > 0

    def __contains__(self, item):
        """Enables: `item in tasklist`"""
        return item in self.tasks


tasks = TaskList()
print(bool(tasks))               # False (empty → falsy)
tasks.add("write code")
tasks.add("test code")
print(bool(tasks))               # True (non-empty → truthy)
print(len(tasks))                # 2
print("test code" in tasks)      # True ← __contains__

# __bool__ matters in if/while:
if tasks:                        # Uses __bool__
    print("You have work to do!")


'''
DUNDER METHODS CHEAT SHEET:
    __eq__        a == b
    __ne__        a != b     (auto from __eq__)
    __lt__        a < b      (sorting, min, max)
    __le__/__gt__/__ge__     (auto via @functools.total_ordering)
    __hash__      hash(a)    (sets, dict keys; must match __eq__)
    __bool__      bool(a)    (if/while/and/or truthiness)
    __call__      a()        (object acts like a function)
    __contains__  x in a     (membership testing)
    __len__       len(a)
    __getitem__   a[i]       (indexing/slicing)
    __setitem__   a[i] = v
    __iter__/__next__        (for loops, unpacking)
    __enter__/__exit__       (context managers: `with`)
    __getattr__   a.missing  (dynamic attribute access)

REMEMBER THE HASH CONTRACT:
    a == b  ⟹  hash(a) == hash(b)
    Override __eq__ → you MUST also override __hash__ (or it becomes None).

---

PART 14: MULTIPLE INHERITANCE & MRO
======================================

Python allows a class to inherit from MULTIPLE parents:
    class Child(ParentA, ParentB):
        ...

But which parent's method wins if both define the same one?
Answer: the METHOD RESOLUTION ORDER (MRO). Python uses the C3 linearization
algorithm to produce a deterministic, predictable order.

    ClassName.__mro__     → tuple of classes in lookup order
    ClassName.mro()       → same as a list

RULES OF MRO (simplified):
    1. A class comes BEFORE its parents.
    2. If a class inherits from multiple parents, left-to-right order is preserved.
    3. Each class appears EXACTLY once.
'''


class A:
    def greet(self):
        return "A.greet"

    def shared(self):
        return "A.shared"


class B(A):
    def greet(self):
        return "B.greet"

    # inherits shared() from A


class C(A):
    def greet(self):
        return "C.greet"

    def shared(self):
        return "C.shared"


class D(B, C):
    """D inherits from BOTH B and C (multiple inheritance)."""
    pass


# --- THE DIAMOND PROBLEM ---
# Both B and C inherit from A. D inherits from B and C.
# This creates a DIAMOND:
#
#        A
#       / \
#      B   C
#       \ /
#        D
#
# When D calls greet(), which one runs? → MRO decides.

d = D()
print(d.greet())                 # B.greet  (B is leftmost in D(B, C))
print(d.shared())                # C.shared (B has no shared(), so MRO goes to C)

# --- VIEW THE MRO ---
print(D.__mro__)
# (<class '...A'>, <class '...B'>, <class '...C'>, <class '...A'>, <class 'object'>)
# Lookup order: D → B → C → A → object

print([cls.__name__ for cls in D.__mro__])
# ['D', 'B', 'C', 'A', 'object']


'''
MRO WALKTHROUGH for D(B, C):
    1. D is checked first (the class itself).
    2. B is next (leftmost parent in `class D(B, C)`).
    3. C is next.
    4. A is last (common base of B and C).
    5. object is always last (every class inherits from it).

super() follows the MRO:
    Inside B.greet, calling super().greet() goes to C.greet (NOT A.greet!),
    because MRO for D is D→B→C→A.

MIXINS — the common use of multiple inheritance:
    A Mixin is a small class that adds ONE specific capability.
    You combine mixins to build feature-rich classes without deep hierarchies.
'''

import json as _json_module


class JsonMixin:
    """Adds JSON serialization to any class with a to_dict() method."""
    def to_json(self):
        return _json_module.dumps(self.to_dict())


class LogMixin:
    """Adds logging to any class."""
    def log(self, msg):
        print(f"[LOG] {type(self).__name__}: {msg}")


class User(JsonMixin, LogMixin):
    """Combines two mixins for extra behavior — no deep inheritance needed."""
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def to_dict(self):
        return {"name": self.name, "age": self.age}


user = User("Manav", 25)
print(user.to_json())            # {"name": "Manav", "age": 25}
user.log("User created")         # [LOG] User: User created


'''
MRO GUIDELINES:
    - Keep inheritance graphs SHALLOW and SIMPLE.
    - Prefer MIXINS (small, single-purpose) over deep diamond hierarchies.
    - Always check ClassName.__mro__ if method resolution is confusing.
    - super() respects MRO — it's NOT always "the parent class."

---

PART 15: COMPOSITION VS INHERITANCE
======================================

INHERITANCE = "IS-A" relationship (Dog IS-A Animal)
COMPOSITION = "HAS-A" relationship (Car HAS-A Engine)

RULE OF THUMB: "Favor composition over inheritance."
    Inheritance is rigid (set at class definition, can't change at runtime).
    Composition is flexible (swap parts at runtime).

Real-world analogy:
    INHERITANCE: You're BORN a Dog. Can't change your species.
    COMPOSITION: A Car HAS an Engine. You can swap a V6 for a V8 anytime.

    class Car(Engine):       ← BAD. A car is not an engine.
    class Car: has Engine     ← GOOD. A car contains/uses an engine.
'''


# --- INHERITANCE: "IS-A" ---
class Engine:
    def start(self):
        return "Engine running"

# Bad: making Car inherit Engine just to reuse start()
# class Car(Engine): ...   ← this is wrong! A Car is NOT an Engine.


# --- COMPOSITION: "HAS-A" ---
class V6Engine(Engine):
    def start(self):
        return "V6 engine fires up — VROOM!"

    def horsepower(self):
        return 300


class ElectricMotor:
    def start(self):
        return "Electric motor hums to life — silent!"

    def horsepower(self):
        return 400


class Car2:
    """A Car HAS-A engine (composition). We can swap engines freely."""
    def __init__(self, brand, engine):
        self.brand = brand
        self.engine = engine       # ← COMPOSITION: Car CONTAINS an Engine

    def start(self):
        # DELEGATE to the engine object
        return f"{self.brand}: {self.engine.start()}"

    def specs(self):
        return f"{self.brand} with {self.engine.horsepower()} HP"


# Same Car class, DIFFERENT engines (swap at runtime):
gas_car = Car2("Mustang", V6Engine())
ev = Car2("Tesla", ElectricMotor())

print(gas_car.start())            # Mustang: V6 engine fires up — VROOM!
print(gas_car.specs())            # Mustang with 300 HP
print(ev.start())                 # Tesla: Electric motor hums to life — silent!
print(ev.specs())                 # Tesla with 400 HP

# Swap the engine at runtime — impossible with inheritance!
gas_car.engine = ElectricMotor()
print(gas_car.start())            # Mustang: Electric motor hums to life — silent!


# --- DEEPER COMPOSITION: building complex objects from parts ---
class Wheel:
    def __init__(self, position):
        self.position = position


class Car3:
    """A Car composed of MULTIPLE parts."""
    def __init__(self, brand, engine):
        self.brand = brand
        self.engine = engine
        self.wheels = [Wheel(f"wheel-{i}") for i in range(1, 5)]  # 4 wheels

    def part_count(self):
        return 1 + len(self.wheels)   # 1 engine + 4 wheels


sports = Car3("Ferrari", V6Engine())
print(f"{sports.brand} has {sports.part_count()} parts")   # Ferrari has 5 parts


'''
COMPOSITION VS INHERITANCE — DECISION GUIDE:
    Use INHERITANCE when:
        - True "IS-A" relationship (Dog IS-A Animal).
        - Subclass is a SPECIALIZED version of the parent.
        - You want to share + override behavior naturally.
    Use COMPOSITION when:
        - "HAS-A" relationship (Car HAS-A Engine).
        - You need to swap behavior at RUNTIME.
        - You want to combine capabilities from unrelated classes.
        - The inheritance hierarchy would be deep/rigid.

    INHERITANCE = static, declared once, rigid.
    COMPOSITION = dynamic, flexible, swappable.

    "Favor composition over inheritance." — Effective Java (also true in Python)

---

PART 16: COMMON PITFALLS
==========================

Avoid these classic OOP mistakes in Python.
'''

# --- PITFALL 1: Mutable default arguments ---
print("\n--- PITFALL 1: Mutable default arguments ---")

class BadCart:
    """BUG: all instances SHARE the same list!"""
    def __init__(self, items=[]):       # ← DANGER: mutable default!
        self.items = items

class GoodCart:
    """FIX: use None and create a new list inside."""
    def __init__(self, items=None):
        self.items = items if items is not None else []


c1 = BadCart()
c2 = BadCart()
c1.items.append("apple")
print(f"c2.items (BUG): {c2.items}")    # ['apple'] — leaked from c1!

g1 = GoodCart()
g2 = GoodCart()
g1.items.append("apple")
print(f"g2.items (FIXED): {g2.items}")  # [] — properly isolated


# --- PITFALL 2: Forgetting super().__init__() ---
print("\n--- PITFALL 2: Forgetting super().__init__() ---")

class Base:
    def __init__(self):
        self.initialized = True

class Broken(Base):
    def __init__(self):
        pass                          # ← Forgot super().__init__()!

class Fixed(Base):
    def __init__(self):
        super().__init__()            # ← Correct: call parent's __init__

b = Broken()
print(f"Broken has 'initialized'? {'initialized' in vars(b)}")  # False
f = Fixed()
print(f"Fixed.initialized = {f.initialized}")                   # True


# --- PITFALL 3: Class attribute vs instance attribute confusion ---
print("\n--- PITFALL 3: Class attribute confusion ---")

class Counter:
    count = 0                 # CLASS attribute (shared)

    def __init__(self):
        Counter.count += 1    # Modify via ClassName, not self

    # WRONG way (creates an INSTANCE attribute that shadows the class attr):
    # def __init__(self):
    #     self.count += 1      # ← creates instance attr, class attr unchanged


Counter()    # count = 1
Counter()    # count = 2
Counter()    # count = 3
print(f"Counter.count = {Counter.count}")   # 3


# --- PITFALL 4: Overriding __eq__ without __hash__ ---
print("\n--- PITFALL 4: __eq__ without __hash__ ---")

class Tag:
    """BUG: defining __eq__ sets __hash__ to None → unhashable!"""
    def __init__(self, label):
        self.label = label

    def __eq__(self, other):
        return isinstance(other, Tag) and self.label == other.label

    # __hash__ is now None by default → can't put in sets!

tag1 = Tag("python")
tag2 = Tag("python")
print(f"tag1 == tag2: {tag1 == tag2}")     # True
# tags = {tag1, tag2}                      # ✗ TypeError: unhashable type: 'Tag'

# FIX: add __hash__:
class HashableTag:
    def __init__(self, label):
        self.label = label

    def __eq__(self, other):
        return isinstance(other, HashableTag) and self.label == other.label

    def __hash__(self):
        return hash(self.label)            # ← consistent with __eq__

ht1 = HashableTag("python")
ht2 = HashableTag("python")
tagset = {ht1, ht2}                        # Works! Deduped to 1 item.
print(f"len(tagset) = {len(tagset)}")      # 1


# --- PITFALL 5: Using inheritance where composition fits ---
print("\n--- PITFALL 5: Wrong relationship type ---")

# BAD: Stack inheriting list (a Stack is NOT a list, it HAS internal storage)
# class Stack(list): ...   ← exposes append, extend, sort, etc. (breaks encapsulation)

# GOOD: Stack CONTAINS a list (composition)
class GoodStack:
    def __init__(self):
        self._items = []             # composition: Stack HAS-A list

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def __len__(self):
        return len(self._items)


gs = GoodStack()
gs.push(1)
gs.push(2)
# gs.sort()                           # ← Not available! Good — a Stack shouldn't sort.
print(f"GoodStack len: {len(gs)}")   # 2


# --- PITFALL 6: Not returning NotImplemented for cross-type comparisons ---
print("\n--- PITFALL 6: Type-checking in comparisons ---")

class SafeMoney:
    """Returns NotImplemented for unknown types → Python tries reflected op."""
    def __init__(self, amount):
        self.amount = amount

    def __eq__(self, other):
        if not isinstance(other, SafeMoney):
            return NotImplemented     # ← lets Python try other.__eq__ or fall back
        return self.amount == other.amount

    def __hash__(self):
        return hash(self.amount)


sm = SafeMoney(100)
print(f"sm == 100: {sm == 100}")     # False (SafeMoney != int, handled gracefully)


'''
PITFALLS SUMMARY:
    1. Mutable default args      → use None + create inside __init__
    2. Missing super().__init__  → parent attributes never set
    3. Class attr confusion       → modify via ClassName, not self
    4. __eq__ without __hash__   → object becomes unhashable (breaks sets/dicts)
    5. Inheritance vs composition → don't inherit just to reuse; prefer HAS-A
    6. Hard type checks           → return NotImplemented for unknown types

=== END OF NEW CONTENT ===
'''


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 6 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1.  Class = blueprint. Object = instance built from blueprint.
2.  __init__ = initializer. 'self' = the current object.
    Use @classmethod for multiple constructors (from_string, from_dict, etc.)
3.  Instance method (self), class method (@classmethod, cls),
    static method (@staticmethod).
4.  Inheritance: Child(Parent) gets everything. Use super().__init__().
5.  Polymorphism: same method name, different behavior per type.
6.  Dunder methods: __str__, __add__, __eq__, __len__, __getitem__,
    __lt__ (sorting), __hash__ (sets/dicts), __call__, __bool__, __contains__.
7.  Encapsulation: _protected, __private. Use @property for validated access.
8.  @property: pythonic getters/setters. Refactor internals without breaking API.
9.  @dataclass: auto-generates __init__, __repr__, __eq__. Use frozen=True
    for immutability, field(default_factory=...) for mutable defaults.
10. ABC (abstract base class): enforce that subclasses implement required methods.
11. Multiple inheritance & MRO: Python uses C3 linearization.
    Check ClassName.__mro__. Favor mixins over deep diamonds.
12. Composition over inheritance: "HAS-A" beats "IS-A" when you need flexibility.

Next: Chapter 7 — Error Handling & File I/O
""")
