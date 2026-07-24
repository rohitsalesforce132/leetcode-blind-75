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


# === VERIFY EVERYTHING ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAPTER 6 COMPLETE!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Class = blueprint. Object = instance built from blueprint.
2. __init__ = constructor. 'self' = the current object.
3. Instance method (self), class method (@classmethod, cls),
   static method (@staticmethod).
4. Inheritance: Child(Parent) gets everything. Use super().__init__().
5. Polymorphism: same method name, different behavior per type.
6. Dunder methods: __str__, __add__, __eq__, __len__, __getitem__.
7. Encapsulation: _protected, __private. Use getters/setters for validation.

Next: Chapter 7 — Error Handling & File I/O
""")
