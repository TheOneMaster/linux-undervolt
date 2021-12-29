#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from window import MainWindow

def main():
    root = MainWindow(title="Linux Undervolt Tool")

    if not root.failed:
        root.connect("destroy", Gtk.main_quit)
        root.show_all()
        Gtk.main()
    else:
        pass

if __name__ == "__main__":
    main()
