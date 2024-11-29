from setuptools import setup, find_packages

BASE_REQUIREMENTS = ["brain-slam", "dash", "plotly", "nibabel", "numpy", "scipy", "trimesh"]
TEST_REQUIREMENTS = ["flake8", "autopep8", "pytest", "pytest-cov", "coveralls"]

setup(
    name="slamviz",
    version="0.0.0",
    packages=find_packages(),
    author="The MeCA Team",
    description="Surface anaLysis And Modeling",
    url="https://github.com/brain-slam/slamviz",
    license="MIT",
    python_requires=">=3.8",  # enforce Python 3.6 as minimum
    install_requires=BASE_REQUIREMENTS,
    extras_require={"dev": TEST_REQUIREMENTS},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
    ],
)
