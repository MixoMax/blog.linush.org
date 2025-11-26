---
title: Things I learned about Python's else clause today
author: Linus Horn
tags: [Python, TILTD]
description: A short note on the else clause in Python and how it can be used with loops and try-except blocks.
created_date: 2025-11-14
---

Coming from other programming languages, the `else` keyword usually has one job: it’s the fallback for an `if` statement. But today I dove a bit deeper into Python’s control flow and realized that `else` is actually a lot more versatile (and slightly more confusing) than I thought.

It turns out you can attach an `else` block to loops and exception handlers, and the logic for when they execute is distinctively "Pythonic."

Here is what I learned.

## The Loop `else` (or: The "No Break" Clause)

You can use `else` with both `for` and `while` loops. Intuitively, you might think the `else` block runs if the loop *doesn't* run (like if a list is empty). That is **not** what happens.

The `else` block inside a loop executes **only if the loop completes normally**. If you exit the loop using a `break` statement, the `else` block is skipped.

This is incredibly useful for search algorithms. Usually, you have to use a "flag" variable to track if you found what you were looking for.

**The "Flag" Way:**
```python
found = False
for number in [1, 3, 5, 7]:
    if number == 4:
        found = True
        break

if not found:
    print("4 was not found in the list.")
```

**The `for-else` Way:**
```python
for number in [1, 3, 5, 7]:
    if number == 4:
        print("Found it!")
        break
else:
    # This runs only if the loop wasn't broken out of
    print("4 was not found in the list.")
```

Some Pythonistas argue that this should have been named `nobreak` instead of `else` to avoid confusion, but once you know the rule, it cleans up the code significantly.

## The Try-Except `else` (or: The "Success" Clause)

I also learned that `try-except` blocks have an optional `else` clause. It goes after the `except` blocks but before `finally`.

The logic here is: **Run this code if no exceptions were raised in the `try` block.**

You might ask: *Why not just put that code inside the `try` block?*

The reason is scope and safety. The general rule of exception handling is to put as little code as possible inside the `try` block. You only want to guard the line that might crash. If you put the subsequent logic inside the `try` block as well, you might accidentally catch an exception you didn't intend to catch.

**Example:**

```python
try:
    # Only guard the dangerous operation
    data = read_database()
except ConnectionError:
    handle_error()
else:
    # Only runs if read_database() succeeded.
    # If process_data() raises an error, it bubbles up 
    # rather than being caught by the specific handler above.
    process_data(data)
```

## Summary

*   **For/While loops:** `else` runs if you **didn't** `break`.
*   **Try/Except:** `else` runs if you **didn't** raise an exception.

It’s a small syntactical feature, but it helps avoid flag variables and keeps exception handling scopes tight. Definitely adding this to my daily toolkit.