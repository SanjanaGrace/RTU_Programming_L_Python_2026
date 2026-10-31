"""
Task 2 – Greeting Function with String Manipulation

Examples:
>>> greet_user("alice")
'Hello, Alice! Welcome to Python!'
>>> greet_user("   bob  ")
'Hello, Bob! Welcome to Python!'
>>> greet_user("anna MARIE")
'Hello, Anna marie! Welcome to Python!'
>>> greet_user("   ")
'Hello, Stranger! Welcome to Python!'
"""


def greet_user(name: str) -> str:
    """Return a greeting message after cleaning and capitalizing the name."""
    cleaned_name = name.strip()

    if cleaned_name == "":
        cleaned_name = "Stranger"
    else:
        cleaned_name = cleaned_name.capitalize()

    return f"Hello, {cleaned_name}! Welcome to Python!"


if __name__ == "__main__":
    name = input("Enter your name: ")
    print(greet_user(name))
