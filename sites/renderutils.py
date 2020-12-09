from jinja2 import (
    Environment,
    BaseLoader,
    TemplateNotFound
)

from themes.models import (
    SiteThemeTemplate,
    SiteThemeSection
)

class DatabaseLoader(BaseLoader):

    def __init__(self, theme):
        self.theme = theme

    def get_source(self, environment, template):
        try:
            if template.startswith("templates/"):
                tmpl = SiteThemeTemplate.objects.get(
                    site_theme=self.theme,
                    name=template.split("templates/")[1])
            elif template.startswith("sections/"):
                tmpl = SiteThemeSection.objects.get(
                    site_theme=self.theme,
                    name=template.split("sections/")[1])
            else:
                tmpl = SiteThemeTemplate.objects.get(
                    site_theme=self.theme,
                    name=template)

            return tmpl.content, template, None

        except SiteThemeTemplate.DoesNotExist:
            raise TemplateNotFound
        except SiteThemeSection.DoesNotExist:
            raise TemplateNotFound


def render(template, context):
    """

    :param template:
    :param context:
    :return:
    """
    env = Environment(loader=DatabaseLoader(template.site_theme))
    jinja2_template = env.get_template(template.name)
    print("here")

    return jinja2_template.render(**context)


