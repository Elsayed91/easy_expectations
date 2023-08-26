import os
from typing import Dict, Optional, Tuple

import yaml

from easy_expectations import CONFIG_DATA


class ConstantsConfig:
    """
    Singleton class to load and provide access to specific configurations and
    constants.

    This class reads a YAML file containing patterns and backends and provides
    methods to access this data. It ensures that only one instance of the class
    is created and shared across the application, using the singleton pattern
    implemented in the __new__ method.
    """

    _instance: Optional["ConstantsConfig"] = None
    DATA_SYSTEMS_INFO_FILE_PATH = CONFIG_DATA["data_systems_info_file_path"]

    def __new__(cls, *args, **kwargs) -> "ConstantsConfig":
        """
        Create a new instance of ConstantsConfig or return the existing
        instance.
        """
        if args or kwargs:
            raise TypeError("ConstantsConfig cannot be instantiated with arguments.")
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_yaml()
        return cls._instance

    @property
    def backend_type_patterns(self):
        """Get the backend type patterns."""
        return [
            entry["pattern"]
            for entry in self.yaml_data.values()
            if "backend_type" in entry
        ]

    def load_yaml(self) -> None:
        """Load the YAML file and store the data in the yaml_data field."""
        try:
            with open(self.DATA_SYSTEMS_INFO_FILE_PATH) as file:
                self.yaml_data = yaml.safe_load(file)
        except (FileNotFoundError, yaml.YAMLError):
            self.yaml_data = {}
        if self.yaml_data is None:
            self.yaml_data = {}

    def get_data_type_patterns(self) -> Dict[str, str]:
        """Get the patterns for different data types from the YAML content."""
        patterns = {}
        if self.yaml_data:
            for entity, details in self.yaml_data.items():
                if "pattern" in details:
                    patterns[entity] = details["pattern"]
        return patterns

    def get_backend_mapping(self) -> Dict[str, str]:
        """
        Get the backend mappings for different entities from the YAML content.
        Only entities that have a 'backend' field in the YAML data are
        included.
        """
        mappings = {}
        for entity, details in self.yaml_data.items():
            if "backend_type" in details:
                mappings[entity] = details["backend_type"]
        return mappings

    def get_inferred_connector_mapping(self) -> Dict[str, str]:
        """
        Get the inferred connector mappings for different entities from the
        YAML content.
        """
        mappings = {}
        for entity, details in self.yaml_data.items():
            if "inferred_connector" in details:
                mappings[entity] = details["inferred_connector"]
        return mappings

    def get_cloud_options(self, cloud_type: str) -> Tuple[str, ...]:
        """Get the cloud options for a given cloud type."""
        cloud_details = self.yaml_data.get(cloud_type, {})
        return tuple(cloud_details.get("cloud_options", []))

    def is_filesystem(self, file_system_type: str) -> bool:
        """Check if a given file system type is a filesystem."""
        # Check if the given type exists in the configuration and has the
        # 'type' attribute set to "filesystem"
        return self.yaml_data.get(file_system_type, {}).get("type") == "filesystem"
