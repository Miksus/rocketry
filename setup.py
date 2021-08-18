from setuptools import setup, find_packages
import versioneer

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="powerbase",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Mikael Koli",
    author_email="koli.mikael@gmail.com",
    packages=find_packages(),
    description="Advanced Task Launch System (scheduling)",
    long_description=long_description,
    long_description_content_type="text/markdown",
     classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
     ],
     include_package_data=True, # for MANIFEST.in
     python_requires='>=3.6.6',

    install_requires = [
        'pandas >= 1.0.0',
        'pytest >= 5.0.1',
        'psutil >= 5.7.0',
        'pyyaml >= 5.3.1'
    ],
)
