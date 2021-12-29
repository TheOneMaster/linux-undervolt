from setuptools import setup
from linux_undervolt import __version__

setup(
    name="Linux Undervolt",
    version=__version__,
    author="Nayan Nair",
    author_email="nayannair@yahoo.com",
    description="GTK UI for Undervolting Intel CPUs",
    url="https://github.com/TheOneMaster/linux-undervolt",
    license="GPLv2",
    packages=["linux_undervolt"],
    entry_points={
        'gui_scripts': [
            'linux_undervolt = linux_undervolt.main:main'
        ]
    },
    install_requires=[
        'gi >= 3.0'
    ],
    python_requires=">=3"
)
