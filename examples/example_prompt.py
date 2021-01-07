from InquirerPy import prompt


def number_validation(text):
    try:
        int(text)
        return True
    except ValueError:
        return False


questions = [
    {
        "type": "input",
        "message": "Enter your age:",
        "validate": number_validation,
        "invalid_message": "Input should be number.",
        "default": "18",
        "name": "age",
        "filter": lambda result: int(result),
        "transformer": lambda result: "Adult" if int(result) >= 18 else "Youth",
    },
    {
        "type": "rawlist",
        "message": "What drinks would you like to buy:",
        "default": 2,
        "choices": lambda result: ["Soda", "Cidr", "Water", "Milk"]
        if result["age"] < 18
        else ["Wine", "Beer"],
        "name": "drink",
    },
    {
        "type": "list",
        "message": "Would you like a bag:",
        "choices": ["Yes", "No"],
        "when": lambda result: result["drink"] in {"Wine", "Beer"},
    },
    {"type": "confirm", "message": "Confirm?", "default": True},
]

result = prompt(questions=questions)