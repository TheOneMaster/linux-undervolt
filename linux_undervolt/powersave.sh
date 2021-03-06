#!/bin/bash

# Move temp service to Systemd services
mv "${1}/temp.service" "/etc/systemd/system/linux-undervolt.powersave.service"
mv "${1}/temp.env" "/etc/systemd/system/linux-undervolt.powersave.env"

# Move temp rule to Udev rules
mv "${1}/linux-undervolt.temp" "/etc/udev/rules.d/100.linux-undervolt.rules"

# Reload systemd and udev services
systemctl daemon-reload
udevadm control --reload
