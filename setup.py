import os

from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'bsm', 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

with open(os.path.join(HERE, 'bsm', 'BSMCLI_CMD')) as bsmcli_cmd_file:
    BSMCLI_CMD = bsmcli_cmd_file.read().strip()

with open(os.path.join(HERE, 'README.rst')) as f:
    LONG_DESCRIPTION = f.read()


setup(
    name='bsm',
    version=VERSION,
    description='Bundled software manager',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/bsmhep/bsm',
    author='Xianghu Zhao',
    author_email='xianghuzhao@gmail.com',
    license='MIT',

    classifiers=[
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

    keywords='bsm',
    packages=find_packages(exclude=[]),
    install_requires=[
        'click',
        'PyYAML',
        'packaging',
    ],
    include_package_data=True,
    tests_require=[
        'pytest',
    ],
    entry_points={
        'console_scripts': [
            BSMCLI_CMD+' = bsm.cli:main',
        ],
    },
)
