#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .MainWindow import MainWindow
from .AdvancedWindow import AdvancedWindow
from .config import Config

if __name__ == "__main__":
    
    config = Config()
    
    window = None
    if config.getBool("advanced"):
        window = AdvancedWindow()
    else:
        window = MainWindow()
    
    window.topLevelWindow.show_all()
    Gtk.main()
