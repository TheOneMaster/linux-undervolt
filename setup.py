from setuptools import setup
import linux_undervolt

def readme() -> str:
    with open("README.md", 'r') as f:
        return f.read()


setup(
    name = "linux-undervolt-tool",
    version = linux_undervolt.__version__,
    author = "TheOneMaster",
    author_email = "tmp@gmail.com",
    description = "GUI Frontend for intel-undervolt",
    long_description=readme(),
    long_description_content_type="text/markdown",
    license="GPLv2",
    url="https://github.com/TheOneMaster/linux-undervolt",
    packages=['linux_undervolt'],
    include_package_data=True,
    entry_points={
        'gui_scripts': ["linux-undervolt = linux_undervolt.__main__:main"],
        'console_scripts': ["linux-undervolt = linux_undervolt.config:cli"]
    },
    data_files=[
        ('share/applications/', ['theonemaster-linux_undervolt.desktop']),
        ('/opt/linux-undervolt', ['linux_undervolt/config.py']),
        ('share/polkit-1/actions/', ['linux_undervolt/misc/org.theonemaster.linux-undervolt.policy'])
    ],
    classifiers=[
        "License :: OSI Approved :: GPLv2 License"
    ]
)
