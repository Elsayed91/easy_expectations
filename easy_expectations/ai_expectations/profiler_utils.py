import ast
import json
import os
import re
from typing import Any, List, Optional, Union

import pandas as pd
import yaml

from easy_expectations import CONFIG_DATA

# from logger import get_logger

# logger = get_logger(__name__)

# Path variables
# Path to the current script


def get_types_from_yaml(
    file_path=CONFIG_DATA["datatypes_info"], source: Optional[str] = "pandas"
) -> str:
    """Retrieve data types for a specified category from a YAML file."""
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return ", ".join(data.get(source.lower(), []))


def get_supported_functions(source, file_path=CONFIG_DATA["core_expectations"]):
    """Get the list of supported functions based on a given source."""
    df = pd.read_csv(file_path)
    # Convert 'True'/'False' strings to actual Boolean values
    df[source.lower()] = df[source.lower()].apply(lambda x: x == "True")

    # Filter rows where the given source is True and select 'function' column
    # values
    supported_functions = df[df[source.lower()]]["function"].tolist()
    # logger.info(f"supported expectations: {len(supported_functions)}")
    return "\n".join(supported_functions)


def generate_base_col_expectations(columns: Union[str, List[str]]) -> str:
    """Generates a list of base column expectations for the given columns."""
    if isinstance(columns, str):
        columns = [columns]

    expectation_mapping = {
        "expect_column_values_to_not_be_null": 'expect_column_values_to_not_be_null(column="{}")',
        "expect_column_to_exist": 'expect_column_to_exist(column="{}")',
    }
    expectations = "\n" + "\n".join(
        [
            expectation_mapping[expectation_type].format(col)
            for col in columns
            for expectation_type in expectation_mapping.keys()
        ]
    )
    return expectations


def convert_value(value: str) -> Any:
    """Converts string value to its actual type (int, float, bool, or str)."""
    try:
        # Use literal_eval to safely evaluate the value
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        # Return original value if it can't be evaluated
        return value


def convert_text_to_expectations(text: str) -> str:
    """Converts the given text into a list of expectation dictionaries."""
    # Adjusted regular expression to capture the pattern without the hyphen
    pattern = r"expect_[a-z_]+\([^)]+\)"

    matches = re.findall(pattern, text)

    expectations = []
    for match in matches:
        # Split the match by the first opening parenthesis to get the expectation type and its arguments
        parts = match.split("(", 1)
        expectation_type = parts[0].strip()
        args = parts[1].rstrip(")")

        expectation = {"expectation_type": expectation_type, "kwargs": {}}

        # Split the args string by comma, ensuring not to split within quotes or brackets
        kwargs_list = re.split(",(?=(?:[^']*'[^']*')*[^']*$)(?![^\[]*\])", args)

        for kwarg in kwargs_list:
            # Split by the first equal sign to get key-value pairs
            key, value = kwarg.split("=", 1)
            key = key.strip()

            # Check if the value is a list
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip(" '") for v in value[1:-1].split(",")]
            else:
                value = value.strip("'")
            # Handle regex values
            if key == "regex" and value.startswith("r"):
                value = value[1:]  # Remove the leading r
                value = value.strip("'")  # Strip any unnecessary single quotes

            value = convert_value(value)
            expectation["kwargs"][key] = value

        expectations.append(expectation)
    r = {"expectations": expectations}
    return json.dumps(r, indent=4)


# def generate_base_col_expectations(columns: Union[str, List[str]]) -> str:
#     """
#     Generates a list of base column expectations for the given columns.

#     Parameters:
#         columns (Union[str, List[str]]): A column name or list of column names.

#     Returns:
#         str: A JSON string representing the generated column expectations.
#     """
#     if isinstance(columns, str):
#         columns = [columns]

#     expectations = [
#         {
#             "expectation_type": expectation_type,
#             "kwargs": {
#                 "column": col
#             }
#         }
#         for col in columns
#         for expectation_type in ["expect_column_values_to_not_be_null", "expect_column_to_exist"]
#     ]

#     return expectations
