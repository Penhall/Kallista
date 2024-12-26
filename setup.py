from setuptools import setup, find_packages
import io

# Lê o README.md usando codificação UTF-8
with io.open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="kallista",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'crewai',
        'langchain',
        'openai',
        'python-dotenv',
        'aiohttp',
        'jinja2',
        'networkx',
        'pandas',
        'numpy',
        'keyring',
        'cryptography',
        'pyyaml',
        'semver'
    ],
    author="Reginaldo Santos",
    author_email="Penhall@gmail.com",
    description="Sistema integrado de gerenciamento de código com suporte a WPF e C#",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/kallista",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'kallista=kallista.main:main',
        ],
    },
)