from typing import Optional

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import Notify

from datetime import date
from time import sleep
import logging


from . import config
from . import backend
from .constants import MAIN_WINDOW

class MainWindow:

    SCALE_MAP = {
        'cpu': 'cpu_scale',
        'cpu_cache': 'cpuCache_scale',
        'gpu': 'gpu_scale',
        'sys_agent': 'sysAgent_scale',
        'analog_io': 'anIO_scale'
    }

    def __init__(self, config):
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(MAIN_WINDOW)
        
        # Initial setup
        self.__initialSetup__()
        self.builder.connect_signals(self)

        # Show Main window
        self.topLevelWindow: gtk.Window = self.builder.get_object("Main")
        # self.destroy_signal = self.topLevelWindow.connect("delete-event", gtk.main_quit)
        
        self.logger.debug("Finished setup for main window")
    
    ##############
    # UI Changes #
    ##############
    

    def __initialSetup__(self) -> None:
        """
        Initial UI Settings to be loaded when the app is starting. Reads config options from config file
        and applies them to the various widgets.
        """

        self.__scaleChange__()
        self.__getPowerProfiles__()
        self.__powerSwitch__()
        self.__startupMenuItem__()
        
        # Set correct profile button active
        active_profile = self.config.getSettings('profile')
        button_id = f"profile_{active_profile}_button"
        
        radio_button = self.builder.get_object(button_id)
        radio_button.set_active(True)

    def __scaleChange__(self) -> None:
        """
        Changes the scale values to the current profile values.
        """

        current_settings = self.config.getProfileSettings()

        for key, value in current_settings.items():

            object_id = MainWindow.SCALE_MAP[key]
            scale = self.builder.get_object(object_id)
            
            # Values are stored as strings thus need to be converted to int
            value = int(value)
            scale.set_value(value)
            
        self.logger.info(f"Set scales to Profile {self.config.getActiveProfile()} settings")

        save_button = self.builder.get_object("save_button")
        save_button.set_label("Save")

    def __getPowerProfiles__(self) -> None:
        """
        Change power profile dropdowns to settings value.
        """

        settings = self.config.getSettings()

        bat_profile = settings['battery_profile']
        ac_profile = settings['ac_profile']

        if bat_profile:
            bat_profile = int(bat_profile)
            bat_profile_dropdown = self.builder.get_object("bat_profile")
            bat_profile_check = self.builder.get_object("bat_profile_bool")

            bat_profile_dropdown.set_active(bat_profile)
            bat_profile_check.set_active(True)

        if ac_profile:
            ac_profile = int(ac_profile)
            ac_profile_dropdown = self.builder.get_object("ac_profile")
            ac_profile_check = self.builder.get_object("ac_profile_bool")

            ac_profile_dropdown.set_active(ac_profile)
            ac_profile_check.set_active(True)

    def __powerSwitch__(self) -> None:
        """
        Activate or deactivate the power profile options according to settings.
        """

        active = self.config._parser.getboolean('SETTINGS', 'battery_switch')
        
        switch = self.builder.get_object('power_switch')
        switch.set_active(active)

        objects = ['ac_profile_box', 'bat_profile_box', 'power_profile_button']
        for object in objects:
            cur_obj = self.builder.get_object(object)
            cur_obj.set_sensitive(active)

    def __startupMenuItem__(self) -> None:

        active = self.config.getBool('startup')
        item = self.builder.get_object("startup_menu_item")

        item.set_active(active)

    def onSliderChange(self, widget) -> None:
        """
        Changes the save button to be italicised when changes are made to the undervolt values.
        """

        label = widget.get_child()
        label.set_markup("<i>Save*</i>")


    ####################
    # Config Functions #
    ####################

    def startupChange(self, widget) -> None:
        startup_value = 1 if widget.get_active() else 0
        self.config.changeSettings('startup', str(startup_value))
        backend.startupChange(startup_value)

    def changeProfile(self, widget) -> None:
        """
        Change the undervolt profile based on which radiobutton is selected. Also redraws the scales based on the new
        profile's settings.
        """
        group_list = widget.get_group()
        for option in group_list:
            if option.get_active():
                new_profile = option.get_label()
                self.config.changeSettings('profile', new_profile)
                break

        self.__scaleChange__()

    def setPowerProfile(self, _) -> None:
        """
        docstring
        """
        options = {
            "ac_profile": "",
            "battery_profile": ""
        }

        ac_power_bool = self.builder.get_object("ac_profile_bool").get_active()
        bat_power_bool = self.builder.get_object("bat_profile_bool").get_active()

        backend_dict = {}

        # Battery power profile is required to set profiles
        if ac_power_bool and not bat_power_bool:

            error = gtk.MessageDialog(
                message_type=gtk.MessageType.ERROR,
                buttons=gtk.ButtonsType.OK,
                text="Battery Profile is required to set an AC profile"
            )
            return

        if ac_power_bool:
            ac_power_profile = self.builder.get_object("ac_profile")
            ac_profile = ac_power_profile.get_active()
            options['ac_profile'] = str(ac_profile)
            backend_dict['ac'] = str(ac_profile)
        
        if bat_power_bool:
            bat_power_profile = self.builder.get_object("bat_profile")
            bat_profile = bat_power_profile.get_active()
            options['battery_profile'] = str(bat_profile)
            backend_dict['bat'] = str(bat_profile)

        self.config.changeSettings(options)
        code = backend.createUdevRule(backend_dict).returncode
        
        if not code:
            Notify.Notification.new(
                summary="Profile switching active",
                body="Switching profiles on the power supply change is now active."
            ).show()
        else:
            dialog = gtk.MessageDialog(
                message_type=gtk.MessageType.ERROR,
                buttons=gtk.ButtonsType.OK,
                text="An error occurred."
            )

            dialog.run()
            dialog.destroy()

    def saveProfile(self, _) -> None:
        """
        Save scale values to the profile in the config
        """

        # Get the values from the scales
        current_settings = self.config.getProfileSettings()

        new_settings = {}
        for key in current_settings:

            object_id = MainWindow.SCALE_MAP[key]
            scale = self.builder.get_object(object_id)

            new_value = scale.get_value()
            new_value = int(new_value)

            new_settings[key] =  new_value
        
        self.config.changeProfileSettings(new_settings)

        save_button = self.builder.get_object("save_button")
        save_button.set_label("Save")
    