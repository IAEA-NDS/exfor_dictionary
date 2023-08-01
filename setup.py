from setuptools import setup, find_packages


def read_requirements(file):
    with open(file) as f:
        return f.read().splitlines()

def read_file(file):
   with open(file) as f:
        return f.read()

version = read_file("VERSION")
requirements = read_requirements("requirements.txt")

setup(
    name="exfor_dictionary",
    description="EXFOR Dictionary Parser",
    packages=find_packages(exclude=["test"]), 
    version=version,
    author="Shin Okumura/IAEA-NDS",
    author_email="s.okumura@iaea.org",
    maintainer="IAEA-NDS",
    maintainer_email="nds.contact-point@iaea.org",
    license="MIT license",
    url="https://github.com/IAEA-NDS/exfor_dictionary.git",
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
