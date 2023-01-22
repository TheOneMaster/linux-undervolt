import os

HOME = os.environ['HOME']
FILE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.join(HOME, ".config/linux-undervolt/")
CONFIG_FILE = os.path.join(CONFIG_DIR, "linux-undervolt.conf")

GLADE_FOLDER = os.path.join(FILE_DIR, "glade_files/")
MAIN_WINDOW = os.path.join(GLADE_FOLDER, "GUI.glade")
ADVANCED_WINDOW = os.path.join(GLADE_FOLDER, "main_adv.glade")

SCRIPTS_FOLDER = os.path.join(FILE_DIR, "Scripts/")
POWER_CONSUMPTION_SCRIPT = os.path.join(SCRIPTS_FOLDER, "power-consumption")
UNDERVOLT_READOUT_SCRIPT = os.path.join(SCRIPTS_FOLDER, "undervolt-readout")
EXIT_TERMINAL_SCRIPT = os.path.join(SCRIPTS_FOLDER, "exit-terminal")
