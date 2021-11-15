"""The setup.py file contains certain instructions and metadata for pip (python's package manager). Namely, we define
the name of the package, the version, and package requirements here (any package mentioned in requirements will be
installed by pip alongside our custom enviroment package).
"""
from setuptools import setup

setup(
    name="gym_env",  # Use same name as sibling directory.
    version="1.0.0",  # Version number.
    install_requires=[
        "gym",
        "numpy",
        "torch",
        "tianshou",
        "wandb",
        "smurves",
    ],  # Python packages required by our environments.
)
