#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")
from gi.repository import Gtk, Gdk, GObject
from gi.repository import Notify

from .MainWindow import MainWindow
from .terminal import TerminalOutput
from . import config
from .constants import ADVANCED_WINDOW


class AdvancedWindow(MainWindow):
    
    def __init__(self):
        self.config = config.Config()
        self.builder = Gtk.Builder()
        
        self.builder.add_from_file(ADVANCED_WINDOW)
        self.builder.connect_signals(self)
        
        self.__initialSetup__()
        
        self.topLevelWindow = self.builder.get_object("Main")
        self.destroy_signal = self.topLevelWindow.connect("delete-event", Gtk.main_quit)
        
        
    def __initialSetup__(self) -> None:
        super().__initialSetup__()
        
        self._addTerminalOutput_()
    
        
    def _addTerminalOutput_(self):
        # 1st Tab
        box1 = self.builder.get_object("live-power-tab")
        term1 = TerminalOutput(box1)
        box1.pack_start(term1, True, True, 0)
        GObject.timeout_add(1000, lambda: self.__termCommand__(term1, "pkexec intel-undervolt measure"))
        
        # 2nd Tab
        box2 = self.builder.get_object("current-undervolt-tab")
        term2 = TerminalOutput(box2)
        term2.output.get_buffer().set_text("Unable to add this until I understand PolKit or I I'll be spammed with sudo requests.")
        box2.pack_start(term2, True, True, 0)
    
    def __termCommand__(self, term: TerminalOutput, command: str):
        term.runCommand(command)
        return False

if __name__ == "__main__":
    window = AdvancedWindow()
    window.topLevelWindow.show_all()
    Gtk.main()
