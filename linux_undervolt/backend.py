import os
import subprocess
from configparser import ConfigParser
import tempfile

HOME = os.environ['HOME']

def createUdevRule(options: dict) -> None:
    """
    Creates a toggle for the power profiles that is automatically called when the power source is changed between battery
    and AC power.
    """

    bat_profile = options.get('bat', False)
    ac_profile = options.get('ac', False)

    # The files are first going to be created in a temporary directory, then moved to the correct location, and then
    # deleted from the filesystem.
    with tempfile.TemporaryDirectory() as tmp_dir:

        # First create the systemd service responsible for the switch of profiles
        filedir = os.path.join(tmp_dir, "temp.service")
        with open(filedir, 'w') as service_file:
    
            config = ConfigParser()
            
            # The default optionxform function converts keys to lowercase when writing. This skips that step.
            config.optionxform = str

            config["Unit"] = {
                "Description": "Toggle Power Profiles on Power change"
            }
            config['Service'] = {
                "Type": "oneshot",
                "RemainAfterExit": "yes",
                "EnvironmentFile": "/etc/systemd/system/linux-undervolt.powersave.env"
            }

            if bat_profile:
                config['Service']['ExecStart'] = f"/usr/bin/python3 /opt/linux-undervolt/config.py -set-profile {bat_profile}"
            if ac_profile:
                config['Service']['ExecStop'] = f"/usr/bin/python3 /opt/linux-undervolt/config.py -set-profile {ac_profile}"


            config['Install'] = {"WantedBy": "multi-user.target"}
            
            config.write(service_file, space_around_delimiters=False)

        # Add environment variables since the service will be run as root
        env_dir = os.path.join(tmp_dir, "temp.env")
        with open(env_dir, 'w') as env_file:
            env_file.write(f'HOME={HOME}\n')

        # Next create the Udev rule to trigger the service on power source change
        temp_rule = os.path.join(tmp_dir, "linux-undervolt.temp")
        with open(temp_rule, 'w') as udev_rule:

            bat = f'ACTION=="change", SUBSYSTEM=="power_supply", ENV{{POWER_SUPPLY_ONLINE}}=="0", RUN+="/usr/bin/systemctl start linux-undervolt.powersave"'
            ac = f'ACTION=="change", SUBSYSTEM=="power_supply", ENV{{POWER_SUPPLY_ONLINE}}=="1", RUN+="/usr/bin/systemctl stop linux-undervolt.powersave"'

            if bat_profile:
                udev_rule.write(bat)
            if ac_profile:
                udev_rule.write("\n")
                udev_rule.write(ac)

        # Run the shell script to move and copy the files to their appropriate places
        script_file = os.path.join(os.getcwd(), 'powersave.sh')

        command_1 = f'chmod +x {script_file}'   # Make the shell script executable
        command_2 = f'{script_file} {tmp_dir}'  # Execute shell script
        command_3 = 'systemctl daemon-reload'   # Reload systemd daemon (for service to be recognised)
        command_4 = 'udevadm control --reload'  # Reload udev rules

        command_run = subprocess.run(f"pkexec sh -c '{command_1}; {command_2}; {command_3}; {command_4}'", shell=True)
    
    return command_run

def removeUdevRule() -> int:

    udev_rule = "/etc/udev/rules.d/100.linux-undervolt.rules"
    systemd_service_dir = "/etc/systemd/system/"

    if os.path.isfile(udev_rule):
        systemd_service = os.path.join(systemd_service_dir, 'linux-undervolt.powersave.service')
        systemd_env = os.path.join(systemd_service_dir, 'linux-undervolt.powersave.env')

        command = f"pkexec rm -f {udev_rule} {systemd_service} {systemd_env}"
        run = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
        return run.returncode

    else:
        return 0
