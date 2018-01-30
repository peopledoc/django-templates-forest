import re
from django.template.loader import get_template


class IncludeTemplatesParser(object):

    def search_included(self, template):
        content = template.source
        pattern = re.compile(
            r"\{\%\s?include ([^%]+)[\swith]?\s?\%\}",
            re.MULTILINE | re.IGNORECASE
        )
        matches = re.finditer(pattern, content)

        if not matches:
            return

        for match in matches:
            template_name = (match.group(1)
                                  .strip()
                                  .replace('"', '')
                                  .replace("'", ""))
            yield template_name.split(" with ")[0]

    def included_templates(self, template_name):
        return self.search_included(get_template(template_name).template)
