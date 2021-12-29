import os
import configparser
import subprocess

HOME = os.environ['HOME']
RELATIVE_DIR = ".config/linux-undervolt.conf"

CONFIG_DIRECTORY = os.path.join(HOME, RELATIVE_DIR)

def checkConfigExists() -> bool:
    """
    Returns a boolean value for whether the config file has already been created.
    """
    
    exists = os.path.isfile(CONFIG_DIRECTORY)
    return exists


def createConfig(options=None, **kwargs) -> None:
    """Creates a configuration file for the program to store the profile and undervolt values.\n
    If no options are passed into this function, a default configuration file is generated and stored.
    """
    if options == None:
        options = makeDefaultConf(**kwargs)

    with open(CONFIG_DIRECTORY, 'w') as config_file:
        options.write(config_file)


def makeDefaultConf(**kwargs) -> configparser.ConfigParser:

    parser = configparser.ConfigParser()

    parser['SETTINGS'] = {
        "profile": 0,
        "undervolt-path": kwargs['undervolt_path']
    }

    profiles = [{i:0 for i in ['cpu', 'gpu', 'cpu_cache', 'sys_agent', 'analog_io']} for i in range(4)]

    for index, profile in enumerate(profiles):
        parser[str(index)] = profile

    return parser


### Read Config Functions
def getCurrentProfileSettings() -> tuple:

    parser = configparser.ConfigParser()
    parser.read(CONFIG_DIRECTORY)

    current_profile = parser['SETTINGS']['profile']
    profile_settings = getProfileSettings(current_profile, parser)

    return (int(current_profile), profile_settings)


def getProfileSettings(profile: str, parser=None) -> dict:
    "Return a dictionary of all settings for the given profile"
    if parser is None:
        parser = configparser.ConfigParser()
        parser.read(CONFIG_DIRECTORY)
    
    settings = parser[profile]
    settings = dict(settings)

    return settings


def getConfigDirectory(parser=None) -> str:

    if parser is None:
        parser = configparser.ConfigParser()
        parser.read(CONFIG_DIRECTORY)

    settings = parser['SETTINGS']

    return settings['undervolt-path']
    

### Change Config functions
def changeProfile(profile: str) -> None:
    "Change currently active profile to input profile"
    parser = configparser.ConfigParser()
    parser.read(CONFIG_DIRECTORY)

    parser.set("SETTINGS", "profile", profile)

    createConfig(parser)


def changeProfileSettings(profile: str, options: dict) -> None:

    parser = configparser.ConfigParser()
    parser.read(CONFIG_DIRECTORY)

    parser[profile] = options

    createConfig(parser)


def applyProfile() -> subprocess.CompletedProcess:

    profile_settings = getCurrentProfileSettings()[1]
    index_map = {'0': 'cpu', '1': 'gpu', '2': 'cpu_cache', '3': 'sys_agent', '4': 'analog_io'}
    config_path = getConfigDirectory()
    temp_file_location = os.environ['XDG_RUNTIME_DIR']
    temp_file = os.path.join(temp_file_location, 'intel-undervolt.conf')

    with open(config_path, 'r') as stream:

        argument_list = []
        for line in stream:
            
            if line[0] in ("#", "\n"):
                argument_list.append(line)
            else:

                arguments = line.split()

                if arguments[0] == 'undervolt':
                    index_val = arguments[1]
                    profile_opt = index_map[index_val]
                    setting = profile_settings[profile_opt]
                    arguments[-1] = setting
                else:
                    pass

                arguments = ' '.join(arguments)
                arguments = f'{arguments}\n'
                
                argument_list.append(arguments)

    with open(temp_file, 'w') as config:
        config.write(''.join(argument_list))

    config_folder = os.path.split(config_path)[0]

    command_1 = f"mv {temp_file} {config_folder}"
    command_2 = "intel-undervolt apply"

    final_command = f"pkexec sh -c '{command_1} ; {command_2}'"
    
    final_run = subprocess.run(final_command, shell=True, stdout=subprocess.DEVNULL)

    return final_run
        

