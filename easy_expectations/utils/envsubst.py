import os
import re
from typing import Any, Match, Tuple, Union

from easy_expectations.utils.logger import logger


class EnvironmentVariableReplacer:
    """
    A class to handle environment variable replacement.
    ${VAR} or $VAR: Replace with the value of VAR.
    ${VAR-default}: Use default only if VAR is unset.
    ${VAR:-default}: Use default if VAR is unset or set and empty.
    """

    _SIMPLE_VARIABLE_PATTERN = re.compile(r"(?<!\\)\$([A-Za-z0-9_]+)")
    _COMPLEX_VARIABLE_PATTERN = re.compile(r"(?<!\\)\$\{([^}]+)\}")

    @classmethod
    def _fetch_environment_variable(
        cls, variable_name: str, default: Union[str, None] = None
    ) -> str:
        """Fetch the value of an environment variable."""
        value = os.environ.get(variable_name, "")
        return value if value != "" else default  # type: ignore

    @classmethod
    def _replace_variable(
        cls, variable_name: str, default_value: Union[str, None] = None
    ) -> str:
        """
        Replace the specified variable with its corresponding environment
        variable value.
        """
        value = cls._fetch_environment_variable(variable_name, default_value)
        if value == "":
            logger.warning(
                f"Environment variable {variable_name} is not set. "
                f"Ensure the variable exists in the environment or use a default value."
            )
        return value

    @classmethod
    def _replace_simple_variable(cls, match: Match[str]) -> str:
        """
        Replace a simple variable in the given match object with the
        corresponding replaced variable string.
        """
        variable_name = match.group(1)
        return cls._replace_variable(variable_name)

    @staticmethod
    def _parse_complex_variable(variable_expression: str) -> Tuple:
        """
        Parse a complex variable expression and return a tuple with the
        variable name and default value.
        """
        if ":-" in variable_expression:
            variable_name, default_value = variable_expression.split(":-", 1)
            return variable_name, default_value
        if "-" in variable_expression:
            variable_name, default_value = variable_expression.split("-", 1)
            if os.environ.get(variable_name, "") == "":
                return variable_name, default_value
            return variable_name, None
        if variable_expression.isidentifier():
            variable_name = variable_expression
            return variable_name, None
        raise ValueError(f"Invalid variable expression: {variable_expression}")

    @classmethod
    def _replace_complex_variable(cls, match: Match[str]) -> str:
        """
        Replace a complex variable in the given match object.
        """
        variable_expression = match.group(1)
        variable_name, default_value = cls._parse_complex_variable(variable_expression)
        if default_value is not None:
            return cls._replace_variable(variable_name, default_value)
        return cls._replace_variable(variable_name)

    @classmethod
    def replace(cls, data: Any) -> Any:
        """
        Replace all instances of complex and simple variables in the given
        data.
        """
        if isinstance(data, dict):
            return {key: cls.replace(value) for key, value in data.items()}
        if isinstance(data, list):
            return [cls.replace(element) for element in data]
        if isinstance(data, str):
            data = cls._COMPLEX_VARIABLE_PATTERN.sub(
                cls._replace_complex_variable, data
            )
            data = cls._SIMPLE_VARIABLE_PATTERN.sub(cls._replace_simple_variable, data)
            return data
        return data
