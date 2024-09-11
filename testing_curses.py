import curses
import time
from constants import APPLICATION_NAME, RED, RESET, BLUE, GREEN
from art import *
from monitor import *
from utils import *

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # Get terminal dimensions
    height, width = stdscr.getmaxyx()

    # Initial dynamic content
    dynamic_content = ["Dynamic line 1", "Dynamic line 2", "Dynamic line 3"]

    # Disable cursor blinking and enable input echo
    curses.curs_set(1)
    stdscr.keypad(True)
    
    # Main loop to keep the terminal interactive
    
    while True:
        try:
            # Print dynamic content at the top
            for idx, line in enumerate(dynamic_content):
                stdscr.addstr(idx, 0, line)  # Print each line at its respective index
            
            # Prompt for user input at the bottom
            stdscr.addstr(height - 2, 0, "Type something (or 'exit' to quit): ")  # Input prompt
            stdscr.clrtoeol()  # Clear to the end of the line to ensure no artifacts

            # Refresh screen to show updates
            stdscr.refresh()

            # Get user input at the bottom
            curses.echo()  # Echo user input
            user_input = stdscr.getstr(height - 1, 0).decode("utf-8").strip()
            curses.noecho()  # Stop echoing after input is taken

            # Process input if necessary
            if user_input.lower() == 'exit':
                break  # Exit the loop if the user types 'exit'

            # Update dynamic content (just as an example)
            dynamic_content.append(f"You typed: {user_input}")
            if len(dynamic_content) > (height - 3):
                dynamic_content.pop(0)  # Keep dynamic content within screen size

            time.sleep(0.5)  # Delay to simulate dynamic updates
        except KeyboardInterrupt:
            break
            


# Initialize curses and start the main function
# curses.wrapper(main)

# expirimenting with display screen and curses

def display_screen(stdscr, help=False, startup=False):
    """
    Function to display the dynamic screen content while keeping input at the bottom.
    """

    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green text
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Red text

    # Clear the screen initially
    stdscr.clear()

    # Disable cursor blinking
    curses.curs_set(1)
    stdscr.keypad(True)

    # Get terminal dimensions
    height, width = stdscr.getmaxyx()

    # Titles and lines to be displayed
    homeTitle = "Home"
    homeLines = [
        f"RAM Watcher: {returnToggle(get_watcher())}",
        f"RAM used: {dictToInt(memory_usage_data)} MB",
        f"Threshold: {get_threshold()} MB",
        f"Application: {APPLICATION_NAME}",
        f"Notifications: {returnToggle(get_notification())}",
        f"Timer: {display_timer(get_interval())}"
    ]

    helpTitle = "Help"
    helpLines = [
        "RAM Watcher: (o)",
        "RAM used: (ur a bitch)",  # Replace with appropriate message
        "Threshold: (t)",
        "Application: (a)",
        "Notifications: (n)",
        "Timer: (ns)"
    ]

    while True:
        # Clear screen at each iteration
        stdscr.clear()

        # Select which content to display at the top
        if startup:
            dynamic_content = create_separator(homeTitle, *homeLines)
        elif help:
            dynamic_content = create_separator(helpTitle, *helpLines)
        else:
            dynamic_content = create_separator(homeTitle, *homeLines)

        # Print the dynamic content at the top
        for idx, line in enumerate(dynamic_content.splitlines()):
            stdscr.addstr(idx, 0, line)

        # Print help and exit information at the bottom with colors
        stdscr.addstr(height - 30, 0, "CAPS LOCK for help / clear", curses.color_pair(1))  # Green text
        stdscr.addstr(height - 29, 0, "e to quit gracefully...", curses.color_pair(2))      # Red text

        # Refresh screen to show updates
        stdscr.refresh()

        # Capture user input at the bottom
        curses.echo()  # Echo user input
        user_input = stdscr.getstr(height - 5, 0).decode("utf-8").strip()
        curses.noecho()  # Stop echoing after input is taken

        # Process input
        if user_input.lower() == 'e':
            break  # Exit if 'e' is typed
        elif user_input.lower() == 'caps lock':
            help = not help  # Toggle the help screen on CAPS LOCK
        elif user_input.lower() == 'clear':
            # Reset to the default screen
            help = False
            startup = False

        # Simulate delay to show dynamic content update
        time.sleep(0.1)

# Wrapper to run the curses application
curses.wrapper(display_screen)


