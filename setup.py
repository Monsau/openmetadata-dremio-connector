"""
Setup script for Dremio Connector
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="dremio-openmetadata-connector",
    version="1.0.0",
    author="Dremio OpenMetadata Team",
    author_email="contact@example.com",
    description="Custom connector for ingesting Dremio metadata into OpenMetadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dremio-connector",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/dremio-connector/issues",
        "Documentation": "https://github.com/yourusername/dremio-connector/wiki",
        "Source Code": "https://github.com/yourusername/dremio-connector",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.32.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0.1",
        "urllib3>=2.0.0",
        "certifi>=2025.1.0",
        "jsonschema>=4.19.0",
        "pyarrow>=14.0.0",
        "typing-extensions>=4.7.0",
        "pandas>=2.2.0",
        "prettytable>=3.14.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "database": [
            "psycopg2-binary>=2.9.7",
        ],
        "search": [
            "opensearch-py>=2.4.0",
            "elasticsearch>=8.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dremio-connector=dremio_connector.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
