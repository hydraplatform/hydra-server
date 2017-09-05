#This is just a work-around for a Python2.7 issue causing
#interpreter crash at exit when trying to log an info message.
try:
    import logging
    import multiprocessing
except:
    pass

import platform
import sys
py_version = sys.version_info[:2]

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs=[
               'nose',
               'coverage',
               ]

install_requires=[
    "beaker",
    "zope.sqlalchemy >= 0.4",
    "sqlalchemy",
    "pandas",
    "numpy",
    "bcrypt",
    "lxml",
    "mysql-connector-python",
    "spyne >= 2.12",
    "python-dateutil",
    "hydra-base"
    ]

if platform.system() == "Windows":  # only add winpaths when platform is Windows so that setup.py is universal
    install_requires.append("winpaths")

setup(
    name='hydra-server',
    version='0.1',
    description='A JSON RPC server front end for the hydra-base network manager',
    author='Stephen Knox',
    author_email='stephen.knox@manchester.ac.uk',
    url='https://github.com/hydraplatform/hydra-server',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'hydra-server': []},
    message_extractors={'hydra-server': [
            ('**.py', 'python', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points = {
                'setuptools.installation': [
                    'eggsecutable = server:run',
                ]
    },
    zip_safe=False,
    dependency_links=['http://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.4.zip'],
)
