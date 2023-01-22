import gi

gi.require_version("Gtk", "3.0")

import fcntl
import logging
import os
import subprocess

from gi.repository import GObject, Gtk

from .constants import EXIT_TERMINAL_SCRIPT


class TerminalOutput(Gtk.ScrolledWindow):
    
    def __init__(self, parent, *args,):
        super().__init__(*args)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.__parent = parent
        self.__lastCommand = None
        self.sudo = False
        self.timer = None
        
        self.output = Gtk.TextView()
        
        # TextView attributes
        self.output.set_monospace(True)
        self.output.set_editable(False)
        self.output.set_cursor_visible(False)
        self.output.set_wrap_mode(Gtk.WrapMode.WORD)
        
        # Scroll attributes
        self.set_vexpand(True)
        self.set_hexpand(True)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        
        self.add_with_viewport(self.output)
        self.logger.info("Finished setup for Terminal Output")
        # self.output.get_buffer().set_text("Testing")
     
    def create_command_list(self, command_list: list[str]):
        new_com_list = command_list.copy()
        if self.sudo:
            new_com_list.insert(0, 'pkexec')
        
        return new_com_list
        
    def run_command(self, command: list[str], sudo=False): 
        self.sudo = sudo           
        command_list = self.create_command_list(command)
        
        self.logger.info(f"Running command: {command_list}")
        # print(command_list)
        
        self.__lastCommand = subprocess.Popen(command_list, stdout=subprocess.PIPE, shell=False, start_new_session=True)
        self.timer = GObject.timeout_add(1000, self.update_terminal, self.__lastCommand.stdout)
        self.logger.info(f"Terminal with command '{command}' added")
        return False
        
    
    def non_block_read(self, output) -> str:
        # Black magic from SO: https://stackoverflow.com/a/17105259
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
    
    def end_command(self) -> None:
        if (self.__lastCommand is not None) and (self.__lastCommand.poll() is None):
            pid = self.__lastCommand.pid
            pgid = os.getpgid(pid)
            command_list = [EXIT_TERMINAL_SCRIPT, str(pgid)]
            if self.sudo:
                command_list.insert(0, "pkexec")
            
            self.logger.info(f"End Command: {command_list}")
            subprocess.run(command_list, shell=False)
            
            self.__lastCommand.communicate()
            GObject.source_remove(self.timer)
        