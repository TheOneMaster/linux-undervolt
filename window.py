import os
from time import sleep
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import config

class MainWindow(Gtk.Window):

    settings_map = {0: "cpu", 1: "gpu", 2: "cpu_cache", 3: "sys_agent", 4: 'analog_io'}
    settings_map_inv = {v: k for k, v in settings_map.items()}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # self.set_resizable(False)

        if not config.checkConfigExists():
            self.firstTimeSetup()

        options = config.getCurrentProfileSettings()
        main_frame = self.createWidgets(options)

        self.add(main_frame)

    def createWidgets(self, options: tuple) -> Gtk.Grid:
        """
        Create the various widgets present on the main window. Any stored profile values can be passed to the constructor
        so that the widgets retain the profile's values when starting.
        """
        main_grid = Gtk.Grid(expand=True)

        active_profile = options[0]
        profile_options = options[1]

        ##################################
        # Scale for the undervolt values #
        ##################################

        scale_box = Gtk.Box(orientation=1)

        undervolt_hw = ['cpu', 'gpu', 'cpu_cache', 'sys_agent', 'analog_io']
        scale_labels = dict(cpu='CPU', gpu='GPU', cpu_cache="CPU Cache", sys_agent="System Agent", analog_io='Analog IO')
        undervolt_scale_list = []
        
        # Create and store the scales
        for i in undervolt_hw:
            
            frame = Gtk.Box(orientation=1)
            scale = Gtk.Scale.new_with_range(0, -100, 0, 5)
            scale.set_value(0)
            scale.set_hexpand(True)
            scale.set_vexpand(True)
            label = Gtk.Label(label=f"{scale_labels[i]} voltage")

            frame.pack_end(label, True, False, 0)
            frame.pack_start(scale, True, True, 0)
            
            scale_box.pack_start(frame, True, True, 5)
            
            undervolt_scale_list.append(scale)

        undervolt_scale_list[0].connect("value-changed", self.linkScale, undervolt_scale_list[2])
        undervolt_scale_list[2].connect("value-changed", self.linkScale, undervolt_scale_list[0])

        
        scale_box.set_margin_top(10)
        scale_box.set_margin_bottom(10)

        for key, value in profile_options.items():
                index = MainWindow.settings_map_inv[key]
                scale = undervolt_scale_list[index]
                scale.set_value(int(value))

        ##############################
        # Radio Buttons for Profiles #
        ##############################

        profile_box = Gtk.Box(spacing=5)
        # profile_box.set_hexpand(True)

        prof_1 = Gtk.RadioButton.new_with_label(None, "Profile 0")
        prof_2 = Gtk.RadioButton.new_with_label_from_widget(prof_1, "Profile 1")
        prof_3 = Gtk.RadioButton.new_with_label_from_widget(prof_2, "Profile 2")
        prof_4 = Gtk.RadioButton.new_with_label_from_widget(prof_3, "Profile 3")

        profile_list = [prof_1, prof_2, prof_3, prof_4]

        profile_list[active_profile].set_active(True)

        for index, profile in enumerate(profile_list):
            profile.connect("clicked", self.profileChange, index, undervolt_scale_list)
            profile.set_hexpand(True)
            profile_box.add(profile)

        ##############
        # Bottom Bar #
        ##############

        bottom = Gtk.Box(spacing=5)

        # Save Button

        save_button = Gtk.Button(label="Save")
        save_button.connect('clicked', self.profileSettingsChange, profile_list, undervolt_scale_list)

        # Apply button
        
        apply_button = Gtk.Button(label="Apply")
        apply_button.connect("clicked", self.applyUndervolt)

        bottom.pack_start(save_button, True, True, 1)
        bottom.pack_start(apply_button, True, True, 1)

        bottom.set_margin_start(2)
        bottom.set_margin_end(2)
        bottom.set_margin_bottom(2)

        ###############################
        # Attach widgets to main_grid #
        ###############################

        main_grid.attach(profile_box, 0, 0, 4, 1)
        main_grid.attach(scale_box, 0, 1, 4, 1)

        main_grid.attach(bottom, 0, 2, 4, 1)

        return main_grid

    def profileSettingsChange(self, widget, profiles: list, values: list):
        """
        This function is called when the "save" button is pressed. All values from the widgets are stored in the config file
        when this function is called.
        """
        profile = 0

        for index, prof in enumerate(profiles):
            if prof.get_active():
                profile = index
                break
        
        settings = {}
        
        for index, scale in enumerate(values):

            value = scale.get_value()
            value = int(value)
            key = MainWindow.settings_map[index]
            
            settings[key] = value

        profile = str(profile)

        config.changeProfileSettings(profile, settings)

    def profileChange(self, widget, name, scales):
        """
        This method is activated whenever the profile is changed. The config file is updated to the new profile and the widgets
        are updated to reflect the new profile's values.
        """
        if widget.get_active():
            config.changeProfile(str(name))
            settings = config.getProfileSettings(str(name))

            for key, value in settings.items():
                index = MainWindow.settings_map_inv[key]
                scale = scales[index]

                scale.set_value(int(value))

        else:
            pass

    def applyUndervolt(self, widget):
        """
        This method is called when the "apply" button is clicked. Attempts to apply all stored config values and 
        returns a message whether the undervolt was applied or failed.
        """
        code = config.applyProfile()
        sleep(0.3)

        return_code = code.returncode

        if not return_code:
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text='Undervolt applied'
            )
        else:
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text='Something Failed. Undervolt not applied.'
            )

        dialog.run()

        dialog.destroy()

    def firstTimeSetup(self):
        """This function is called only the first time the script is run. Used to initialize the default values for the config file.
        \n Asks the user to select the intel-undervolt folder.
        """
        
        folder_dialog = Gtk.FileChooserDialog("Select intel-undervolt Config File", None, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_conf = Gtk.FileFilter()
        filter_conf.set_name("Configuration files")
        filter_conf.add_pattern("*.conf")
        folder_dialog.add_filter(filter_conf)

        response = folder_dialog.run()

        if response == Gtk.ResponseType.OK:
            response = folder_dialog.get_filename()
        else:
            self.firstTimeSetup()

        folder_dialog.destroy()

        print(response)
        config.createConfig(undervolt_path=response)

        return response

    def linkScale(self, scale_1, scale_2):
        """
        Connect 2 scales so that when one scale moves, the other is synchronized with it.
        """
        
        value_new = scale_1.get_value()

        scale_2.set_value(value_new)