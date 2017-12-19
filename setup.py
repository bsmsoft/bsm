import sys
import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['tests']

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'cepcenv', 'CEPCENV_VERSION')) as version_file:
    version = version_file.read().strip()

with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name = 'cepcenv',
    version = version,
    description = 'CEPC software management toolkit',
    long_description = long_description,
    url = 'https://github.com/cepc/cepcenv',
    author = 'Xianghu Zhao',
    author_email = 'zhaoxh@ihep.ac.cn',
    license = 'MIT',

    classifiers = [
        'Development Status :: 4 - Beta',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: System :: Software Distribution',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords = 'CEPC',
    packages = find_packages(exclude=[]),
    install_requires = [
        'paradag',
        'click>=6.0,<7.0',
        'PyYAML>=3.0,<4.0',
        'distro',
    ],
    include_package_data = True,
    tests_require = [
        'pytest',
    ],
    entry_points = {
        'console_scripts': [
            'cepcenv_cmd = cepcenv:main',
        ],
    },
    cmdclass = {'test': PyTest},
)
