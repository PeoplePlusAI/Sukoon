from setuptools import setup, find_packages

# Read requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read README.md for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sukoon",
    version="3.0.0",
    author="Luv Singh",
    author_email="luv@peopleplus.ai",
    description="Mental Health Support using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luv-singh-ai/Sukoon",
    packages=find_packages(where="src", exclude=["tests*", "docs*"]),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Healthcare",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.2.5',
            'pytest-cov>=2.12.1',
            'black>=22.3.0',
            'flake8>=3.9.2',
            'mypy>=0.910',
        ],