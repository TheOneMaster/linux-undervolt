#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")
from gi.repository import Gtk, GObject
from gi.repository import Notify

import logging

from .MainWindow import MainWindow
from .TerminalOutput import TerminalOutput
from .constants import ADVANCED_WINDOW


class AdvancedWindow(MainWindow):
    
    def __init__(self, config):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.config = config
        self.builder = Gtk.Builder()
        
        self.builder.add_from_file(ADVANCED_WINDOW)        
        
        self.terminals: list[TerminalOutput] = []
        self.__initialSetup__()
        self.builder.connect_signals(self)
        
        self.topLevelWindow = self.builder.get_object("Main")
        self.destroy_signal = self.topLevelWindow.connect("destroy", Gtk.main_quit)
        self.logger.debug("Finished setup for main window")
        
        
    def __initialSetup__(self) -> None:
        super().__initialSetup__()
        
        self._addTerminalOutput_()
    
        
    def _addTerminalOutput_(self):
        # 1st Tab
        box1 = self.builder.get_object("live-power-tab")
        term1 = TerminalOutput(box1)
        box1.add(term1)
        
        # Run with delay so that the password prompt only shows up after the main GUI, and is focused
        GObject.timeout_add(1000, term1.runCommand, 'pkexec intel-undervolt measure')
        
        self.logger.debug("Finished 1st tab setup")
        
        # 2nd Tab
        box2 = self.builder.get_object("current-undervolt-tab")
        term2 = TerminalOutput(box2)
        term2.output.get_buffer().set_text(
            "Unable to add this until I understand PolKit or I'll be spammed with sudo requests."
            " If someone wants to work on this and help me out or pull request this functionality, that'd be great.")
        box2.add(term2)
        self.logger.debug("Finished 2nd tab setup")
        
        self.terminals.append(term1)
        self.terminals.append(term2)
    
    def __termCommand__(self, term: TerminalOutput, command: str):
        term.runCommand(command)
        return False

    def on_quit(self, action) -> None:
        for terminal in self.terminals:
            terminal.end_command()

if __name__ == "__main__":
    window = AdvancedWindow()
    window.topLevelWindow.show_all()
    Gtk.main()
