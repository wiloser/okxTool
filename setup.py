from setuptools import setup, find_packages

setup(
    name="okx_tool",
    version="0.1.0",
    author="Your Name",
    author_email="your_email@example.com",
    description="A package for fetching OKX K-line data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mypackage",  # 替换为你的项目地址
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "tqdm",
    ],
)
