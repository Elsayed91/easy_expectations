from .base_strategy import BaseStrategy


class RunNameTemplateStrategy(BaseStrategy):
    def compute(self, context):
        run_name_template = context.get("run_name_template", None)
        if not run_name_template:
            context[
                "run_name_template"
            ] = f"%Y%m%d%H%M-{context.get('data_connector_name')}"
