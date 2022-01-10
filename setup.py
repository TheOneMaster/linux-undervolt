from setuptools import setup
import linux_undervolt

setup(
    name = "linux_undervolt-tool",
    version = linux_undervolt.__version__,
    author = "TheOneMaster",
    author_email = "tmp@gmail.com",
    description = "GUI Frontend for intel-undervolt",
    license="GPLv2",
    url="https://github.com/TheOneMaster/linux_undervolt",
    packages=['linux_undervolt'],
    include_package_data=True,
    entry_points={
        'gui_scripts': ["linux_undervolt = linux_undervolt.main:main"]
    },
    data_files=[
        ('share/applications/', ['theonemaster-linux_undervolt.desktop'])
    ],
    classifiers=[
        "License :: OSI Approved :: GPLv2 License"
    ]
)
