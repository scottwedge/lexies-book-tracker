# -*- encoding: utf-8
"""
Defines the models for this app.

Here's a quick sketch of the expected flow:

    +--------+        +---------+        +--------+
    |  Plan  | -----> | Reading | -----> | Review |
    +--------+        +---------+        +--------+
        \                  |                  /
         \                 |                 /
          -----------------+-----------------
                           |
                           v
                  +------+   +------+
                  | Book |   | User |
                  +------+   +------+

The three models along the top represent the stages in a book's life:

*   Plan: you want to read this book
*   Reading: you are currently reading this book
*   Review: you have read and reviewed this book

The expected flow is that books move from left to right as you see them,
read them, review them.  There are helpers that move in that direction,
not in the other.

The Book and User models are separate from these flows.  Each Plan/Reading/Review
is associated with a (Book, User) pair.

"""

from .book import Book
from .reading import AlreadyReadingException, Reading
from .review import Review
from .plan import Plan, PlanAlreadyExistsException
from .user import User

__all__ = [
    "AlreadyReadingException",
    "Book",
    "Plan",
    "PlanAlreadyExistsException",
    "Reading",
    "Review",
    "User",
]
