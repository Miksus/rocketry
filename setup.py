from setuptools import setup, find_packages


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="PyPipe",
    version="0.1.0",
    author="Mikael Koli",
    author_email="koli.mikael@gmail.com",
    packages=find_packages(),
    description="Scheduling library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
     classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
     ],
     include_package_data=True, # for MANIFEST.in
     python_requires='>=3.6.6',
)
