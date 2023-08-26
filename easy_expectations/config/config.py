import os

import yaml


def load_and_process_config(
    config_file_path: str,
    project_root: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
) -> dict:
    """Load configuration from a YAML file and process any path variables."""

    config_file_path = os.path.join(project_root, config_file_path)
    # Ensure the config file exists
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"Config file {config_file_path} not found!")

    # Load the raw configuration data from the file
    with open(config_file_path, "r") as f:
        raw_config_data = yaml.safe_load(f)

    # Check if raw_config_data is loaded properly
    if raw_config_data is None:
        raise ValueError(
            f"Failed to load configuration from \
                        {config_file_path}. Please check if the \
                        file contains valid YAML."
        )

    # Process the raw_config_data and resolve paths
    config_data = {}
    for key, value in raw_config_data.items():
        if isinstance(value, str) and value.startswith(
            "filepath:"
        ):  # Here's where you'd detect a path in your YAML
            resolved_path = os.path.join(
                project_root, value.replace("filepath:", "").strip()
            )
            config_data[key] = resolved_path
        else:
            config_data[key] = value

    return config_data
