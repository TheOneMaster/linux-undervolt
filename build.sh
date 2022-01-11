#!/bin/bash
# Build the deb file
python3 setup.py --command-packages=stdeb.command bdist_deb

# Copy deb file to another folder
cp ./deb_dist/*.deb ./builds

# Delete files created by stdeb for the build
sudo rm -f -r ./deb_dist ./dist ./linux_undervolt_tool.egg-info ./*.tar.gz
