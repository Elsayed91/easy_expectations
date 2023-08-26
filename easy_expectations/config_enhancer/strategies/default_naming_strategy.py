from .base_strategy import BaseStrategy


class ResolveStoreAndConnectorNamingStrategy(BaseStrategy):
    def __init__(self):
        self.names = [
            "data_connector",
            "expectations_store",
            "validations_store",
            "checkpoint_store",
        ]

    def compute(self, context):
        for name_key in self.names:
            self.resolve_name(context, name_key)

    def resolve_name(self, context, name_key):
        name_value = context.get(f"{name_key}_name", None)
        type_value = context.get(f"{name_key}_type", None)
        if name_value is None and type_value is not None:
            default_name = f"{type_value}_{name_key}"
            context[f"{name_key}_name"] = default_name
        elif name_value is None and type_value is None:
            default_name = f"local_{name_key}"
            context[f"{name_key}_name"] = default_name


class ResolveEvaluationParameterStoreNamingStrategy(BaseStrategy):
    def compute(self, context):
        if (
            "evaluation_parameter_store_name" not in context
            and "checkpoint_store_name" in context
        ):
            name = "evaluation_parameter_store"
            context["evaluation_parameter_store_name"] = name


class CheckpointNameStrategy(BaseStrategy):
    def compute(self, context):
        if "checkpoint_name" not in context:
            data_connector_type = context.get("data_connector_type")
            if data_connector_type:
                context["checkpoint_name"] = f"{data_connector_type}_checkpoint"


# class ExpectationsSuiteNameStrategy(BaseStrategy):
#     def compute(self, context):
#         if "expectations_suite_name" not in context:
#             data_connector_type = context.get("data_connector_type")
#             if data_connector_type:
#                 context["expectations_suite_name"] = f"{data_connector_type}_suite"


class ExpectationsSuiteNameStrategy(BaseStrategy):
    def compute(self, context):
        # Check if 'expectations_suite_name' is already in the context
        if "expectations_suite_name" in context:
            return

        # If 'expectations_file' exists and neither 'contract_tests' nor 'tests' exist or are empty
        if context.get("expectations_file") and not (
            context.get("contract_tests") or context.get("tests")
        ):
            context["expectations_suite_name"] = context["expectations_file"]

        # If 'contract_tests' exist
        elif context.get("contract_tests"):
            # Use 'contract_suite_name' if it exists
            if "contract_suite_name" in context:
                context["expectations_suite_name"] = context["contract_suite_name"]
            # Or set a default one based on 'data_connector_type'
            else:
                data_connector_type = context.get(
                    "data_connector_type", "default_connector"
                )
                context[
                    "expectations_suite_name"
                ] = f"{data_connector_type}_data_contract"

        # If 'tests' exist
        elif context.get("tests"):
            # Use 'expectations_suite_name' if it exists
            if "expectations_suite_name" in context:
                context["expectations_suite_name"] = context["expectations_suite_name"]
            # Or set a default one based on 'data_connector_type'
            else:
                data_connector_type = context.get(
                    "data_connector_type", "default_connector"
                )
                context["expectations_suite_name"] = f"{data_connector_type}_suite"


class ResolveDocSiteNamingStrategy(BaseStrategy):
    def compute(self, context):
        doc_sites_count = context.get("doc_sites_count", 0)
        for i in range(1, doc_sites_count + 1):
            name_key = f"doc_site_{i}"
            self.resolve_name(context, name_key, doc_site=True)

    def resolve_name(self, context, name_key, doc_site=False):
        name_value = context.get(f"{name_key}_name", None)
        type_value = context.get(f"{name_key}_type", None)
        if name_value is None and type_value is not None:
            default_name = (
                f"{type_value}_doc_site" if doc_site else f"{type_value}_{name_key}"
            )
            context[f"{name_key}_name"] = default_name
