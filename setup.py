import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'bsm', 'BSM_VERSION')) as version_file:
    version = version_file.read().strip()

with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name = 'bsm',
    version = version,
    description = 'Bundled software manager',
    long_description = long_description,
    url = 'https://github.com/bsmhep/bsm',
    author = 'Xianghu Zhao',
    author_email = 'zhaoxh@ihep.ac.cn',
    license = 'MIT',

    classifiers = [
        'Development Status :: 5 - Production/Stable',

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

    keywords = 'bsm',
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
            'bsm_cmd = bsm:main',
        ],
    },
)
