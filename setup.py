from pathlib import Path
from typing import Generator

from setuptools import find_packages, setup


def parse_requirements(filename: str) -> Generator[str, None]:
    lines = (line.strip() for line in Path(filename).read_text().split('\n'))
    return (line for line in lines if line)


def get_requirements(filename: str) -> Generator[str, None]:
    return (requirement for requirement in parse_requirements(filename))


setup(
    name='name-is-coming',
    packages=find_packages(include=('name_is_coming', 'name_is_coming.*')),
    python_requires='>=3.9',
    install_requires=get_requirements('requirements.txt'),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': (
            'poller=name_is_coming.poller.__main__:entrypoint',
        ),
    },
)
