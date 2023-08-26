from .base_strategy import BaseStrategy


class SuffixDefaultPathsStrategy(BaseStrategy):
    def compute(self, context):
        artifacts_path = context.get("artifacts_path")
        paths_to_check = [
            ("validations_store_path", "validations"),
            ("expectations_store_path", "expectations"),
            ("checkpoint_store_path", "checkpoints"),
        ]

        # Add the doc_site paths to paths_to_check
        doc_sites_count = context.get("doc_sites_count", 0)
        paths_to_check += [
            (f"doc_site_{i}_path", "docs") for i in range(1, doc_sites_count + 1)
        ]

        for path_key, suffix in paths_to_check:
            path_value = context.get(path_key)
            if path_value and path_value == artifacts_path:
                # Add a slash if the path doesn't already end with one
                separator = "" if path_value.endswith("/") else "/"
                context[path_key] += f"{separator}{suffix}"


# class SuffixDefaultPathsStrategy(BaseStrategy):
#     def compute(self, config_dict, context):
#         artifacts_path = config_dict.get("artifacts_path")
#         paths_to_check = [
#             ("validations_store_path", "validations"),
#             ("expectations_store_path", "expectations"),
#             ("checkpoint_store_path", "checkpoints"),
#         ]

#         # Add the doc_site paths to paths_to_check
#         doc_sites_count = config_dict.get("doc_sites_count", 0)
#         paths_to_check += [
#             (f"doc_site_{i}_path", "docs") for i in range(1, doc_sites_count + 1)
#         ]

#         for path_key, suffix in paths_to_check:
#             path_value = config_dict.get(path_key)
#             if path_value and path_value == artifacts_path:
#                 # Add a slash if the path doesn't already end with one
#                 separator = "" if path_value.endswith("/") else "/"
#                 config_dict[path_key] += f"{separator}{suffix}/"
#                 context[path_key] += f"{separator}{suffix}/"
