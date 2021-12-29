import os
import subprocess

HOME = os.environ['HOME']

def createUdevRule(options: dict) -> None:
    """
    Creaes a Udev rule for when the system is switched between battery and AC power.
    """
    # First we create the shell script to be called when the udev rule is triggered
    # temp_filedir = os.environ['XDG_RUNTIME_DIR']
    filedir = os.getcwd()
    filedir = os.path.join(filedir, "power-profile.sh")

    with open(filedir, 'w') as script_file:

        script_file.write("#!/bin/bash\n")
        export_variables = f"""
        HOME="{HOME}"
        XDG_RUNTIME_DIR="{os.environ['XDG_RUNTIME_DIR']}"

        export HOME
        export XDG_RUNTIME_DIR
        \n
        """
        script_file.write(export_variables)

        profile_change_python = os.getcwd()
        profile_change_python = os.path.join(profile_change_python, 'udev_change.py')

        script_file.write(f"""
        if on_ac_power
        then
            python3 {profile_change_python} --set-profile {options['ac']}
        else
            python3 {profile_change_python} --set-profile {options['bat']}
        fi
        """)

    # Next create the Udev rule

    temp_rule = os.path.join(os.environ['XDG_RUNTIME_DIR'], "linux-undervolt.temp")

    with open(temp_rule) as udev_rule:


        bat = f'ACTION=="change", SUBSYSTEM=="power_supply", RUN+="{filedir}"'
        udev_rule.write(bat)
    
    # Add custom udev rule to /etc/udev/rules.d

    custom_rule_folder = "/etc/udev/rules.d"
    custom_rule_file = os.path.join(custom_rule_folder, '100.linux-undervolt.rules')

    command = f"mv {temp_rule} {custom_rule_file}"

    command_run = subprocess.run(f"pkexec {command}")

    return command_run

    
