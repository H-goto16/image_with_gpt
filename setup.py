from setuptools import setup, find_packages

VERSION = '1.0.0'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("LICENSE", "r", encoding="utf-8") as fh:
    license = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as req_file:
    requirements = req_file.read().splitlines()

setup(
    name='image_with_gpt',
    version=VERSION,
    author='Haruki Goto',
    author_email='h.goto.engineer@gmail.com',
    description='image and prompt to text.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=license,
    url='https://github.com/rionehome/image_with_gpt',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
