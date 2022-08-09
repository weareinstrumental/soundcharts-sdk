from setuptools import setup, find_packages

setup(
    name="soundcharts-sdk",
    version="1.18.0",
    description="SDK for Soundcharts API",
    author="Simon Christian",
    author_email="simon.christian@weareinstrumental.com",
    url="https://github.com/weareinstrumental/soundcharts-sdk",
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[],
)
