from setuptools import setup, find_packages

setup(
    name="fishtank.py",
    version="0.0.0",
    include_package_data=True,
    packages=["fishtank"],
    data_files=[("data", ["fishtank/data/species.json"])],
    license="MIT",
    description="An interactive fishtank for your terminal.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[],
    python_requires=">=3.9.0",
    url="https://github.com/bczsalba/fishtank.py",
    author="BcZsalba",
    author_email="bczsalba@gmail.com",
    entry_points={"console_scripts": ["fishtank = fishtank.main:cmdline"]},
)
