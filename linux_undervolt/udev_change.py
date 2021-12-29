#!/usr/bin/python3

import config
import argparse

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--set-profile", type=int)

    args = parser.parse_args()

    new_profile = args.set_profile

    if new_profile is not None:
        config.changeProfile(str(new_profile))
        config.applyProfile() 

if __name__ == "__main__":
    main()
