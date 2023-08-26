from easy_expectations.config_enhancer.system_config import ConstantsConfig
from easy_expectations.fs_component_extractor.fs_component_extractor_factory import (
    FileSystemComponentExtractorFactory,
)

from .base_strategy import BaseStrategy


class FileSystemEnhancementStrategy(BaseStrategy):
    SUPPORTED_PATHS = [
        "data_connector_path",
        "expectations_store_path",
        "validations_store_path",
        "checkpoint_store_path",
    ]

    def __init__(self):
        self.constants_config = ConstantsConfig()

    def compute(self, context):
        self._add_doc_site_paths(context)
        self._extract_file_system_components(context)

    def _add_doc_site_paths(self, context):
        doc_sites_count = context.get("doc_sites_count", 0)
        for i in range(1, doc_sites_count + 1):
            self.SUPPORTED_PATHS.append(f"doc_site_{i}_path")

    def _extract_file_system_components(self, context):
        for path_key in self.SUPPORTED_PATHS:
            file_system_type_key = path_key.replace("_path", "_type")
            file_system_type = context.get(file_system_type_key)

            # Check if the file_system_type is a supported filesystem using ConstantsConfig
            if not self.constants_config.is_filesystem(file_system_type):
                continue

            path = context.get(path_key)
            if path:
                extractor = FileSystemComponentExtractorFactory.create_extractor(
                    file_system_type, path
                )
                extracted_components = extractor.components()

                entity_prefix = path_key.split("_path")[0]
                self._update_config_and_context(
                    context, entity_prefix, extracted_components
                )

    def _update_config_and_context(self, context, entity_prefix, components):
        for key, value in components.items():
            full_key = f"{entity_prefix}_{key}"
            context[full_key] = value


class CleanupStrategy(BaseStrategy):
    def compute(self, context):
        # List of keys to be removed
        keys_to_remove = [
            "expectations_store_filename",
            "expectations_store_pattern",
            "validations_store_filename",
            "validations_store_pattern",
            "checkpoint_store_filename",
            "checkpoint_store_pattern",
            "default_data_docs_filename",
            "default_data_docs_pattern",
        ]

        # Get doc_sites_count from context
        doc_sites_count = context.get("doc_sites_count", 0)
        for i in range(1, doc_sites_count + 1):
            keys_to_remove.append(f"doc_site_{i}_filename")
            keys_to_remove.append(f"doc_site_{i}_pattern")

        # Remove the keys from context
        for key in keys_to_remove:
            context.pop(key, None)
