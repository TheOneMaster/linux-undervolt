import os
import configparser
import subprocess
import tempfile

HOME = os.environ['HOME']
CONFIG_DIRECTORY = os.path.join(HOME, '.config/linux-undervolt.conf')

class Config:

    def __init__(self, created=False, undervolt_file=None):
        """
        docstring
        """

        # Define instance variables
        self.parser = configparser.ConfigParser()
        self.undervolt_file = None
        self.active_profile = None

        if created:
            self.parser.read(CONFIG_DIRECTORY)
        else:
            self.createConfig(general_options={'undervolt_file': undervolt_file})
            self.saveChanges()

        self.undervolt_file = self.parser['SETTINGS']['undervolt_path']
        self.active_profile = self.parser['SETTINGS']['profile']


    def createConfig(self, exists=False, general_options=None) -> None:
        """
        Creates the configuration file for the application. Stores the general settings as well as profile-specific
        information.
        """

        if not exists:
            
            undervolt_path = general_options.get("undervolt_path", "/etc/intel-undervolt.conf")
            battery_switch = general_options.get("bat_switch", False)
            battery_profile = general_options.get("bat_profile", "")
            ac_profile = general_options.get("ac_profile", "")

            self.parser['SETTINGS'] = {
                'profile': 0,
                'undervolt_path': undervolt_path,
                'battery_switch': battery_switch,
                'battery_profile': battery_profile,
                'ac_profile': ac_profile
            }

        profile_options = ['cpu', 'gpu', 'cpu_cache', 'sys_agent', 'analog_io']

        profiles = [{i:0 for i in profile_options} for j in range(4)]

        for index, profile in enumerate(profiles):
            self.parser[str(index)] = profile

    ################################# 
    # Settings and Profiles methods # 
    #################################

    def getProfileSettings(self, profile_number=None) -> dict:
        """
        Return a dictionary of the various profile settings for the selected profile. If no profile is provided,
        the function defaults to the currently active profile.
        """

        if profile_number is None:
            profile_number = self.parser['SETTINGS']['profile']

        settings = self.parser[profile_number]
        settings = dict(settings)

        return settings

    def changeSettings(self, setting: str, new_value: str) -> None:

        self.parser['SETTINGS'][setting] = new_value

    def changeProfile(self, profile_number: str) -> None:
        """
        Change the active profile of the tool.
        """
        self.parser['SETTINGS']['profile'] = profile_number
        self.saveChanges()

    def changeProfileSettings(self, settings: dict, profile=None) -> None:
        """
        Change the undervolt settings for a profile.

        Arguments:
        settings              - A dictionary containing the various settings values
        profile(default None) - A string containing the profile number for the settings to be applied to.
                                If no value is provided, defaults to the active profile. 
        """
        if profile is None:
            profile = self.parser['SETTINGS']['profile']

        self.parser[profile] = settings

        self.saveChanges()

    def saveChanges(self) -> None:
        """
        Save the profile settings to the config file.
        """
        with open(CONFIG_DIRECTORY, 'w') as config_file:
            self.parser.write(config_file)

    def applyChanges(self) -> None:
        """
        Copy the active profile settings to the undervolt file and apply the undervolt to the system.
        """
        
        index_map = {
            '0': 'cpu',
            '1': 'gpu',
            '2': 'cpu_cache',
            '3': 'sys_agent',
            '4': 'analog_io'
        }

        profile_settings = self.getProfileSettings()

        # Create the undervolt file in a temporary directory and then move it to the correct location.
        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a list of each line of the undervolt file. For the undervolt lines, overwrite the present values
            # with the new profile values.
            line_list = []
            with open(self.undervolt_file) as stream:
                for line in stream:
                    
                    if line[0] in ('#', '\n'):
                        line_list.append(line)
                    else:

                        arguments = line.split()

                        if arguments[0] == 'undervolt':
                            index_val = arguments[1]
                            current_option = index_map[index_val]
                            setting = profile_settings[current_option]
                            arguments[-1] = setting
                        
                        arguments = ' '.join(arguments)
                        arguments = f'{arguments}\n'

                        line_list.append(arguments)

            temp_undervolt_file_dir = os.path.join(temp_dir, 'temp-undervolt.conf')
            
            # Write the lines to a new temp file
            with open(temp_undervolt_file_dir, 'w') as tmp_undervolt:
                total_string = ''.join(line_list)
                tmp_undervolt.write(total_string)

            undervolt_folder = os.path.split(self.undervolt_file)[0]

            command_1 = f"mv {temp_undervolt_file_dir} {undervolt_folder}"
            command_2 = "intel-undervolt apply"

            # Move the undervolt file to the correct place and apply the undervolt. Requires root priviliges.
            final_command = f"pkexec sh -c '{command_1} ; {command_2}'"
            
            final_run = subprocess.run(final_command, shell=True, stdout=subprocess.DEVNULL)

        
        return final_run



def checkPrerequisites() -> bool:
    """
    Checks if the system has the prerequisite software (intel-undervolt) installed.
    """

    intel_undervolt = subprocess.run("command -v intel-undervolt", shell=True, stdout=subprocess.DEVNULL)
    check = bool(intel_undervolt)

    return check
