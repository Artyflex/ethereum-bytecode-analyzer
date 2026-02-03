from setuptools import setup, find_packages

setup(
    name="ethereum-bytecode-analyzer",
    version="0.1.0",
    description="EVM Bytecode Analyzer - Parse and analyze Ethereum smart contract bytecode",
    author="Artyflex",
    author_email="",
    url="https://github.com/Artyflex/ethereum-bytecode-analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "eth-hash>=0.5.0",
        "hexbytes>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "bytecode-analyzer=bytecode_analyzer.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: GNU General Public License v3.0",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
)