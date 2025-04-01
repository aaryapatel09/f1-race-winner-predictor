from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="f1-predictor",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A machine learning application for predicting Formula 1 race outcomes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/f1-predictor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "f1-predictor=f1_predictor.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "f1_predictor": ["data/*", "models/*", "config/*"],
    },
    zip_safe=False,
) 