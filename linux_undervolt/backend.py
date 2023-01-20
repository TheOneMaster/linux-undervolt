import os
import subprocess
import tempfile
import zipfile

from configparser import ConfigParser

from .config import CONFIG_DIR
from .constants import HOME, FILE_DIR

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
        script_file = os.path.join(FILE_DIR, 'powersave.sh')

        command_1 = f'chmod +x {script_file}'   # Make the shell script executable
        command_2 = f'{script_file} {tmp_dir}'  # Execute shell script

        command_run = subprocess.run(f"pkexec sh -c '{command_1}; {command_2}'", shell=True)
    
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

def createBackup() -> None:

    undervolt_file = '/etc/intel-undervolt.conf'

    zip_file = os.path.join(CONFIG_DIR, 'intel-undervolt.bak.zip')
    with zipfile.ZipFile(zip_file, 'w') as backup_archive:
        backup_archive.write(undervolt_file, 'intel-undervolt.conf')

def startupChange(value: int) -> None:
    """
    Set the startup behaviour for the undervolt. If on, the undervolt is applied on boot.
    Should only be called after the undervolt settings have been tested by the user.
    """
    key = {
        0: "stop",
        1: "start"
    }

    command = f"pkexec systemctl {key[value]} intel-undervolt"
    run = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
    return run.returncode
