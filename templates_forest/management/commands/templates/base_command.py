import os
import logging
from anytree import Node, RenderTree
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.template.loader_tags import ExtendsNode
from django.template.loaders.app_directories import get_app_template_dirs
from .parsers import IncludeTemplatesParser


class BaseTemplateCommand(BaseCommand):

    def __init__(self, *args, **kwargs):
        self.parser = IncludeTemplatesParser()
        super(BaseTemplateCommand, self).__init__(*args, **kwargs)

    def print_green(self, message):
        """
        Print in green
        """
        self.stdout.write(self.style.HTTP_REDIRECT(message))

    def print_red(self, message):
        """
        Print in red
        """
        self.stdout.write(self.style.ERROR(message))

    def print_yellow(self, message):
        """
        Print in yellow
        """
        self.stdout.write(self.style.WARNING(message))

    def print_white(self, message):
        """
        Print in white
        """
        self.stdout.write(message)

    def add_arguments(self, parser):
        super(BaseTemplateCommand, self).add_arguments(parser)
        parser.add_argument('--quiet',
                            action='store_true',
                            dest='quiet',
                            default=False,
                            help='Displays warnings when loading files.')
        parser.add_argument('--include-packages',
                            action='store_true',
                            dest='include-packages',
                            default=False,
                            help='Include templates from external packages')
        parser.add_argument('--vars',
                            nargs='+',
                            default=[],
                            help="Space separated list vars and values: "
                                 "e.g. --vars foo=true bar=something")

    def get_parent(self, template, quiet=False):
        """
        Using django's functions we'll try to get the template's parent
        """
        var = None
        try:
            # if template == "mails/routing_action/body.html":
            #     import ipdb; ipdb.set_trace()

            nodes = get_template(template).template.nodelist

            if not nodes or not isinstance(nodes[0], ExtendsNode):
                # template has no "extends" node, so it has no parent
                return
            parent = nodes[0].parent_name

            # parent = get_template(template).template.nodelist[0].parent_name
            token = parent.token.replace('"', '').replace("'", '')
            var = str(parent.var)
        except AttributeError as e:
            if not quiet:
                logging.warning("WTF when loading %s: %s" % (template, e))
            pass
        except Exception as e:
            if not quiet:
                logging.warning("Can't load template %s: %s" % (template, e))
            pass

        # check if there's a yesno condition:
        # {% extends some_var|yesno:parent1.html,parent2.html" %})
        if var and var != token and "yesno" in token:
            parent_yes, parent_no = (token.split(':')[1]
                                          .replace('"', '')
                                          .split(','))
            # Check if we passed a value to be used on the command
            if not quiet and var not in self.context_vars:
                self.print_yellow(
                    "No value for condition var `%s` on template `%s`. "
                    "Assuming `False`: `%s`" % (var, template, parent_no)
                )
            return parent_yes if self.context_vars.get(var) else parent_no

        # check if the parent is dynamic
        # {% extends my_var %})
        if var and not var.endswith(".html"):
            if not quiet and var not in self.context_vars:
                self.print_red(
                    "Parent is dynamic on template `%s` using var `%s` "
                    "that was not passed to the command" % (template, var)
                )
            return self.context_vars.get(var)

        return var

    def get_templates(self):
        """
        Returns a list of templates (.html files) on every app
        """
        app_dir = settings.APPLICATION_DIR
        for template_dir in get_app_template_dirs('templates'):
            if not self.options['include-packages'] and not template_dir.startswith(app_dir):  # noqa
                continue
            for base_dir, dirnames, filenames in os.walk(template_dir):
                for filename in filenames:
                    if filename.endswith(".html"):
                        yield (os.path.join(base_dir, filename)
                                      .split('templates/')[-1])

    def get_template_nodes(self):
        """
        Returns a dict of templates an its nodes:
         { "template1":
            {"node": Node("template1"), "includes": ["foo.html"]
         },{
           "template2":
            {"node": Node("template2"), "includes": ["bar.html"]},
        }
        """
        # we'll create a list of tuples with templates and their parent
        # [(template1, parent1), (template2, parent1), ...]
        self.print_yellow("Parsing templates...")

        templates = set()
        for t in self.get_templates():
            parent = self.get_parent(t, self.options['quiet'])

            templates.add((t, parent))

        # initialize template_nodes
        template_nodes = {
            t: {
                "node": Node(t),
                "includes": [],
                "included_in": set()
            }
            for t, p in templates
        }

        for t, p in template_nodes.iteritems():
            includes = self.get_include_templates(t)
            p["includes"] = includes
            for i in includes:
                if i in template_nodes:
                    template_nodes[i]["included_in"].add(t)

        self.nodes_without_parents = []

        # Loop over the templates tuple list to fill the template_nodes dict
        for template, parent in templates:
            if not parent:
                self.nodes_without_parents.append(template)
                template_nodes[template]["node"].parent = None
                continue
            if parent not in template_nodes:
                includes = self.get_include_templates(parent)
                template_nodes[parent] = {
                    "node": Node(parent),
                    "includes": includes,
                    "included_in": set()
                }
                for i in includes:
                    if i in template_nodes:
                        template_nodes[i]["included_in"].add(parent)

            template_nodes[template]["node"].parent = template_nodes[parent]["node"]  # noqa
        return template_nodes

    def get_include_templates(self, template):
        """
        returns the list of included templates {% include %} found
        in the `template`
        """
        return list(self.parser.included_templates(template))

    def print_tree(self, node, highlight_template=None):
        """
        :param node: node's tree to print
        :type node: anynode Node instance
        :param highlight_template: if specified, this template will be
                                   highlighted
        :type highlight_template: string
        """
        if highlight_template is None:
            highlight_template = []
        for pre, fill, node in RenderTree(node):
            print_func = self.print_white
            if node.name in highlight_template:
                print_func = self.print_green
            print_func(
                "%s%s\t(%s incl. templates)" % (
                    pre,
                    node.name,
                    len(self.template_nodes[node.name]['includes'])
                )
            )

    def _handle(self):
        """
        to be implemented on child commands
        """
        raise NotImplementedError

    def handle(self, **options):
        self.context_vars = {}
        # parsing context vars
        for v in options['vars']:
            name, value = v.split("=")
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            self.context_vars[name] = value
        self.options = options
        # generating template nodes
        self.template_nodes = self.get_template_nodes()
        return self._handle()
