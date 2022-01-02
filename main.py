import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

from time import sleep
import os

import config


class MainWindow:

    SCALE_MAP = {
        'cpu': 'cpu_scale',
        'cpu_cache': 'cpuCache_scale',
        'gpu': 'gpu_scale',
        'sys_agent': 'sysAgent_scale',
        'analog_io': 'anIO_scale'
    }

    def __init__(self):

        # Define instance variables
        self.config = None
        self.builder = gtk.Builder()
        self.active_profile = None

        # Check if this is the first time the app is run
        if not os.path.isfile(config.CONFIG_DIRECTORY):
            return_code = self.firstTimeSetup()

            if return_code != gtk.ResponseType.OK:
                return
        else:
            self.config = config.Config(created=True)

        # Create template and add general signals 
        gladeFile = "GUI.glade"
        
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)

        # Initial setup
        self.scaleChange()
        self.getPowerProfiles()
        
        # Set correct profile button active
        button_id = f"profile_{self.config.active_profile}_button"
        radio_button = self.builder.get_object(button_id)
        radio_button.set_active(True)

        # Show Main window
        window = self.builder.get_object("Main")
        window.connect("delete-event", gtk.main_quit)
        window.show()

    def firstTimeSetup(self):
        """
        Creates the initial files required for the application to run. This is only called the first time
        the application is run. 
        """

        # Check whether intel-undervolt has been installed.

        prereqs = config.checkPrerequisites()
        if prereqs:
            default_undervolt_path = '/etc/intel-undervolt.conf'
            
            if os.path.isfile(default_undervolt_path):
                self.config = config.Config()
                return gtk.ResponseType.OK

            else:
                # TODO: Add file chooser dialog for undervolt conf file
                folder_dialog = gtk.FileChooserDialog("Select intel-undervolt Config File", None, gtk.FileChooserAction.OPEN,
                (gtk.STOCK_CLOSE, gtk.ResponseType.CLOSE, gtk.STOCK_OPEN, gtk.ResponseType.OK))
        
                filter_conf = gtk.FileFilter()
                filter_conf.set_name("Configuration files")
                filter_conf.add_pattern("*.conf")
                folder_dialog.add_filter(filter_conf)

                response = folder_dialog.run()

                if response == gtk.ResponseType.OK:
                    response = folder_dialog.get_filename()
                    options = {'undervolt_path': response}
                    self.config = config.Config(options=options)
                else:
                    folder_dialog.destroy()

                return response
        else:
            # TODO: Create an error dialog letting the user know what isn't installed.
            
            dialog = gtk.MessageDialog(
                message_type=gtk.MessageType.ERROR,
                buttons=gtk.ButtonsType.CLOSE,
                text="""The prerequisites for this program have not been met. Please check whether you have the
                required programs (intel-undervolt) properly installed."""
            )

            dialog.run()
            dialog.destroy()

            return dialog

    ##############
    # UI Changes #
    ##############

    def scaleChange(self):
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

    def changeProfile(self, widget):
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

        self.scaleChange()

    def getPowerProfiles(self):
        """
        docstring
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

    #####################
    # Profile Functions #
    #####################

    def saveProfile(self, _):

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

    def applyProfile(self, _):
        
        code = self.config.applyChanges().returncode
        sleep(0.3)

        if not code:
            dialog = gtk.MessageDialog(
                message_type=gtk.MessageType.INFO,
                buttons=gtk.ButtonsType.OK,
                text='Undervolt applied'
            )
        else:
            dialog = gtk.MessageDialog(
                message_type=gtk.MessageType.ERROR,
                buttons=gtk.ButtonsType.OK,
                text='Something Failed. Undervolt not applied.'
            )

        dialog.run()
        dialog.destroy() 

    def setPowerProfile(self, _):
        """
        docstring
        """

        options = {
            "ac_profile": "",
            "battery_profile": ""
        }

        ac_power_bool = self.builder.get_object("ac_profile_bool")
        bat_power_bool = self.builder.get_object("bat_profile_bool")

        if ac_power_bool.get_active():
            ac_power_profile = self.builder.get_object("ac_profile")
            ac_profile = ac_power_profile.get_active()
            options['ac_profile'] = str(ac_profile)
        
        if bat_power_bool.get_active():
            bat_power_profile = self.builder.get_object("bat_profile")
            bat_profile = bat_power_profile.get_active()
            options['battery_profile'] = str(bat_profile)

        self.config.changeSettings(options)
        



if __name__ == "__main__":
    
    main = MainWindow()
    gtk.main()
