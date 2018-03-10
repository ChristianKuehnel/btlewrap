"""Python package description."""
from setuptools import setup, find_packages

setup(
    name='btle',
    version='0.0.1',
    description='wrapper around different bluetooth low energy backends',
    url='https://github.com/ChristianKuehnel/btlewrap',
    author='Christian Kühnel',
    author_email='christian.kuehnel@gmail.com',
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
