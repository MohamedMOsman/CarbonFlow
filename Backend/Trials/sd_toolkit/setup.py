"""
Setup script for the High-Resolution Spatiotemporal System Dynamics Toolkit.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sd-toolkit",
    version="0.1.0",
    author="System Dynamics Toolkit Team",
    author_email="contact@sd-toolkit.org",
    description="A Python-based software toolkit for system dynamics modeling with multi-dimensional, unit-aware data structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/sd-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "interactive": [
            "plotly>=5.0.0",
            "bokeh>=2.4.0",
            "ipywidgets>=7.6.0",
        ],
        "spatial": [
            "geopandas>=0.10.0",
            "rasterio>=1.2.0",
            "shapely>=1.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "sd-toolkit=sd_toolkit.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sd_toolkit": [
            "data/*.json",
            "data/*.csv",
        ],
    },
    keywords="system dynamics, modeling, simulation, climate, spatiotemporal, units",
    project_urls={
        "Bug Reports": "https://github.com/your-org/sd-toolkit/issues",
        "Source": "https://github.com/your-org/sd-toolkit",
        "Documentation": "https://sd-toolkit.readthedocs.io/",
    },
)
