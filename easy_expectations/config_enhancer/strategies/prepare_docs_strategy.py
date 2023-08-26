from .base_strategy import BaseStrategy


class CountDocSitesStrategy(BaseStrategy):
    def compute(self, context):
        if context.get("disable_docs"):
            return

        count = 1 if context.get("artifacts_path") else 0
        count += len(context.get("doc_sites", []))

        context["doc_sites_count"] = count


class FlattenDocSitesStrategy(BaseStrategy):
    def compute(self, context):
        if context.get("disable_docs") or "doc_sites" not in context:
            return

        for index, doc_site in enumerate(context["doc_sites"], 1):
            for key, value in doc_site.items():
                flattened_key = f'doc_site_{index}_{key.lower().replace(" ", "_")}'
                context[flattened_key] = value
        context.pop("doc_sites", None)


class ReplaceLocationWithPathStrategy(BaseStrategy):
    def compute(self, context):
        if context.get("disable_docs"):
            return

        for key in list(context.keys()):
            if "_location" in key:
                new_key = key.replace("_location", "_path")
                context[new_key] = context.pop(key)


class GenerateDefaultDataDocsStrategy(BaseStrategy):
    def __init__(self, default_key="artifacts_path"):
        self.default_key = default_key

    def compute(self, context):
        if context.get("disable_docs", False):
            return

        default_value = context.get(self.default_key, None)
        if default_value is not None and not any(
            key.startswith("doc_site_") and key.endswith("_path") for key in context
        ):
            context["doc_site_1_path"] = default_value


# class CountDocSitesStrategy(BaseStrategy):
#     def compute(self, config_dict, context):
#         # If disable_docs is true or doc_sites is not in config_dict
#         if config_dict.get("disable_docs"):
#             return

#         # If doc_sites is not in config_dict and artifacts_path is not set
#         if "doc_sites" not in config_dict and not config_dict.get("artifacts_path"):
#             return None

#         # If doc_sites is not in config_dict and artifacts_path is set
#         if "doc_sites" not in config_dict and config_dict.get("artifacts_path"):
#             count = 1
#         else:
#             count = len(config_dict["doc_sites"])

#         context["doc_sites_count"] = count
#         config_dict["doc_sites_count"] = count


# class FlattenDocSitesStrategy(BaseStrategy):
#     def compute(self, config_dict, context):
#         if config_dict.get("disable_docs"):
#             return

#         if config_dict.get("doc_sites"):
#             self._flatten_doc_sites(config_dict, context)
#             config_dict.pop("doc_sites", None)

#     def _flatten_doc_sites(self, config_dict, context):
#         for index, doc_site in enumerate(config_dict["doc_sites"], 1):
#             for key, value in doc_site.items():
#                 flattened_key = f'doc_site_{index}_{key.lower().replace(" ", "_")}'
#                 config_dict[flattened_key] = value
#                 context[flattened_key] = value


# class ReplaceLocationWithPathStrategy(BaseStrategy):
#     def compute(self, config_dict, context):
#         if config_dict.get("disable_docs"):
#             return

#         for key in list(config_dict.keys()):
#             if "_location" in key:
#                 new_key = key.replace("_location", "_path")
#                 config_dict[new_key] = config_dict.pop(key)


# class GenerateDefaultDataDocsStrategy(BaseStrategy):
#     def __init__(self, default_key="artifacts_path"):
#         self.default_key = default_key

#     def compute(self, config_dict, context):
#         if config_dict.get("disable_docs", False):
#             return

#         default_value = config_dict.get(self.default_key, None)
#         if default_value is not None and not any(
#             key.startswith("doc_site_") and key.endswith("_path") for key in config_dict
#         ):
#             context["doc_site_1_path"] = default_value
#             config_dict["doc_site_1_path"] = default_value
