from __future__ import absolute_import

import io
import os
import six
from django.conf import settings
from .templates.base_command import BaseTemplateCommand


class Command(BaseTemplateCommand):
    help = 'Checks all templates to raise some warnings'

    def _handle(self):
        single_use = []
        never_used = []
        for template_name, info in six.iteritems(self.template_nodes):
            if len(info["included_in"]) == 1:
                single_use.append(template_name)

            if (len(info["included_in"]) == 0 and
               not info['node'].parent and
               not info['node'].children):
                never_used.append(template_name)

        never_used = [
            n
            for n, found in six.iteritems(self._found_in_python_files(never_used))  # noqa
            if not found
        ]

        single_use.sort()
        never_used.sort()

        self.print_yellow("Templates included only once:")
        if single_use:
            self._print_list(single_use)
        else:
            self.print_white("None")

        self.print_red("Templates never included or inherited and not found in"
                       " python files")

        if never_used:
            self._print_list(never_used)
        else:
            self.print_white("None")

    def _found_in_python_files(self, text_list):
        text_map = {text: False for text in text_list}

        for root, dirs, files in os.walk(settings.APPLICATION_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".py"):
                    file_content = io.open(file_path, encoding='utf-8').read()
                    for text in text_list:
                        if text in file_content:
                            text_map[text] = True
        return text_map

    def _print_list(self, items):
        for template_name in items:
            info = self.template_nodes[template_name]
            self.print_white(
                "%s\t(height=%d, includes=%d)" % (
                    template_name,
                    info['node'].height,
                    len(info['includes'])
                )
            )
