import os
from typing import Any, Dict, Optional, Union

from easy_expectations import CONFIG_DATA
from easy_expectations.utils.yaml_handler import YamlHandler


class ConfigMapper:
    CONFIG_MAPPER_VARS_FILE = CONFIG_DATA["config_mapper_vars_file_path"]

    def __init__(
        self,
        config: Dict,
        mapping: Optional[Dict] = None,
        mapping_key: Optional[str] = None,
    ) -> None:
        """
        Initialize the class with the provided configuration and optional mapping.

        Args:
            config (Dict): The configuration dictionary.
            mapping (Dict, optional): The mapping dictionary. Defaults to None.
            mapping_key (str, optional): The mapping key. Defaults to None.
        """
        self.mapping = YamlHandler().parse_input(self.CONFIG_MAPPER_VARS_FILE)

        if mapping:
            user_mapping = (
                mapping if isinstance(mapping, dict) else config.get(mapping, {})
            )
            self.mapping.update(self.load_user_mapping(user_mapping))

        if mapping_key and mapping_key in config:
            user_mapping = self.load_user_mapping(config[mapping_key])
            self.mapping.update(user_mapping)

        self.config = self.flatten_dict(config)

    @staticmethod
    def load_user_mapping(mapping: Union[str, dict]) -> dict:
        """
        Load user mapping from a file or return the mapping as is.

        Args:
            mapping (str or dict): The mapping to be loaded.

        Returns:
            dict: The loaded mapping if a file is provided, otherwise the
            mapping as is.
        """
        if isinstance(mapping, str) and os.path.isfile(mapping):
            return YamlHandler().read_yaml_file(mapping)
        return mapping  # type: ignore

    def flatten_dict(self, d: dict, parent_key: str = "", sep: str = "/") -> dict:
        """
        Recursively flattens a nested dictionary into a single-level dictionary.

        Args:
            d (dict): The nested dictionary to be flattened.
            parent_key (str, optional): The parent key for the current
            iteration. Defaults to "".
            sep (str, optional): The separator to be used between keys.
            Defaults to "/".

        Returns:
            dict: A single-level dictionary containing the flattened key-value
            pairs from the input dictionary.
        """
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                # Check if the new_key with a trailing slash exists in the mapping
                if new_key + sep in self.mapping.values():
                    variable_name = self._get_variable_name(new_key + sep)
                    if variable_name is not None:
                        items.append((variable_name, v))
                else:
                    items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                variable_name = self._get_variable_name(new_key)
                if variable_name is not None:
                    items.append((variable_name, v))
        return dict(items)
        # items = []
        # for k, v in d.items():
        #     new_key = parent_key + sep + k if parent_key else k
        #     if isinstance(v, dict):
        #         items.extend(self.flatten_dict(v, new_key, sep=sep).items())
        #     else:
        #         variable_name = self._get_variable_name(new_key)
        #         if variable_name is not None:
        #             items.append((variable_name, v))
        # return dict(items)

    def _get_variable_name(self, new_key: Any) -> Optional[str]:
        """Find the variable name associated with a given key in the mapping."""
        return next(
            (var for var, path in self.mapping.items() if path == new_key), None
        )

    def get(self, variable: str) -> Any:
        """Retrieve the value of a variable from the configuration mapping."""
        if variable not in self.mapping:
            raise KeyError(f"Variable '{variable}' not found in mapping")
        return self.config.get(variable)
