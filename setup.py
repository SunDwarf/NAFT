import os
import sys
from setuptools import setup, find_packages

rootpath = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0:2] < (3, 3):
    raise SystemError("This module cannot be used on Python 3.2 or below.")

requires = []

if sys.version_info[0:2] < (3, 5):
    requires.append("typing")


def extract_version(module='naft'):
    version = None
    fname = os.path.join(rootpath, module, '__init__.py')
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation characters.
                break
    return version


setup(
    name='naft',
    version=extract_version(),
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    url='https://github.com/SunDwarf/NAFT',
    license='MIT',
    author='Isaac Dickinson',
    author_email='sun@veriny.tf',
    description='NAFT Python bytecode interpreter',
    tests_require=['pytest>=2.9.1', 'coveralls', 'pytest-cov>=2.2.1', 'coveralls>=1.1'],
    install_requires=requires
)
