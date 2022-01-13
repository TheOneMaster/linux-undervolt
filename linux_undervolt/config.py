import os
import configparser
import subprocess
import tempfile

HOME = os.environ['HOME']
CONFIG_DIRECTORY = os.path.join(HOME, '.config/linux-undervolt.conf')


class Config:

    def __init__(self, configFile=CONFIG_DIRECTORY):
        """
        docstring
        """

        # Define instance variables
        self.parser = configparser.ConfigParser()
        self.undervolt_file = None
        self.active_profile = None

        if os.path.isfile(configFile):
            self.parser.read(configFile)
        else:
            self.createConfig()
            self.saveChanges()

        self.undervolt_file = self.parser['SETTINGS']['undervolt_path']
        self.active_profile = self.parser['SETTINGS']['profile']

    def createConfig(self) -> None:
        """
        Creates the configuration file for the application. Stores the general settings as well as profile-specific
        information.
        """

        self.parser['SETTINGS'] = {
            'profile': 0,
            'undervolt_path': "/etc/intel-undervolt.conf",
            'battery_switch': 'false',
            'battery_profile': "",
            'ac_profile': ""
        }

        profile_options = ['cpu', 'gpu', 'cpu_cache', 'sys_agent', 'analog_io']

        profiles = [{i: 0 for i in profile_options} for j in range(4)]

        # Create default undervolt values for each profile in config file
        for index, profile in enumerate(profiles):
            self.parser[str(index)] = profile

    #################################
    # Settings and Profiles methods #
    #################################

    def getSettings(self, setting=None) -> dict:

        settings = self.parser['SETTINGS']
        settings = dict(settings)

        if setting:
            settings = settings[setting]

        return settings

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

    def changeSettings(self, setting: str or dict, new_value=None) -> None:
        """
        Change one or more of the general settings of the config file.

        Arguments:
        setting (either str or dict) - Either a dictionary of key:value pairs for settings to be changed
                                       or a string denoting a single setting
        new_value (str) - When a single setting is to be changed, provide the new value into this argument
        """
        if isinstance(setting, str):
            self.parser['SETTINGS'][setting] = new_value

        elif isinstance(setting, dict):
            for key, value in setting.items():
                self.parser['SETTINGS'][key] = value

        else:
            raise TypeError

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

    ########################
    # Save & Apply changes #
    ########################

    def exportConfig(self, output):

        with open(output, 'w') as export_file:
            self.parser.write(export_file)

    def saveChanges(self) -> None:
        """
        Save the profile settings to the config file.
        """
        with open(CONFIG_DIRECTORY, 'w') as config_file:
            self.parser.write(config_file)

    def applyChanges(self) -> subprocess.CompletedProcess:
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
            undervolt_file = os.path.join(undervolt_folder, 'intel-undervolt.conf')

            command_1 = f"mv {temp_undervolt_file_dir} {undervolt_file}"
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


def main():
    """
    Command line interface to change some settings. Should not be called from GUI.
    """

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-set-profile")

    args = vars(parser.parse_args())
    new_profile = args['set_profile']

    if new_profile:
        temp_config = Config(created=True)
        temp_config.changeSettings('profile', new_profile)
        temp_config.applyChanges()
        


if __name__ == "__main__":
    main()
