#! /usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from window import MainWindow


if __name__ == "__main__":
    root = MainWindow(title="Linux Undervolt Tool")
    root.connect("destroy", Gtk.main_quit)
    root.show_all()

    Gtk.main()

    