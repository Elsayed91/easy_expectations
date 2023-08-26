import re

from .base_strategy import BaseStrategy


class GroupEntitiesStrategy(BaseStrategy):
    ENTITY_KEYS = [
        "checkpoint_store",
        "data_connector",
        "evaluation_parameter_store",
        "expectations_store",
        "validations_store",
        "email_alerting",
        "slack_alerting",
        "teams_alerting",
        "opsgenie_alerting",
        "pagerduty_alerting",
        "sns_alerting",
        "openlineage_integration",
        "datahub_integration",
    ]

    def group_by_prefix(self, context, prefix):
        group = {}
        pattern = re.compile(f"^{prefix}_(.+)")
        for key, value in list(context.items()):
            match = pattern.match(key)
            if match:
                attribute_key = match.group(1)
                group[attribute_key] = value
                del context[key]
        return group

    def compute(self, context):
        grouped_entities = {entity_key: {} for entity_key in self.ENTITY_KEYS}

        # Handle doc sites dynamically based on doc_sites_count
        doc_sites_count = context.get("doc_sites_count", 1)
        doc_sites = {
            f"doc_site_{i}": self.group_by_prefix(context, f"doc_site_{i}")
            for i in range(1, doc_sites_count + 1)
        }
        grouped_entities["doc_sites"] = doc_sites

        # Group remaining keys
        for entity_key in self.ENTITY_KEYS:
            grouped_entities[entity_key].update(
                self.group_by_prefix(context, entity_key)
            )

        # Update the context with grouped entities
        context.update({k: v for k, v in grouped_entities.items() if v})


# class GroupEntitiesStrategy(BaseStrategy):
#     ENTITY_KEYS = [
#         "checkpoint_store",
#         "data_connector",
#         "evaluation_parameter_store",
#         "expectations_store",
#         "validations_store",
#         "email_alerting",
#         "slack_alerting",
#         "teams_alerting",
#         "opsgenie_alerting",
#         "pagerduty_alerting",
#         "sns_alerting",
#         "openlineage_integration",
#         "datahub_integration",
#     ]

#     def group_by_prefix(self, config_dict, prefix):
#         group = {}
#         pattern = re.compile(f"^{prefix}_(.+)")
#         for key, value in list(config_dict.items()):
#             match = pattern.match(key)
#             if match:
#                 attribute_key = match.group(1)
#                 group[attribute_key] = value
#                 del config_dict[key]
#         return group

#     def compute(self, config_dict, context):
#         grouped_entities = {entity_key: {} for entity_key in self.ENTITY_KEYS}

#         # Handle doc sites dynamically based on doc_sites_count
#         doc_sites_count = config_dict.get("doc_sites_count", 1)
#         doc_sites = {
#             f"doc_site_{i}": self.group_by_prefix(config_dict, f"doc_site_{i}")
#             for i in range(1, doc_sites_count + 1)
#         }
#         grouped_entities["doc_sites"] = doc_sites

#         # Group remaining keys
#         for entity_key in self.ENTITY_KEYS:
#             grouped_entities[entity_key].update(
#                 self.group_by_prefix(config_dict, entity_key)
#             )

#         # Update the config_dict with grouped entities
#         config_dict.update(grouped_entities)
