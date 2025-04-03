from setuptools import setup, find_packages

setup(
    name="f1-predictor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.12.0",
        "pandas",
        "numpy",
        "scikit-learn",
        "plotly",
        "altair==4.2.2",
        "joblib"
    ],
    author="Aarya Patel",
    author_email="aaryapatel09@gmail.com",
    description="F1 Race Winner Predictor using machine learning",
    keywords="f1, formula 1, racing, prediction, machine learning",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Sports Fans",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
) 