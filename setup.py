# -*- coding: utf-8 -*-
"""Python package description."""
from setuptools import setup, find_packages


def readme():
    """Load the readme file."""
    with open('README.rst') as readme_file:
        return readme_file.read()


setup(
    name='btlewrap',
    version='0.0.2',
    description='wrapper around different bluetooth low energy backends',
    url='https://github.com/ChristianKuehnel/btlewrap',
    author='Christian Kuehnel',
    author_email='christian.kuehnel@gmail.com',
    long_description=readme(),
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    packages=find_packages(),
    keywords='bluetooth low-energy ble',
    zip_safe=False,
    extras_require={'testing': ['pytest']}
)
