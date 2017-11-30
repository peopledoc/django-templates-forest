from __future__ import absolute_import

from .templates.base_command import BaseTemplateCommand


class Command(BaseTemplateCommand):
    help = 'Returns the template trees where the template is included'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('template_name',
                            nargs="?",
                            help='Template name to search.')

    def _handle(self):
        template_name = self.options['template_name']
        if not template_name:
            return

        template_node = self.template_nodes[template_name]
        ancestors = template_node['node'].ancestors

        # Display the template's tree
        self.print_yellow("\nTemplate Tree:\n")
        if ancestors:
            oldest = self.template_nodes[ancestors[0].name]
            self.print_tree(oldest['node'], highlight_template=template_name)
        elif template_node['node'].height:
            self.print_tree(
                template_node['node'],
                highlight_template=template_name
            )
        else:
            self.print_white("Not a tree")

        # list of templates directly included in the current template
        self.print_yellow("\nTemplates included in %s:\n" % template_name)
        if not template_node["includes"]:
            self.print_white("None")
        else:
            for template in template_node["includes"]:
                self.print_white(template)

        # display the trees where the current template has been included
        self.print_yellow("\nTrees where %s is included:\n" % template_name)

        hosts = self.template_nodes[template_name]['included_in']
        if not hosts:
            self.print_white("None")
            return

        host_roots = set()
        for host in hosts:
            ancestors = self.template_nodes[host]['node'].ancestors
            if ancestors:
                host_roots.add(ancestors[0].name)
            else:
                host_roots.add(host)

        for root in host_roots:
            self.print_white("\n============\n")
            self.print_tree(
                self.template_nodes[root]['node'],
                highlight_template=hosts
            )
