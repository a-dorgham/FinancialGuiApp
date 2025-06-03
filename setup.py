from setuptools import setup, find_packages

setup(
    name="financial_gui_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.14.0",
    ],
    entry_points={
        "console_scripts": [
            "financial_gui_app=src.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A PyQt6-based GUI for financial data visualization and strategy testing",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)