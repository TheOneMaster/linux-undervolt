import os

home = os.environ['HOME']
file_dir = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.join(home, ".config/linux_undervolt/")
CONFIG_FILE = os.path.join(CONFIG_DIR, "linux-undervolt.conf")

MAIN_WINDOW = os.path.join(file_dir, "GUI.glade")
ADVANCED_WINDOW = os.path.join(file_dir, "main_adv.glade")
