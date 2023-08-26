import os

from jinja2 import Environment, FileSystemLoader, Template


class TemplateRenderer:
    def __init__(self, config, template_name):
        self.config = config
        self.template_name = template_name

    def _get_template(self) -> Template:
        current_dir = os.path.dirname(
            os.path.abspath(__file__)
        )  # Get the directory of the current script
        template_dir = os.path.join(
            current_dir, "templates"
        )  # Join it with the relative path to the templates directory
        env = Environment(
            loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True
        )
        template = env.get_template(self.template_name)
        return template

    def render_template(self):
        template = self._get_template()
        rendered_template = template.render(self.config)
        return rendered_template
