from setuptools import find_packages, setup

setup(
    name="ExcelCalendarAutomation",
    version="0.1.0",
    author="Unbo10",
    author_email="srochap@unal.edu.co",
    description="A project to automate calendar events from a list o tasks contained in Excel files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Unbo10/ExcelCalendarAutomation",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
        "openpyxl",
        "python-dotenv"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)