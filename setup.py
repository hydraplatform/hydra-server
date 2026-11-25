#This is just a work-around for a Python2.7 issue causing
#interpreter crash at exit when trying to log an info message.
try:
    import logging
    import multiprocessing
except:
    pass

import platform
import sys
import os

py_version = sys.version_info[:2]

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires=[
    "hydra-base",
    "lxml",
    "spyne @ git+https://github.com/arskom/spyne.git@af96bf95feb7950617640671f8aba9654f31acd3",
    "click",
    "requests",
    ]

if platform.system() == "Windows":  # only add winpaths when platform is Windows so that setup.py is universal
    install_requires.append("winpaths")

setup(
    name='hydra-server',
    use_scm_version=True,  # from the git tag; see pyproject.toml
    description='A JSON RPC server front end for the hydra-base network manager',
    author='Stephen Knox',
    author_email='stephen.knox@manchester.ac.uk',
    url='https://github.com/hydraplatform/hydra-server',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        'console_scripts': ['hydra-server=hydra_server.cli:start_cli']
    },
    zip_safe=False,
)
