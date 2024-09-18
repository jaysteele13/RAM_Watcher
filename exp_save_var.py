import configparser
import os
from constants import *

CONFIG_FILE = 'config.ini'
DEFAULT_SECTION = 'DEFAULT'

# Initialize configparser
config = configparser.ConfigParser()

# Function to load the config file
def load_config():
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        # Set default values if config doesn't exist
        config[DEFAULT_SECTION] = {Command_Menu.RAM_WATCHER: True, Command_Menu.RAM_USED: 10, Command_Menu.THRESHOLD: 1250, Command_Menu.NOTIFICATIONS: True, Command_Menu.NOTIFICATIONS_TIMER: 600}
        save_config()

# Function to save the config file
def save_config():
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Function to set a specific config value
def set_config_value(key, value, section = DEFAULT_SECTION):
    key = str(key)
    value = str(value)

    # Compare current file data with new data
    if config[section][key] == value:
        return
    else:
        if section not in config:
                config[section] = {}
        config[section][key] = value
        save_config()

    

# function to check if i need to rewrite values

def get_config_value(key, section=DEFAULT_SECTION):
    """
    This function retrieves a specific configuration value from the config file.
    If the section or key doesn't exist, it returns None.
    """
    key = str(key)
    if section in config and key in config[section]:
        return convert_value(config[section][key])
    else:
        return None  # Return None if the key/section doesn't exist
    
def convert_value(value):
    # Try converting to Boolean
    if isinstance(value, bool):
        return value
    elif isinstance(value, (int, float, str)) and value in {0, 1}:
        return bool(value)
    elif value == 'True':
        return True
    elif value == 'False':
        return False

    # Try converting to Integer
    try:
        return int(value)
    except (ValueError, TypeError):
        pass
    
    # Try converting to Float
    try:
        return float(value)
    except (ValueError, TypeError):
        pass
    
    # Fallback to String
    return str(value)