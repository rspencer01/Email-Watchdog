"""Setup for nimbus."""

from setuptools import setup

setup(
    name="nimbus",
    description="",
    version="0.0.1dev",
    author="R. A. Spencer",
    author_email="general@robertandrewspencer.com",
    packages=["nimbus"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
    ],
    entry_points='''
        [console_scripts]
        nimbus-travel=nimbus.cli:travel
        nimbus-notifications=nimbus.cli:notifications
        nimbus-time=nimbus.cli:timesheet
    ''',
    python_requires=">=3.5",
    install_requires=[
        "gpxpy==1.3.5",
        "pandas==0.25.3",
        "traces==0.5.2",
        "sklearn==0.0",
        "click"
    ],
)
