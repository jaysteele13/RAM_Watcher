import keyboard
import threading
import os
import re
from art import *
from monitor import *
import ctypes
from constants import *
import curses
import sys

# Variable to hold the process of the currently running script
current_process = None
help = False
# Initialize memory variable
memory = None
# Define timeout duration in seconds
timeout_duration = 1200
refresh_rate = 15

# STOP DEBOUNCING for FLAG
last_shift_event_time = 0
debounce_interval = 0.5  # 500 milliseconds
def set_default_values():
    # Defaults (dk if these are necessary)
    set_refresh_rate(1)
    set_threshold(1250)
    set_interval(600) # 10 mins default
    set_watcher(True)
    set_notification(True)


#instead have a function that just maps this
def map_row_to_command(row: int) -> Command_Menu:
    try:
        return Command_Menu(row)  # Convert integer to corresponding enum
    except ValueError:
        raise ValueError("Invalid row number, cannot map to Command_Menu")  # Handle invalid rows

def dictToInt(memory):
    memory_usage_str = str(memory)
    
    # Search for the first occurrence of one or more digits in the string
    match = re.search(r'\d+', memory_usage_str)
    
    if match:
        # Extract the number and convert it to an integer
        return float(match.group())
        # " decimal places"
    else:
        return "Retrieving RAM"

def returnToggle(toggle):
    return "On" if toggle else "Off"

# Clear screen function
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_timer(interval):
    if interval == 60:
        return f"{int(interval/60)} min"
    else: 
        return f"{int(interval/60)} mins"
    

def allow_text(allow = True):
    if allow:
        curses.echo()  # Enable echoing of inputs
        curses.curs_set(1)
    else:
        curses.curs_set(0)
        curses.noecho()


        
def is_terminal_focused():
    # Get the current active window handle
    active_window_handle = ctypes.windll.user32.GetForegroundWindow()

    # Get the window title of the active window
    window_title = ctypes.create_string_buffer(512)
    ctypes.windll.user32.GetWindowTextA(active_window_handle, window_title, 512)

    terminal_titles = [b"RAM_Watcher"]
    return any(title in window_title.value for title in terminal_titles)


def change_number_validation(stdscr, number, setter):
    # Check for empty input

    while True:
        if number == "":
            print_center(stdscr, 'Empty response, would you still like to set a value? (y/n): ', highlight_phrase="y/n")
            emptyResponse = stdscr.getstr().decode("utf-8").lower().strip()
            if emptyResponse == 'y':
                emptyResponse = stdscr.getstr().decode("utf-8").lower().strip()
                change_number_validation(stdscr, emptyResponse, setter)
                break
            elif emptyResponse == 'n':
                break
            else:
                allow_text(False)
                print_center(stdscr, "I'm done with you.")
                break
        else:
            # Attempt to convert input to a float
            try:
                number = int(number)  # Convert to float
                if setter == set_interval:
                    number = number*60         
                setter(number)
                print_center(stdscr, 'Setting value...')
                curses.napms(500)
                break
            except ValueError:
                print_center(stdscr, 'You must input a whole number! Exiting...', highlight_phrase="whole number", color_pair=8)
                curses.napms(500)
                break


def handle_language_refresh_rate_change(refresh):
    if refresh == 10:
        return "Standard Refresh rate is 10 seconds , do you really wanna change that (this could displace the notification timer)?"
    else:
        return f"Modified Refresh Rate is {refresh}, wanna change this again?"
    

# ammend this so it takes certain text to change colour of
def print_center(stdscr, text, highlight_phrase=None, color_pair=4):
    stdscr.clear()
    h, w = stdscr.getmaxyx()  # Get the screen height and width
    
    # Split text into multiple lines if it exceeds the screen width
    lines = []
    while len(text) > w:
        # Find the last space within the first w characters
        split_index = text[:w].rfind(" ")
        if split_index == -1:
            # If no space found, force split at the screen width
            split_index = w
        # Append the split line and update the text
        lines.append(text[:split_index])
        text = text[split_index:].strip()  # Trim leading spaces in the next part
    
    # Append the remaining text
    lines.append(text)

    # Calculate vertical starting point to center the block of text
    y_start = max(0, h // 2 - len(lines) // 2)

    # Display each line centered on the screen
    for i, line in enumerate(lines):
        x = max(0, w // 2 - len(line) // 2)  # Center each line horizontally
        
        if highlight_phrase and highlight_phrase in line:
            # Find where the highlighted phrase starts in the line
            start_idx = line.find(highlight_phrase)
            # Print the text before the phrase
            stdscr.addstr(y_start + i, x, line[:start_idx])
            # Print the highlighted phrase in the chosen color
            stdscr.attron(curses.color_pair(color_pair))
            stdscr.addstr(line[start_idx:start_idx + len(highlight_phrase)])
            stdscr.attroff(curses.color_pair(color_pair))
            # Print the text after the phrase
            stdscr.addstr(line[start_idx + len(highlight_phrase):])
        else:
            # If no highlight, print the whole line as usual
            stdscr.addstr(y_start + i, x, line)
        
    stdscr.refresh()  # Refresh the screen to show the text


def handle_commands(stdscr, command_type: Command_Menu):
    handling = True
    while handling:
        allow_text()
        handling = False

        if command_type == Command_Menu.EXIT:
            print_center(stdscr, f"Exiting the program GRACEFULLY.\n", highlight_phrase="GRACEFULLY")
            stdscr.refresh()
            curses.napms(1000)
            curses.endwin()  # Ensure curses cleanup
            handling = False
            sys.exit(0)  # Use sys.exit() to terminate properly

        elif command_type == Command_Menu.RAM_USED:
           
            print_center(stdscr, f"{handle_language_refresh_rate_change(get_refresh_rate())} y/n: ", highlight_phrase=str(get_refresh_rate()))
            stdscr.refresh()
            response = stdscr.getstr().decode("utf-8").lower().strip()
            if response == 'y':
                print_center(stdscr,"Right then, select a time in seconds to refresh RAM here: ")
                stdscr.refresh()
                number = stdscr.getstr().decode("utf-8").strip()
                change_number_validation(stdscr, number, set_refresh_rate)
            else:
                allow_text(False)
                break

        elif command_type == Command_Menu.RAM_WATCHER:
            allow_text(False)
            print_center(stdscr, "Toggling RAM_Watcher\n", highlight_phrase="RAM_Watcher")
            stdscr.refresh()
            set_watcher(not get_watcher())

        elif command_type == Command_Menu.THRESHOLD:
            print_center(stdscr, f"What would you like to change the threshold ({get_threshold()}) to: ", highlight_phrase=str(get_threshold()))
            stdscr.refresh()
            number = stdscr.getstr().decode("utf-8").strip()
            change_number_validation(stdscr, number, set_threshold)

        elif command_type == Command_Menu.APPLICATION:
            allow_text(False)
            print_center(stdscr, "This doesn't change. Your a bitch for thinking I'd put in this much effort\n", highlight_phrase="bitch", color_pair=8)
            curses.napms(2000)
            stdscr.refresh()

        elif command_type == Command_Menu.NOTIFICATIONS:
            allow_text(False)
            print_center(stdscr, "(Don't see why you would turn this off as it's the whole point of this app but fuck it)\n")
            stdscr.refresh()
            curses.napms(1000)
            print_center(stdscr, "Toggling Notification\n", highlight_phrase="Notification")
            set_notification(not get_notification())

        elif command_type == Command_Menu.NOTIFICATIONS_TIMER:
            print_center(stdscr, f"What would you like to change the timer ({display_timer(get_interval())}) to (min): ", highlight_phrase=str(display_timer(get_interval())))
            stdscr.refresh()
            number = stdscr.getstr().decode("utf-8").strip()
            change_number_validation(stdscr, number, set_interval)
        else:
            print_center(stdscr, f"Unknown command: {command}\n")
            handling = True

        stdscr.refresh()
        curses.napms(500)

     
def startup():
    # On start up do this
    clear_screen()
    print('Launching RAM Watcher - Jay steele')
    time.sleep(1)
    # Call the function
    print_graphic(graphic)
    time.sleep(1)
    clear_screen()



