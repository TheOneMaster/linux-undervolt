# Linux Undervolt Tool

A fairly simple GTK tool built to mimic the basic functionality of ThrottleStop on Windows. Acts as a GUI so users are able to tell what they are doing without fiddling with the terminal.

Uses <a href="https://github.com/kitsunyan/intel-undervolt">intel-undervolt</a> to perform the undervolting, therefore it must be installed on the user's system. <a href="https://github.com/kitsunyan/intel-undervolt/blob/master/README.md">The guide to installing it can be found here</a>

To run this program, download the deb file from the latest <a href="https://github.com/TheOneMaster/linux-undervolt/releases/latest">release</a> and install it to the user's system. Once installed, it can be run either using the command line call `linux-undervolt` or finding the application in the application launcher (Currently it uses a placeholder icon from gnome).

Alternatively, follow the instruction to install the [Python GTK bindings](https://pygobject.readthedocs.io/en/latest/getting_started.html#ubuntu-logo-ubuntu-debian-logo-debian) for your distro. Then run the following commands
```
git clone https://github.com/TheOneMaster/linux-undervolt.git
cd linux-undervolt
python3 -m linux_undervolt
```

## GUI Instructions

Once changes have been made to a profile (by changing the slider values), the changes mst first be saved before applied. If not saved, the previous values present in the configuration file will be used. Thus, the program won't fail or throw an error message, but any change to the undervolt will not occur.

What the GUI currently looks like:


<img src="images/undervolt-tool_current.png"></img>

---

## Features
* Set Profile for AC/BAT
* 4 profiles to quickswitch between (only 1 in intel-undervolt)
* Import/Export settings
* Live System Power consumption readout (advanced mode)
### TODO:

* Add CPU info tab
* Add buttons for toggles in intel-undervolt (daemon mode, enable)
* Create power user settings toggle that enables more advanced features
