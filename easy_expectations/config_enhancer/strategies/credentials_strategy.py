from easy_expectations.config_enhancer.system_config import ConstantsConfig

from .base_strategy import BaseStrategy


class ResolveCloudAttributesStrategy(BaseStrategy):
    """
    A strategy class for resolving cloud attributes based on the provided
    context.
    """

    def __init__(self):
        self.constants_config = ConstantsConfig()

    def compute(self, context):
        """
        Resolves cloud attributes based on the provided context.

        Args:
            context (dict): The context dictionary containing the attributes.

        Returns:
            dict: The updated context dictionary with resolved cloud
            attributes.
        """
        # Iterate through a copy of the keys in the context to avoid modifying the dictionary during iteration
        for key, value in list(context.items()):
            if key.endswith("_type"):
                # Get the prefix for the current entity (e.g., "data_connector" for "data_connector_type")
                entity_prefix = key[:-5]

                # Retrieve the cloud options associated with the cloud type using ConstantsConfig
                cloud_options = self.constants_config.get_cloud_options(value)

                # Iterate through the attributes associated with the cloud type
                for attribute in cloud_options:
                    # Check if the specific attribute is already defined for the entity
                    entity_attribute_key = f"{entity_prefix}_{attribute}"
                    if entity_attribute_key not in context:
                        # Check if there is a default value for the attribute
                        default_attribute_key = f"default_{attribute}"
                        if default_attribute_key in context:
                            # If there is a default value, add the entity-specific attribute to the context
                            context[entity_attribute_key] = context[
                                default_attribute_key
                            ]

        return context


# class ResolveCloudAttributesStrategy(BaseStrategy):
#     # Mapping of cloud types to their corresponding attribute keys
#     ATTRIBUTE_MAPPING = {
#         "gcs": ("gcp_project",),
#         "s3": (
#             "boto_endpoint",
#             "s3_region",
#             "aws_access_key_id",
#             "aws_secret_access_key",
#             "aws_session_token",
#             "assume_role_arn",
#             "assume_role_duration",
#         ),
#         "azure": (
#             "azure_connection_string",
#             "azure_account_url",
#             "azure_protected_container_credentials",
#         ),
#     }

#     def compute(self, config_dict, context):
#         # Iterate through a copy of the keys in the config_dict to avoid modifying the dictionary during iteration
#         for key, value in list(config_dict.items()):
#             if key.endswith("_type") and value in self.ATTRIBUTE_MAPPING:
#                 # Get the prefix for the current entity (e.g., "data_connector" for "data_connector_type")
#                 entity_prefix = key[:-5]

#                 # Iterate through the attributes associated with the cloud type
#                 for attribute in self.ATTRIBUTE_MAPPING[value]:
#                     # Check if the specific attribute is already defined for the entity
#                     entity_attribute_key = f"{entity_prefix}_{attribute}"
#                     if entity_attribute_key not in config_dict:
#                         # Check if there is a default value for the attribute
#                         default_attribute_key = f"default_{attribute}"
#                         if default_attribute_key in config_dict:
#                             # If there is a default value, add the entity-specific attribute to the config_dict
#                             config_dict[entity_attribute_key] = config_dict[
#                                 default_attribute_key
#                             ]
