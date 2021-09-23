from os.path import dirname, join

from setuptools import find_packages, setup

setup(
    name='myapp',
    description='Simplified implementation of the grep utility',
    version='1.0',
    author='Oleg Smirnov',
    author_email='sm-oleg1209@yandex.ru',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    entry_points={'console_scripts': ['mygrep = myapp.app:main']},
)
