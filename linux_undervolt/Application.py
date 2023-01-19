import sys
from typing import Type, List, Optional
import logging
from datetime import date

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Notify

from .AdvancedWindow import AdvancedWindow
from .MainWindow import MainWindow
from .config import Config, checkPrerequisites, configExists
from .backend import createBackup, removeUdevRule

class Application(Gtk.Application):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, 
                         application_id="org.theonemaster.linux_undervolt",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.window: Optional[Gtk.Window] = None
        
        if not checkPrerequisites():
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE,
                text="""The prerequisites for this program have not been met. Please check whether you have the
                required programs (intel-undervolt) properly installed."""
            )
            self.logger.error("intel-undervolt not installed on the system. Please install before running. Closing the program.")
            dialog.run()
            dialog.destroy()
            self.quit()
        
        self.config = None
        if not configExists():
            self.config = Config.create_config()
            createBackup()
        else:
            self.config = Config()
            
        self.main_windows: List[Type[MainWindow]] = [MainWindow, AdvancedWindow]
        self.window_state = self.config.getInt("advanced")
        

    
    def do_activate(self) -> None:
        if not self.window:
            self.window = self.main_windows[self.window_state](self.config)
            window = self.window.topLevelWindow
            window.set_application(self)
            window.show_all()
        
        self.window.topLevelWindow.present()
    
    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        
        Notify.init("Linux Undervolt Tool")
        
        # Set application actions
        action_map = {
            "about": self.about_dialog,
            "toggle_advanced": self.toggleAdvanced,
            "activate": self.apply_profile,
            "apply_profile": self.apply_profile,
            "import_config": self.import_config,
            "export_config": self.export_config,
            "power_profile_toggle": self.power_profile_toggle
        }
        
        for actionId, callback in action_map.items():
            action = Gio.SimpleAction.new(actionId, None)
            action.connect("activate", callback)
            self.add_action(action)
    
    def do_command_line(self, command_line) -> None:
        options = command_line.get_options_dict()
        options = options.end().unpack()
        
        # Do things with the options dictionary
        
        self.activate()
        return 0
    
    
    # Menu items 
    def toggleAdvanced(self, action: Gio.SimpleAction, parameter: Optional[GLib.VariantType]) -> None:                
        self.window_state = 1 - self.window_state
        self.config.changeSettings("advanced", str(self.window_state))
        
        self.window.topLevelWindow.destroy()
        self.window = None
        
        self.do_activate()
            
    def about_dialog(self, action: Gio.SimpleAction, parameter: Optional[GLib.VariantType]) -> None:
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            transient_for=self.window.topLevelWindow,
            flags=0,
            buttons=Gtk.ButtonsType.OK,
            text="About"
        )
        
        dialog.format_secondary_markup(
            'This tool was made using Python and Gtk.'
            ' Find the source code at <a href="https://github.com/TheOneMaster/linux-undervolt">the Github repository</a>.'
        )
        
        # self.logger.info("Showed about dialog")
        dialog.run()
        dialog.destroy()
    
    def import_config(self, action: Gio.SimpleAction, parameter: Optional[GLib.VariantType]) -> None:
        dialog = Gtk.FileChooserDialog(
            title="Choose import file",
            action=Gtk.FileChooserAction.OPEN
        )

        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Config File")
        file_filter.add_pattern("*.conf")

        dialog.add_filter(file_filter)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.config = Config(filename)
            self.config.save()
            
            self.window.config = self.config
            self.window.__initialSetup__()
        
        dialog.destroy() 
    
    def export_config(self, action: Gio.SimpleAction, parameter: Optional[GLib.VariantType]) -> None:
        dialog = Gtk.FileChooserDialog(
            title="Select export file",
            action=Gtk.FileChooserAction.SAVE
        )

        # Set default export file name
        file_name = date.today().isoformat()
        file_name = f"{file_name}_linux-undervolt.conf"
        dialog.set_current_name(file_name)

        dialog.add_buttons(
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
        )

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.config.save(dialog.get_filename())
        
        dialog.destroy()
    
    
    # Button Logic
    def apply_profile(self, action: Gio.SimpleAction, parameter: Optional[GLib.VariantType]) -> None:
        code = self.config.applyChanges().returncode
        
        if not code:
            Notify.Notification.new(
                summary="Profile Applied",
                body=f"Profile {self.config.getActiveProfile()} settings were applied."
            ).show()
        else:
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Something failed. Undervolt not applied."
            )
            dialog.run()
            dialog.destroy()
    
    def power_profile_toggle(self, action: Gio.SimpleAction, parameter: Optional[GLib.VariantType]) -> None:
        power_state = self.config.getBool("battery_switch")
        power_state = not power_state
        
        if not power_state:
            run = removeUdevRule()
            
            # If the run fails do not change the UI. TODO: Add error message stating that the run failed
            if run:
                return
    
        self.config.changeSettings('battery_switch', str(power_state))
        self.window.__powerSwitch__()
    
    def on_quit(self) -> None:
        self.quit()
        
        
    
if __name__ == "__main__":
    app = Application()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
