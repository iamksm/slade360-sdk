from setuptools import find_packages, setup

version = "0.0.1"
name = "slade360"


setup(
    name=name,
    version=version,
    packages=find_packages(),
    description="A Slade360 python SDK",
    long_description=open("README.md").read(),
    url=f"http://pip.slade360.co.ke/docs/{name}/",
    author="Kossam Ouma",
    author_email="koss797@gmail.com",
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7.*,<=3.12.*",
    install_requires=[
        "requests",
    ],
    include_package_data=True,
)
