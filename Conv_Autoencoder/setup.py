# setup.py

from setuptools import setup, find_packages

setup(
    name='Conv_Library',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'tensorflow',
        'keras',
        'scikit-image',
        'opencv-python',
    ],
    author='Venkatesh Jyothula',
    description='Library for Color Constancy Model.',
)


