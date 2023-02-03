from setuptools import setup

setup(
    name='contxt',
    version='0.1.0',
    py_modules=['contxt'],
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'contxt = contxt.cli:cli',
        ],
    },
)