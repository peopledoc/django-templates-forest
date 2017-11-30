from django.template.base import Node
from django.template.loader_tags import IncludeNode, ExtendsNode
from django.template.loader import get_template


class IncludeTemplatesParser(object):

    def walk_nodes(self, node, original=None, context=None):
        if original is None:
            original = node
        for n in self.get_nodelist(node, original, context):
            if isinstance(n, IncludeNode):
                yield n.template.var
            else:
                for n1 in self.walk_nodes(n, original, context):
                    yield n1

    def get_nodelist(self, node, original, context):
        if isinstance(node, ExtendsNode):
            return getattr(node, 'nodelist', [])

        nodelist = []
        if isinstance(node, Node):
            for attr in node.child_nodelists:
                nodelist += getattr(node, attr, [])
        else:
            nodelist = getattr(node, 'nodelist', [])
        return nodelist

    def _get_node(self, template, context=None):
        for node in template:
            if isinstance(node, IncludeNode):
                return node
            elif isinstance(node, ExtendsNode):
                return self._get_node(node.nodelist, context)
        return []

    def included_templates(self, template_name):
        return self.walk_nodes(get_template(template_name).template)
