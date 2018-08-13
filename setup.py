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
from packaging.version import Version

py_version = sys.version_info[:2]

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

# get version string from __init__.py
with open(os.path.join(os.path.dirname(__file__), "hydra_server", "__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            version = Version(line.split("=")[1].strip().strip("\"'"))

install_requires=[
    "hydra-base",
    "lxml",
    "spyne", 
    "click",
    ]

dependency_links=[
    "git+https://github.com/arskom/spyne.git@spyne-2.13.2-alpha#egg=spyne",
]

if platform.system() == "Windows":  # only add winpaths when platform is Windows so that setup.py is universal
    install_requires.append("winpaths")

setup(
    name='hydra-server',
    version=str(version),
    description='A JSON RPC server front end for the hydra-base network manager',
    author='Stephen Knox',
    author_email='stephen.knox@manchester.ac.uk',
    url='https://github.com/hydraplatform/hydra-server',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    dependency_links=dependency_links,
    include_package_data=True,
    entry_points={
        'console_scripts': ['hydra-server=hydra_server.commands:start_cli']
    },
    zip_safe=False,
)
