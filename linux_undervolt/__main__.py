#!/usr/bin/env python3
import sys

from .Application import Application

def main() -> None:
    app = Application()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == "__main__":
    main()
