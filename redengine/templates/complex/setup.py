from setuptools import setup, find_packages

setup(
    name='my_package', # <TARGET>
    version='0.1.0',
    url='https://github.com/<TARGET>.git',
    author='Author Name',
    author_email='author@gmail.com',
    description='Description of my package',
    packages=find_packages(),    
    install_requires=['redengine'],
    include_package_data=True, # for MANIFEST.in
)