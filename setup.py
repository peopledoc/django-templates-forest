import os
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read().strip()


README = read_relative_file('README.md')
version = '0.0.1'

if __name__ == '__main__':
    setup(
        name='templates-forest',
        version=version,
        author='Peopledoc',
        packages=[
            'templates_forest',
            'templates_forest.management',
            'templates_forest.management.commands',
            'templates_forest.management.commands.templates'
        ],
        description='Template Forest is a series of django commands that might'
                    ' help you visualize your\'s templates inheritance.',
        long_description=README,
        install_requires=[
            'Django>=1.8',
            'anytree',
        ],
    )
