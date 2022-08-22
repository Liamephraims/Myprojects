import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Data_Validation_Toolkit',
    version='0.36.01',
    author='Liam Ephraims',
    author_email='liam.ephraims@gmail.com',
    description='Use driver functions and utility functions to run stage 1, 2 and 3 checks, can also run individual checks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Liamephraims/Myprojects',
    license='MIT',
    packages=['Data_Validation_Toolkit'],
    install_requires=['pyathena', 'pandas'] #, 
)
