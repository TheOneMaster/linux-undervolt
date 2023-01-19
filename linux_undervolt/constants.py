import os

home = os.environ['HOME']
file_dir = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.join(home, ".config/linux-undervolt/")
CONFIG_FILE = os.path.join(CONFIG_DIR, "linux-undervolt.conf")

GLADE_FOLDER = os.path.join(file_dir, "glade_files/")
MAIN_WINDOW = os.path.join(GLADE_FOLDER, "GUI.glade")
ADVANCED_WINDOW = os.path.join(GLADE_FOLDER, "main_adv.glade")
