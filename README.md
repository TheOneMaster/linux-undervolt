# Linux Undervolt Tool

A fairly simple GTK tool built to mimic the basic functionality of ThrottleStop on Windows. Acts as a GUI so users are able to tell what they are doing without fiddling with the terminal.

Uses <a href="https://github.com/kitsunyan/intel-undervolt">intel-undervolt</a> to perform the undervolting, therefore it must be installed on the user's system. <a href="https://github.com/kitsunyan/intel-undervolt/blob/master/README.md">The guide to installing it can be found here</a>

To run this program, download the deb file from the latest <a href="https://github.com/TheOneMaster/linux-undervolt/releases/latest">release</a> and install it to the user's system. Once installed, it can be run either using the command line call `linux_undervolt` or finding the application in the application launcher (Currently it uses a placeholder icon from gnome).

## GUI Instructions

Once changes have been made to a profile (by changing the slider values), the changes mst first be saved before applied. If not saved, the previous values present in the configuration file will be used. Thus, the program won't fail or throw an error message, but any change to the undervolt will not occur.

What the GUI currently looks like:


<img src="images/undervolt-tool_current.png"></img>

### TODO:

* Add CPU info tab
* Add import/export functionality for config file
* Add buttons for toggles in intel-undervolt (daemon mode, enable)
* Create Backup of original intel-undervolt config file for easy reset to default
* Create power user settings toggle that enables more advanced features
* Add tab for live cpu W/h readings
