from django.test import SimpleTestCase
from templates_forest.management.commands.templates.base_command import BaseTemplateCommand  # noqa


class MockCommand(BaseTemplateCommand):
    def _handle(self):
        pass


class TemplatesTreesTesCase(SimpleTestCase):

    def test_basic_inheritance(self):
        cmd = MockCommand()
        options = {
            'vars': [],
            'include-packages': False,
            'quiet': True,
            'no_color': True,
        }
        cmd.execute(**options)
        base_template = 'basic_inheritance/base.html'
        child_template = 'basic_inheritance/child.html'

        self.assertIn(
            base_template,
            cmd.nodes_without_parents
        )

        base_node = cmd.template_nodes[base_template]['node']
        child_node = cmd.template_nodes[child_template]['node']

        self.assertEquals(base_node.height, 1)
        self.assertTrue(base_node.is_root)
        self.assertEquals(base_node.descendants[0], child_node)

        self.assertEquals(child_node.height, 0)
        self.assertTrue(child_node.is_leaf)
        self.assertEquals(child_node.parent, base_node)
