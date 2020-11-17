import re
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


with open("befaas/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)


setuptools.setup(
    name="befaas", # Replace with your own username
    version=version,
    author="befaas",
    author_email="befaas@test.com",
    description="Function and classes for analyzing befaas experiments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Be-FaaS/BeFaaS-analysis",
    packages=setuptools.find_packages(),
    install_requires=[
        "json_coder==0.5",
        "argmagic==1.0.1",
        "networkx",
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
