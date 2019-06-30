import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'bsm', 'VERSION')) as version_file:
    version = version_file.read().strip()

with open(os.path.join(here, 'bsm', 'BSMCLI_CMD')) as bsmcli_cmd_file:
    bsmcli_cmd = bsmcli_cmd_file.read().strip()

with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()


setup(
    name = 'bsm',
    version = version,
    description = 'Bundled software manager',
    long_description = long_description,
    url = 'https://github.com/bsmhep/bsm',
    author = 'Xianghu Zhao',
    author_email = 'xianghuzhao@gmail.com',
    license = 'MIT',

    classifiers = [
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: System :: Software Distribution',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords = 'bsm',
    packages = find_packages(exclude=[]),
    install_requires = [
        'click',
        'PyYAML',
        'packaging',
    ],
    include_package_data = True,
    tests_require = [
        'pytest',
    ],
    entry_points = {
        'console_scripts': [
            bsmcli_cmd+' = bsm.cli:main',
        ],
    },
)
