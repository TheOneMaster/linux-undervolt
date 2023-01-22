#!/usr/bin/env python3
import logging

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")
from gi.repository import Gtk, GObject
from gi.repository import Notify 

from .MainWindow import MainWindow
from .TerminalOutput import TerminalOutput
from .constants import ADVANCED_WINDOW, POWER_CONSUMPTION_SCRIPT, UNDERVOLT_READOUT_SCRIPT


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
        self.topLevelWindow.connect("destroy", self.on_quit)
        
        self.logger.debug("Finished setup for main window")
        
        
    def __initialSetup__(self) -> None:
        super().__initialSetup__()
        
        self._addTerminalOutput_()
    
        
    def _addTerminalOutput_(self):
        # 1st Tab
        box1 = self.builder.get_object("live-power-tab")
        term1 = TerminalOutput(box1)
        box1.add(term1)
        
        term1.run_command([POWER_CONSUMPTION_SCRIPT], True)
        self.logger.debug("Finished 1st tab setup")
        
        # 2nd Tab
        box2 = self.builder.get_object("current-undervolt-tab")
        term2 = TerminalOutput(box2)      
        box2.add(term2)
        
        term2.run_command([UNDERVOLT_READOUT_SCRIPT], True)
        self.logger.debug("Finished 2nd tab setup")
        
        self.terminals.append(term1)
        self.terminals.append(term2)
    
    def __termCommand__(self, term: TerminalOutput, command: str):
        term.run_command(command)
        return False

    def on_quit(self, _) -> None:
        for terminal in self.terminals:
            terminal.end_command()

if __name__ == "__main__":
    window = AdvancedWindow()
    window.topLevelWindow.show_all()
    Gtk.main()
