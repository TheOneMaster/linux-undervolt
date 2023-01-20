#!/usr/bin/env python3
import os
import configparser
import subprocess
import tempfile
import pathlib
import logging

from .constants import CONFIG_DIR, CONFIG_FILE

class Config:
    
    __slots__ = ("_parser", "undervolt_file", "logger")

    def __init__(self, configFile=CONFIG_FILE):
        """
        docstring
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._parser = configparser.ConfigParser()
        self._parser.read(configFile)
        self.undervolt_file = self._parser['SETTINGS']['undervolt_path']
        
    @classmethod
    def create_config(cls) -> 'Config':
        parser = configparser.ConfigParser()
        
        parser['SETTINGS'] = {
            'profile': 0,
            'undervolt_path': "/etc/intel-undervolt.conf",
            'battery_switch': 'false',
            'battery_profile': "",
            'ac_profile': "",
            'startup': 0,
            "advanced": 0
        }

        profile_options = ['cpu', 'gpu', 'cpu_cache', 'sys_agent', 'analog_io']
        profiles = [{i: 0 for i in profile_options} for j in range(4)]

        # Create default undervolt values for each profile in config file
        for index, profile in enumerate(profiles):
            parser[str(index)] = profile
            
        # Save file
        pathlib.Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as config_out:
            parser.write(config_out)
        
        return cls()

    #################################
    # Settings and Profiles methods #
    #################################

    def getSettings(self, setting=None) -> dict:

        settings = self._parser['SETTINGS']
        settings = dict(settings)

        if setting:
            settings = settings[setting]

        return settings

    def getBool(self, setting) -> bool:
        return self._parser.getboolean('SETTINGS', setting)

    def getActiveProfile(self) -> int:
        active_profile = self._parser['SETTINGS']['profile']
        return int(active_profile)

    def getProfileSettings(self, profile_number=None) -> dict:
        """
        Return a dictionary of the various profile settings for the selected profile. If no profile is provided,
        the function defaults to the currently active profile.
        """

        if profile_number is None:
            profile_number = self._parser['SETTINGS']['profile']

        settings = self._parser[profile_number]
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
            self._parser['SETTINGS'][setting] = new_value

        elif isinstance(setting, dict):
            for key, value in setting.items():
                self._parser['SETTINGS'][key] = value

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
            profile = self._parser['SETTINGS']['profile']

        self._parser[profile] = settings

        self.saveChanges()

    ########################
    # Save & Apply changes #
    ########################

    def exportConfig(self, output):

        with open(output, 'w') as export_file:
            self._parser.write(export_file)

    def saveChanges(self) -> None:
        """
        Save the profile settings to the config file.
        """
        with open(CONFIG_FILE, 'w') as config_file:
            self._parser.write(config_file)

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

            final_run = subprocess.run(final_command, shell=True)

        return final_run




def configExists() -> bool:
    return os.path.isfile(CONFIG_FILE)
        



def checkPrerequisites() -> bool:
    """
    Checks if the system has the prerequisite software (intel-undervolt) installed.
    """

    intel_undervolt = subprocess.run("command -v intel-undervolt", shell=True, stdout=subprocess.DEVNULL)
    check = bool(intel_undervolt)

    return check


def cli():
    """
    Command line interface to change some settings. Should not be called from GUI.
    """

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-set-profile")

    args = vars(parser.parse_args())
    new_profile = args['set_profile']

    if new_profile:
        temp_config = Config()
        temp_config.changeSettings('profile', new_profile)
        temp_config.applyChanges()
        


if __name__ == "__main__":
    cli()
