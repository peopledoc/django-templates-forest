from __future__ import absolute_import

import os
from django.conf import settings
from .templates.base_command import BaseTemplateCommand


class Command(BaseTemplateCommand):
    help = 'Checks all templates to raise some warnings'

    def _handle(self):
        single_use = []
        never_used = []
        for template_name, info in self.template_nodes.iteritems():
            if len(info["included_in"]) == 1:
                single_use.append(template_name)

            if (len(info["included_in"]) == 0 and
               not info['node'].parent and
               not info['node'].children):
                never_used.append(template_name)

        never_used = [
            n
            for n, found in self._found_in_python_files(never_used).iteritems()
            if not found
        ]

        single_use.sort()
        never_used.sort()

        self.print_yellow("Templates included only once:")
        self._print_list(single_use)

        self.print_red("Templates never included or inherited and not found in"
                       " python files")
        self._print_list(never_used)

    def _found_in_python_files(self, text_list):
        text_map = {text: False for text in text_list}

        for root, dirs, files in os.walk(settings.APPLICATION_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".py"):
                    for text in text_list:
                        if text in open(file_path, 'r').read().decode('utf-8'):
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
