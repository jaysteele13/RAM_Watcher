from enum import Enum
import curses
# constants


APPLICATION_NAME = 'brave.exe'

# Colours
RESET = "\033[0m"  # Reset to default color
BLUE = "\033[34m"
GREEN = "\033[1;32m"
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

def init_colors():
    curses.start_color()
    curses.init_pair(123, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_RED)
