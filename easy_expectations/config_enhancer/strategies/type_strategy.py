import re

from easy_expectations.config_enhancer.system_config import ConstantsConfig

from .base_strategy import BaseStrategy


class ResolveTypeStrategy(BaseStrategy):
    DATA_TYPE_PATTERNS = ConstantsConfig().get_data_type_patterns()

    PATHS = [
        "data_connector_path",
        "expectations_store_path",
        "validations_store_path",
        "checkpoint_store_path",
        "default_data_docs_path",
    ]

    def compute(self, context):
        # Include doc_site_*_path keys
        path_keys = self.PATHS + [
            key
            for key in context
            if key.startswith("doc_site_") and key.endswith("_path")
        ]
        for path_key in path_keys:
            path_value = context.get(path_key, None)
            if path_value:
                data_type = self._resolve_data_type(path_value)
                if data_type:
                    self._update_context(context, path_key, data_type)

    def _resolve_data_type(self, path_value):
        for data_type, pattern in self.DATA_TYPE_PATTERNS.items():
            if re.match(pattern, path_value):
                return data_type
        return None

    def _update_context(self, context, path_key, data_type):
        type_key = path_key.replace("_path", "_type")
        context[type_key] = data_type


# class ResolveTypeStrategy(BaseStrategy):
#     DATA_TYPE_PATTERNS = ConstantsConfig().get_data_type_patterns()

#     PATHS = [
#         "data_connector_path",
#         "expectations_store_path",
#         "validations_store_path",
#         "checkpoint_store_path",
#         "default_data_docs_path",
#     ]

#     def compute(self, config_dict, context):
#         # Include doc_site_*_path keys
#         path_keys = self.PATHS + [
#             key
#             for key in config_dict
#             if key.startswith("doc_site_") and key.endswith("_path")
#         ]
#         for path_key in path_keys:
#             path_value = config_dict.get(path_key, None)
#             if path_value:
#                 data_type = self._resolve_data_type(path_value)
#                 if data_type:
#                     self._update_context_and_config(
#                         context, config_dict, path_key, data_type
#                     )

#     def _resolve_data_type(self, path_value):
#         for data_type, pattern in self.DATA_TYPE_PATTERNS.items():
#             if re.match(pattern, path_value):
#                 return data_type
#         return None

#     def _update_context_and_config(self, context, config_dict, path_key, data_type):
#         type_key = path_key.replace("_path", "_type")
#         context[type_key] = data_type
#         config_dict[type_key] = data_type
