from django.test import SimpleTestCase
from templates_forest.management.commands.templates.base_command import BaseTemplateCommand  # noqa


class MockCommand(BaseTemplateCommand):
    """
    We mock a command that inherits from BaseTemplateCommand, we only want
    to execute the base command and test the results
    """
    def _handle(self):
        pass


class BaseCommandTesCase(SimpleTestCase):

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
        grandchild_template = 'basic_inheritance/grandchild1.html'

        self.assertIn(
            base_template,
            cmd.nodes_without_parents
        )

        base_node = cmd.template_nodes[base_template]['node']
        child_node = cmd.template_nodes[child_template]['node']
        grandchild_node = cmd.template_nodes[grandchild_template]['node']

        self.assertEquals(base_node.height, 2)
        self.assertTrue(base_node.is_root)
        self.assertEquals(base_node.descendants[0], child_node)

        self.assertEquals(child_node.height, 1)
        self.assertFalse(child_node.is_leaf)
        self.assertEquals(child_node.parent, base_node)

        self.assertEquals(grandchild_node.height, 0)
        self.assertTrue(grandchild_node.is_leaf)
        self.assertEquals(grandchild_node.parent, child_node)

    def test_conditional_inheritance_default(self):
        """
        No vars passed to the command in templates that use yesno conditions
        to select the parent template.
        """
        cmd = MockCommand()
        options = {
            'vars': [],
            'include-packages': False,
            'quiet': True,
            'no_color': True,
        }
        cmd.execute(**options)
        base1_template = 'conditional_inheritance/base1.html'
        base2_template = 'conditional_inheritance/base2.html'
        child_template = 'conditional_inheritance/child.html'
        base1_node = cmd.template_nodes[base1_template]['node']
        base2_node = cmd.template_nodes[base2_template]['node']
        child_node = cmd.template_nodes[child_template]['node']

        # Base1 should not have descendants
        self.assertEquals(base1_node.height, 0)
        self.assertTrue(base1_node.is_root)
        self.assertFalse(base1_node.descendants)

        # base2 was select as parent of "child"
        self.assertEquals(base2_node.height, 1)
        self.assertTrue(base2_node.is_root)
        self.assertEquals(base2_node.descendants[0], child_node)

        # child's parent should be base2
        self.assertEquals(child_node.height, 0)
        self.assertTrue(child_node.is_leaf)
        self.assertEquals(child_node.parent, base2_node)

    def test_conditional_inheritance_using_vars(self):
        """
        Set the value for the context in templates that use yesno conditions
        to select the parent template.
        """
        cmd = MockCommand()
        options = {
            'vars': ['my_parent.use_first=True'],
            'include-packages': False,
            'quiet': True,
            'no_color': True,
        }
        cmd.execute(**options)
        base1_template = 'conditional_inheritance/base1.html'
        base2_template = 'conditional_inheritance/base2.html'
        child_template = 'conditional_inheritance/child.html'
        base1_node = cmd.template_nodes[base1_template]['node']
        base2_node = cmd.template_nodes[base2_template]['node']
        child_node = cmd.template_nodes[child_template]['node']

        # Base1 should be parent of children
        self.assertEquals(base1_node.height, 1)
        self.assertTrue(base1_node.is_root)
        self.assertEquals(base1_node.descendants[0], child_node)

        # base2 should not be parent
        self.assertEquals(base2_node.height, 0)
        self.assertTrue(base2_node.is_root)
        self.assertFalse(base2_node.descendants)

        # child's parent should be base1
        self.assertEquals(child_node.height, 0)
        self.assertTrue(child_node.is_leaf)
        self.assertEquals(child_node.parent, base1_node)
