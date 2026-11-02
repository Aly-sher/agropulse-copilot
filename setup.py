"""Setup script for agropulse-copilot."""

from setuptools import find_packages, setup

setup(
    name="agropulse-copilot",
    version="1.0.0",
    description="Enterprise Hyper-Local Smallholder Crop & Irrigation Copilot",
    # Explicitly tell setuptools that all Python code lives inside the 'backend' folder
    package_dir={"": "backend"},
    # Explicitly find packages ONLY within the 'backend' folder
    packages=find_packages(where="backend"),
)
