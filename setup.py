from setuptools import setup, find_packages

print("packages: " + str(find_packages()))

setup(
    name="pocket_ic",
    version="0.0.0",
    author="DFINITY",
    description="A caniste testing platform",
    url="https://github.com/dfinity/pocketic-py",
    python_requires=">=3.7, <4",
    packages=find_packages(),
)
