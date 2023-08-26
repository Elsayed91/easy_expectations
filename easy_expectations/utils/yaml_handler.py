from typing import Dict, List, Union

import yaml

from .envsubst import EnvironmentVariableReplacer


class YamlHandler:
    @staticmethod
    def parse_input(yaml_input: Union[str, Dict, List[str]]) -> Dict:
        """
        Detects the type of input (file path, YAML string, or dictionary)
        and parses it accordingly.
        """
        if isinstance(yaml_input, dict):
            return YamlHandler.replace_env_var(yaml_input)

        if isinstance(yaml_input, str):
            # Check if it looks like a file path based on extension
            if yaml_input.endswith((".yaml", ".yml")):
                return YamlHandler.replace_env_var(
                    YamlHandler.read_yaml_file(yaml_input)
                )

            # If not a file path, attempt to parse as YAML string
            try:
                return YamlHandler.replace_env_var(
                    YamlHandler.parse_yaml_string(yaml_input)
                )
            except yaml.YAMLError:
                raise ValueError(
                    f"Invalid YAML content or unrecognized file path: {yaml_input}"
                )

        if isinstance(yaml_input, list):
            parsed_yaml_data = []
            for yaml_file in yaml_input:
                data = YamlHandler.read_yaml_file(yaml_file)
                if data is None:
                    parsed_yaml_data.append({})
                elif YamlHandler.validate_yaml_data(data):
                    parsed_yaml_data.append(YamlHandler.replace_env_var(data))

        return {k: v for d in parsed_yaml_data for k, v in d.items()}

    @staticmethod
    def read_yaml_file(yaml_file: str) -> Dict:
        """Reads a YAML file and returns its contents as a dictionary."""
        # if yaml_file.startswith("gs://"):
        #     file_content = GCPFileSystem().open(yaml_file[5:]).read()
        # elif yaml_file.startswith("s3://"):
        #     file_content = S3FileSystem().open(yaml_file[5:]).read()
        # elif re.match(r"^https://.*\.blob\.core\.windows\.net", yaml_file):
        #     file_content = AzureFileSystem().open(yaml_file).read()
        # else:
        with open(yaml_file, encoding="utf-8") as file:
            file_content = file.read()
        return yaml.safe_load(file_content)

    @staticmethod
    def parse_yaml_string(yaml_string: str) -> Dict:
        """Parse a YAML string and return the parsed dictionary representation."""
        return yaml.safe_load(yaml_string)

    @staticmethod
    def validate_yaml_data(data: Dict) -> bool:
        """Validates the given YAML data."""
        if not isinstance(data, dict):
            raise yaml.YAMLError("Invalid YAML data")
        return True

    @staticmethod
    def replace_env_var(data: Dict) -> Dict:
        """Replace environment variables in the given dictionary."""
        data = EnvironmentVariableReplacer.replace(data)
        return data


# # Set environment variable for testing
# os.environ['CITY'] = 'New York'

# def test_local_file():
#     data = YamlHandler.parse_input('local_tests/l.yaml')
#     assert data == {"name": "John Doe", "age": 30, "city": "New York"}
#     print("Local file test passed!")

# def test_yaml_string():
#     yaml_string = """
#     name: Jane Doe
#     age: 25
#     city: $CITY
#     """
#     data = YamlHandler.parse_input(yaml_string)
#     assert data == {"name": "Jane Doe", "age": 25, "city": "New York"}
#     print("YAML string test passed!")

# def test_yaml_dict():
#     yaml_dict = {
#         "name": "Alice",
#         "age": 28,
#         "city": "$CITY"
#     }
#     data = YamlHandler.parse_input(yaml_dict)
#     assert data == {"name": "Alice", "age": 28, "city": "New York"}
