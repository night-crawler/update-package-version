from setuptools import setup, find_packages
from update_package_version import __version__

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='update-package-version',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/night-crawler/update-package-version',
    license='MIT',
    author='night-crawler',
    author_email='lilo.panic@gmail.com',
    description='A python executable that delivers a path-wide version bump feature',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'update-package-version = update_package_version.cli:main',
            'upv = update_package_version.cli:main',
        ]
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
    install_requires=['fire', 'pyyaml']
)
