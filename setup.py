from setuptools import setup, find_packages

setup(
    name="cine-brain",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.12",
    install_requires=[
        "langchain-groq>=0.3.2",
        "langchain>=0.3.24",
        "pydantic>=2.11.3",
        "pydantic-settings>=2.9.1",
        "directory-tree>=1.0.0",
        "pytest>=8.3.5",
        "rich>=14.0.0",
        "crawl4ai>=0.6.3",
    ],
)
