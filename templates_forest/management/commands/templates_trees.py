from __future__ import absolute_import
from .templates.base_command import BaseTemplateCommand


class Command(BaseTemplateCommand):
    help = 'Inspects the templates in order to produce a schema of the'
    'templates inheritance'

    def _handle(self):
        # Find root nodes and orphans
        roots = []
        orphans = []
        for node in self.nodes_without_parents:
            height = self.template_nodes[node]['node'].height
            if height:
                roots.append((node, height))
            else:
                orphans.append(node)

        while True:
            self.print_green("Root Nodes.")
            self.print_green("1.\tShow orphans")
            for i, node in enumerate(roots):
                self.print_green(
                    "%d.\t(height=%d) %s" % (i + 2, node[1], node[0])
                )
            try:
                selected_index = input("Tree to display: ")
            except EOFError:
                return

            if not selected_index:
                return

            if selected_index == "1":
                orphans.sort()
                for template in orphans:
                    self.print_white(
                        "%s\t(%s incl. templates)" % (
                            template,
                            len(self.template_nodes[template]['includes'])
                        )
                    )
            else:
                base_node = roots[int(selected_index) - 2][0]
                self.print_tree(self.template_nodes[base_node]['node'])
