# Copyright (C) <2018-2022>  <Agence Data Services, DSI Pôle Emploi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from setuptools import setup, find_packages

# Get package directory
package_directory = os.path.dirname(os.path.abspath(__file__))

# Get package version (env variable or version file + +local)
version_path = os.path.join(package_directory, 'version.txt')
with open(version_path, 'r') as version_file:
    version = version_file.read().strip()
version = os.getenv('VERSION') or f"{version}+local"

# Get package description
readme_path = os.path.join(package_directory, 'README.md')
with open(readme_path, 'r') as readme_file:
    long_description = readme_file.read()

# Setup
setup(
    name="{{package_name}}",
    version=version,
    packages=find_packages(include=["{{package_name}}*"]),
    license='AGPL-3.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="",
    author_email="",
    description="Generated using Gabarit",
    url="",
    platforms=['windows', 'linux'],
    python_requires='>=3.8',
    include_package_data=True,
    package_data={'': ['{{package_name}}/configs/**']},
    install_requires=[
        'pandas>=1.4.4',
        'numpy>=1.19',
        'scikit_learn>=1.3',
        'lightgbm>=2.3.0',
        'words-n-fun>=1.6.0',
        'nltk>=3.8',
        'matplotlib>=3.0.3',
        'seaborn>=0.9.0',
        'dill>=0.3.2',
        'protobuf>=3.9.2',
        'mlflow>=2.7',
    ],
    extras_require={
        "tensorflow": ["tensorflow>=2.13.1"],
        "torch": ["torch>=2.0", "transformers>=4.23.0", "sentencepiece>=0.1.93", "accelerate>=0.23.0"],
        "explicability": ['lime>=0.2'],
    }
    # pip install {{package_name}} || pip install {{package_name}}[tensorflow] || etc.
)
