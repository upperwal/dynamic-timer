import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pravah-scrapper",
    version="0.0.5",
    author="Abhishek Upperwal",
    author_email="mesh@soket.in",
    description="Scrapping framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/upperwal",
    packages=setuptools.find_packages(),
    package_dir={'':'src'},
    py_modules=['pravah_scrapper'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'dytimer'
    ]
)