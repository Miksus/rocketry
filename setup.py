from setuptools import setup, find_packages
import versioneer

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="redengine",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Mikael Koli",
    author_email="koli.mikael@gmail.com",
    url="https://github.com/Miksus/red-engine.git",
    packages=find_packages(),
    description="Advanced scheduling framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
     classifiers=[
         "Development Status :: 5 - Production/Stable",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",

        "Topic :: Office/Business :: Scheduling",

        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
     ],
     include_package_data=True, # for MANIFEST.in
     python_requires='>=3.6.0',

    install_requires = [
        'pandas', 'redbird', 'pydantic'
    ],
    extras_require={
        "full": [
            "networkx", "matplotlib"
        ],
    },
)
