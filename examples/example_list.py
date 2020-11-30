from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "list",
        "question": "Select a fruit:",
        "options": [{"name": "banana", "value": "peach"}, "apple", "orange"],
        "default": "apple",
    },
    {
        "type": "list",
        "question": "Select a sport:",
        "options": [
            {"name": "Basketball", "value": "NBA"},
            {"name": "Rugby", "value": "NFL"},
            Separator(),
            "Soccer",
        ],
        "default": "apple",
    },
]

result = prompt(questions=questions, editing_mode="vim")
print(result)
