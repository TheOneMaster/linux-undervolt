import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

from time import sleep

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

        # Create template and add general signals 
        gladeFile = "GUI.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)

        # Initial setup
        self.scaleChange()

        # Show Main window
        window = self.builder.get_object("Main")
        window.connect("delete-event", gtk.main_quit)
        window.show()

    def scaleChange(self):
        """
        Changes the scale values to the current profile values.
        """
        current_settings = config.getCurrentProfileSettings()[1]

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
                config.changeProfile(new_profile)
                break

        self.scaleChange()

    def saveProfile(self, _):

        # Get the values from the scales
        current_profile, current_settings = config.getCurrentProfileSettings()

        new_settings = {}
        for key in current_settings:

            object_id = MainWindow.SCALE_MAP[key]
            scale = self.builder.get_object(object_id)

            new_value = scale.get_value()
            new_value = int(new_value)

            new_settings[key] =  new_value
        
        config.changeProfileSettings(current_profile, new_settings)

    def applyProfile(self, _):
        
        code = config.applyProfile().returncode
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

if __name__ == "__main__":
    
    main = MainWindow()
    gtk.main()
