import re


def detect_case(s: str) -> str:
    if "_" in s:
        return "snake_case"
    elif s[0].isupper() and " " not in s:
        return "PascalCase"
    elif " " in s and s[0].isupper():
        return "SpaceSeparated"
    else:
        return "unknown"


def to_space_separated(s: str) -> str:
    if detect_case(s) == "snake_case":
        return " ".join(word.capitalize() for word in s.split("_"))
    elif detect_case(s) == "PascalCase":
        return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
    else:
        return s


def convert_yaml_keys(yaml_dict):
    new_dict = {}
    for key, value in yaml_dict.items():
        new_key = to_space_separated(key)
        if isinstance(value, dict):
            new_dict[new_key] = convert_yaml_keys(value)
        else:
            new_dict[new_key] = value
    return new_dict


# Test
yaml_content = {
    "this_is_snake_case": {
        "nestedSnake_case": "value",
        "AnotherNestedPascal": {"DeepNestedSnake_case": "deep_value"},
    },
    "ThisIsPascalCase": "value",
}

converted_yaml = convert_yaml_keys(yaml_content)
print(converted_yaml)


def to_camel_case(s):
    """Convert space-separated string to camelCase."""
    words = s.split(" ")
    return words[0].lower() + "".join(word.capitalize() for word in words[1:])


def to_snake_case(s):
    """Convert space-separated string to snake_case."""
    return s.replace(" ", "_").lower()


def to_pascal_case(s):
    """Convert space-separated string to PascalCase."""
    return "".join(word.capitalize() for word in s.split(" "))


def format_content(content, format_type):
    """Format content based on user's choice."""
    if format_type == "camel":
        return to_camel_case(content)
    elif format_type == "snake":
        return to_snake_case(content)
    elif format_type == "pascal":
        return to_pascal_case(content)
    else:  # Default to space-separated capitalized
        return content
