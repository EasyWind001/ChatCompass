"""
ChatCompass 安装脚本
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chatcompass",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI对话知识库管理系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ChatCompass",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PyQt6>=6.6.1",
        "playwright>=1.41.0",
        "beautifulsoup4>=4.12.3",
        "requests>=2.31.0",
        "openai>=1.10.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "chatcompass=main:main",
        ],
    },
)
