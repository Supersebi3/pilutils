from setuptools import setup, find_namespace_packages
from pilutils import __version__ as pilutils_version

name = "pilutils"


def long_description():
    with open("README.md") as fp:
        return fp.read()


def parse_requirements_file(path):
    with open(path) as fp:
        dependencies = (d.strip() for d in fp.read().split("\n") if d.strip())
        return [d for d in dependencies if not d.startswith("#")]


setup(
    name="pilutils",
    version=pilutils_version,
    description="A simple module with some helper functions for Pillow.",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    author="Supersebi3",
    author_email="gdsupersebi3@gmail.com",
    url="https://github.com/Supersebi3/pilutils",
    packages=find_namespace_packages(include=[name + "*"]),
    install_requires=parse_requirements_file("requirements.txt"),
    python_requires=">=3.8.0,<3.10",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
