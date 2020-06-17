from setuptools import Extension, setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    author="Andriy Rossoshynskyy",
    author_email="andriy.rossoshynskyy@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    description="A lock-free, thread-safe queue using the C++ atomic library to synchronise memory access.",
    install_requires=["atomic-sequence"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="atomic-queue",
    packages=find_packages(),
    python_requires=">=3.6",
    url="https://github.com/arossoshynskyy/atomic-queue",
    setup_requires=["atomic-sequence"],
    version="0.0.1",
)
