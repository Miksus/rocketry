import sys

sys.stderr.write("""
Unsupported installation method: python setup.py
Please use `python -m pip install .` instead.
"""
)
#sys.exit(1)
from setuptools import setup

setup(
    name="rocketry",
    install_requires = [
        'python-dateutil', 'redbird>=0.5.0', 'pydantic'
    ],
)
