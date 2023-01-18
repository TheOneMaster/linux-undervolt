from typing import Optional, List

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GObject, Gdk

import logging
import os
import subprocess
import fcntl

class TerminalOutput(Gtk.ScrolledWindow):
    
    def __init__(self, parent, *args,):
        super().__init__(*args)
        
        # self.resize(100, 500)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.__parent = parent
        self.__lastCommand = None
        
        self.output = Gtk.TextView()
        
        # TextView attributes
        self.output.set_monospace(True)
        self.output.set_editable(False)
        self.output.set_cursor_visible(False)
        self.output.set_wrap_mode(Gtk.WrapMode.WORD)
        # self.output.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("black"))
        
        # Scroll attributes
        self.set_vexpand(True)
        self.set_hexpand(True)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        
        self.add_with_viewport(self.output)
        self.logger.info("Finished setup for Terminal Output")
        # self.output.get_buffer().set_text("Testing")
        
    def runCommand(self, command: str, args: Optional[List[str]]=None):
        self.logger.info(f"Running command: {command} {args}")
        if args is None:
            args = []
        
        self.__lastCommand = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        GObject.timeout_add(1000, lambda: self.update_terminal(self.__lastCommand.stdout))
        
    
    def non_block_read(self, output) -> str:
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        try:
            return output.read().decode("utf-8").strip()
        except:
            return ""
        
    def update_terminal(self, stdout):
        self.output.get_buffer().set_text(self.non_block_read(stdout))
        return self.__lastCommand.poll() is None
        