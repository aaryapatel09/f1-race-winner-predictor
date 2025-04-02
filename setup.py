from setuptools import setup, find_packages

setup(
    name="f1-predictor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "requests>=2.26.0",
        "streamlit>=1.15.0",
        "plotly>=5.3.0",
        "python-dotenv>=0.19.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "boto3>=1.26.0",  # AWS SDK
        "google-cloud-storage>=2.0.0",  # GCP Storage
        "prometheus-client>=0.12.0",  # Monitoring
        "python-json-logger>=2.0.0",  # Logging
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "f1-predictor=src.main:main",
        ],
    },
) 