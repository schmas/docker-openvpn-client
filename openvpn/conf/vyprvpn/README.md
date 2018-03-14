# VyprVPN
## Configuration Files
Configuration files have been created for both 160-bit and 256-bit options.
A symlink has been created for each of the 256-bit configurations.
File names have been reduced for simplicity.

## Configuration Updater (updateConfigs.py)
Python3 stdlib script is provided to update the VyprVPN configuration files.

## Up/Down Scripts
In order to respect the VyprVPN DNS push, custom Up/Down scripts are provided.
This should plug DNS leaks and eliminate the need for Google (or other) DNS.

## Known Issues
### Down Script
Down script has not been thoroughly tested.
It has failed before.
