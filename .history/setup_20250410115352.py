from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="catalyst-ot2-arduino",
    version="0.1.0",
    author="Sissi Feng",
    author_email="sissifeng@gmail.com",
    description="A modular automated experimental system for electrochemistry using OT-2 and Arduino",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sissifeng/catalyst-OT2-arduino",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "catalyst-test=scripts.test_connection:main",
        ],
    },
    include_package_data=True,
    package_data={
        "catalyst": [
            "config/*.json",
            "config/*.yaml",
        ],
    },
) 
