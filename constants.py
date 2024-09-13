from enum import Enum
# constants


APPLICATION_NAME = 'brave.exe'

# Colours
GREEN = "\033[32m"
RESET = "\033[0m"  # Reset to default color
BLUE = "\033[34m"
RED = "\033[41m"
INVERTED = "\033[7m"

# types
class Command_Menu(Enum):
    RAM_WATCHER = 0
    RAM_USED = 1
    THRESHOLD = 2
    APPLICATION = 3
    NOTIFICATIONS = 4
    NOTIFICATIONS_TIMER = 5
    EXIT = 6