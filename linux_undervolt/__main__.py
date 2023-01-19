#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .MainWindow import MainWindow
from .AdvancedWindow import AdvancedWindow
from .config import Config, configExists
from .backend import createBackup

def main() -> None:
    window = None
    if not configExists():
        window = MainWindow(True)
    else:
        advanced = Config().getBool("advanced")
        window = AdvancedWindow() if advanced else MainWindow()
        
    try:
        window.topLevelWindow.show_all()
    except RuntimeError:
        pass
    
    Gtk.main()

if __name__ == "__main__":
    main()
