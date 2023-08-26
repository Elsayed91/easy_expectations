# from easy_expectations.cerberus_validation.cerberus_validator import validate_schema
import json

import yaml

from easy_expectations.config_enhancer.enhancer import Enhancer
from easy_expectations.config_mapper.mapper import ConfigMapper
from easy_expectations.template_renderer.renderer import TemplateRenderer
from easy_expectations.utils.logger import logger
from easy_expectations.utils.yaml_handler import YamlHandler
from easy_expectations.wrapper.wrapper import GreatExpectationsWrapper


def save_to_yaml(data, filename):
    with open(filename, "w") as file:
        yaml.dump(data, file)


def parse_config(user_config):
    return YamlHandler().parse_input(user_config)


def enhance_config(config):
    enhancer = Enhancer()
    return enhancer.process(config)


def render_template(config_dict, template_name):
    return TemplateRenderer(config_dict, template_name).render_template()


def build_ge_wrapper(ge_config, cp_config, enhanced_config_dict, enable=True):
    wrapper = (
        GreatExpectationsWrapper(
            ge_config, cp_config, enhanced_config_dict, enable
        )
        .with_data_context()
        .with_checkpoint()
        .with_expectations_suite()
        .with_run_checkpoint()
        .with_data_docs()
        .with_summary_table()
        .with_check_success_threshold()
        .with_clean_temp()
        .build()
    )
    return wrapper


def main(
    user_config,
    mapping=None,
    mapping_key=None,
    save_configs=False,
    build_wrapper=True,
):
    parsed_config = parse_config(user_config)
    mapper = ConfigMapper(
        parsed_config, mapping=mapping, mapping_key=mapping_key
    )
    enhanced_config_dict = enhance_config(mapper.config)
    logger.info(
        f"generated configuration:\n{json.dumps(enhanced_config_dict, indent=4)}"
    )

    ge_config = render_template(enhanced_config_dict, "great_expectations.tpl")
    cp_config = render_template(enhanced_config_dict, "checkpoint.tpl")
    if save_configs:
        save_to_yaml(ge_config, "great_expectations.yaml")
        save_to_yaml(cp_config, "checkpoint.yaml")

    if build_wrapper:
        wrapper = build_ge_wrapper(ge_config, cp_config, enhanced_config_dict)
        return wrapper


# def main(user_config, mapping=None, mapping_key=None):
#     print("running config mapper")
#     mapper = ConfigMapper(
#         YamlHandler().parse_input(user_config),
#         mapping=mapping, mapping_key=mapping_key)
#     enhancer = Enhancer()
#     enhanced_config_dict = enhancer.process(mapper.config)
#     print(json.dumps(enhanced_config_dict, indent=4))
#     ge_config = TemplateRenderer(
#         enhanced_config_dict, "great_expectations.tpl"
#     ).render_template()
#     cp_config = TemplateRenderer(
#         enhanced_config_dict, "checkpoint.tpl"
#     ).render_template()
#     wrapper = (
#         GreatExpectationsWrapper(ge_config, cp_config, enhanced_config_dict, True)
#         .with_data_context()
#         .with_checkpoint()
#         .with_expectations_suite()
#         .with_run_checkpoint()
#         .with_data_docs()
#         .with_summary_table()
#         .with_check_success_threshold()
#          .with_clean_temp()
#         .build()
#     )
#     return wrapper
