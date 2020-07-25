from setuptools import setup, find_namespace_packages

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
    version="0.0.0.1",
    description="A small extension module for PIL/Pillow",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    author="supersebi3",
    author_email="supersebi3@gmail.com",
    url="https://github.com/supersebi3/pilutils",
    install_requires=parse_requirements_file("requirements.txt"),
    packages=find_namespace_packages(include=[name + "*"]),
    python_requires=">=3.8.0,<3.10",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
