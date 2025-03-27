from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

APP_NAME = 'PyThermoLinkDB'
AUTHUR = 'Sina Gilassi'
EMAIL = "<sina.gilassi@gmail.com>"
VERSION = '1.1.0'
DESCRIPTION = 'PyThermoLinkDB is a Python package providing a robust and efficient interface between `PyThermoDB` and other applications.'
LONG_DESCRIPTION = "PyThermoLinkDB is a Python package providing a robust and efficient interface between `PyThermoDB` and other applications. It enables seamless thermodynamic data exchange, integration, and analysis. With PyThermoLinkDB, developers can easily link PyThermoDB to various tools, frameworks, and databases, streamlining thermodynamic workflows."

# Setting up
setup(
    name=APP_NAME,
    version=VERSION,
    author=AUTHUR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    include_package_data=True,  # Make sure to include non-Python files
    # Add both config and data files
    package_data={'': ['config/*.yml', 'data/*.csv']},
    license='MIT',
    license_files=['LICENSE'],
    install_requires=['pandas', 'pillow', 'requests',
                      'urllib3', 'matplotlib', 'numpy', 'PyYAML', 'PyThermoDB'],
    keywords=['python', 'chemical engineering', 'thermodynamics',
              'PyThermoDB'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.10',
)
