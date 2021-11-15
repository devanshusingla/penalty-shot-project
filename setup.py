from setuptools import setup, find_packages

setup(
    name="psp",
    version="1.0",
    packages=find_packages(
        exclude=[
            "examples",
            "examples.*",
            "saved_policies",
            "saved_policies.*",
            "gym-env",
            "gym-env.*",
        ],
    ),
    install_requires=[
        "numpy<1.21,>=1.17",
        "tianshou==0.4.4",  # to match tensorflow's minimal requirements
        "smurves==1.0.1",
        "matplotlib>3.4",
        "pyglet==1.5.0",
    ],
)
