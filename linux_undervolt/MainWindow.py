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

    def __init__(self):
        
        self.logger = logging.getLogger(self.__class__.__name__)

        # Define instance variables
        self.config = config.Config()
        self.builder = gtk.Builder()

        # Check if this is the first time the app is run
        if not config.checkPrerequisites():
            dialog = gtk.MessageDialog(
                message_type=gtk.MessageType.ERROR,
                buttons=gtk.ButtonsType.CLOSE,
                text="""The prerequisites for this program have not been met. Please check whether you have the
                required programs (intel-undervolt) properly installed."""
            )

            self.logger.error("intel-undervolt not installed. Install the package before running this program")
            
            dialog.run()
            dialog.destroy()
            return
        
        self.builder.add_from_file(MAIN_WINDOW)
        
        # Initial setup
        self.__initialSetup__()
        self.builder.connect_signals(self)

        # Show Main window
        self.topLevelWindow = self.builder.get_object("Main")
        self.destroy_signal = self.topLevelWindow.connect("delete-event", gtk.main_quit)
        
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
        
        Notify.init("Linux Undervolt Tool")
        
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
    
    def toggleAdvanced(self, widget) -> None:
        from .AdvancedWindow import AdvancedWindow
        state = widget.get_active()
        
        self.config.changeSettings('advanced', str(state))
        
        if state:
            window = AdvancedWindow()
        else:
            window = MainWindow()
            
        
        self.topLevelWindow.disconnect(self.destroy_signal)
        self.topLevelWindow.destroy()
        
        self.destroy_signal = None
        
        window.topLevelWindow.connect("delete-event", gtk.main_quit)
        window.topLevelWindow.show_all()
        
        mode = "advanced" if state else "simple"
        
        self.logger.info(f"Changed to {mode} mode.")
    
    def powerProfileActivate(self, _, state) -> None:
        """
        docstring
        """

        state_str = str(state).lower()
        
        if not state:
            run = backend.removeUdevRule()

            # If the run fails, do not change the UI. TODO: Add error message stating that the run failed.
            if run:
                return        
        
        self.config.changeSettings('battery_switch', state_str)
        self.__powerSwitch__()

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

    def importConfig(self, _) -> None:

        dialog = gtk.FileChooserDialog(
            title="Choose import file",
            action=gtk.FileChooserAction.OPEN
        )

        dialog.add_buttons(
            gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
            gtk.STOCK_OPEN, gtk.ResponseType.OK
        )

        file_filter = gtk.FileFilter()
        file_filter.set_name("Config File")
        file_filter.add_pattern("*.conf")

        dialog.add_filter(file_filter)

        response = dialog.run()

        if response == gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.config = config.Config(filename)
            self.config.saveChanges()
        
        dialog.destroy()

    def exportConfig(self, _) -> None:
        
        dialog = gtk.FileChooserDialog(
            title="Select export file",
            action=gtk.FileChooserAction.SAVE
        )

        # Set default export file name
        file_name = date.today().isoformat()
        file_name = f"{file_name}_linux-undervolt.conf"
        dialog.set_current_name(file_name)

        dialog.add_buttons(
            gtk.STOCK_SAVE, gtk.ResponseType.OK,
            gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL
        )

        response = dialog.run()

        if response == gtk.ResponseType.OK:
            self.config.exportConfig(dialog.get_filename())
        
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

    def applyProfile(self, _) -> None:
        """
        Apply the undervolt from the current profile values.
        """
        
        code = self.config.applyChanges().returncode
        sleep(0.3)

        if not code:
            Notify.Notification.new(
                summary="Profile Applied",
                body=f"Profile {self.config.getSettings('profile')}'s settings were applied."
            ).show()
        else:
            dialog = gtk.MessageDialog(
                message_type=gtk.MessageType.ERROR,
                buttons=gtk.ButtonsType.OK,
                text='Something Failed. Undervolt not applied.'
            )

            dialog.run()
            dialog.destroy() 

    ##################
    # Menu Functions #
    ##################
    
    def about(self, _) -> None:
        dialog = gtk.MessageDialog(
            message_type=gtk.MessageType.INFO,
            transient_for=self.topLevelWindow,
            flags=0,
            buttons=gtk.ButtonsType.OK,
            text="About"
        )
        
        dialog.format_secondary_markup(
            'This tool was made using Python and GTK.'
            ' Find the source code at <a href="https://github.com/TheOneMaster/linux-undervolt">the Github repository</a>.'
        )
        
        self.logger.info("Showed about dialog")
        dialog.run()
        dialog.destroy()
    