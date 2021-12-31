import os
import subprocess
from configparser import ConfigParser
import tempfile

HOME = os.environ['HOME']

def createUdevRule(options: dict) -> None:
    """
    Creates a Udev rule for when the system is switched between battery and AC power.
    """
    # First we create the systemd service to be called when the udev rule is triggered

    with tempfile.TemporaryDirectory() as tmp_dir:

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
                "EnvironmentFile": "/etc/systemd/system/linux-undervolt.powersave.env",
                "ExecStart": f"/usr/bin/python3 /opt/linux-undervolt/udev_change.py --set-profile {options['bat']}",
                "ExecStop": f"/usr/bin/python3 /opt/linux-undervolt/udev_change.py --set-profile {options['ac']}"
            }
            config['Install'] = {"WantedBy": "multi-user.target"}
            
            config.write(service_file, space_around_delimiters=False)

        # Add environment variables since the service will be run as root
        env_dir = os.path.join(tmp_dir, "temp.env")
        with open(env_dir, 'w') as env_file:
            env_file.write(f'HOME={HOME}\n')
            env_file.write(f"XDG_RUNTIME_DIR={os.environ['XDG_RUNTIME_DIR']}")

        # Next create the Udev rule
        temp_rule = os.path.join(tmp_dir, "linux-undervolt.temp")
        with open(temp_rule, 'w') as udev_rule:

            bat = f'ACTION=="change", SUBSYSTEM=="power_supply", ENV{{POWER_SUPPLY_ONLINE}}=="0", RUN+="/usr/bin/systemctl start linux-undervolt.powersave"'
            ac = f'ACTION=="change", SUBSYSTEM=="power_supply", ENV{{POWER_SUPPLY_ONLINE}}=="1", RUN+="/usr/bin/systemctl stop linux-undervolt.powersave"'
            udev_rule.write(bat)
            udev_rule.write("\n")
            udev_rule.write(ac)

        # Run the shell script to move and copy the files to their appropriate places
        script_file = os.path.join(os.getcwd(), 'powersave.sh')
        command_run = subprocess.run(f"pkexec sh -c 'chmod +x {script_file}; {script_file} {tmp_dir}; udevadm control --reload'", shell=True)
    
    return command_run
