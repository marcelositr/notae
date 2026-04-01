from setuptools import setup, find_packages

setup(
    name="notae",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'notae=notae.main:main',
        ],
    },
    python_requires='>=3.6',
    author="Marcelo Trindade",
    description="An encrypted CLI personal journal for Linux",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
