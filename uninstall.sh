#!/bin/bash

# Remove the Udev rule from the system if it was created. 
python3 -c "from linux_undervolt import backend; backend.removeUdevRule()"
