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
    set_refresh_rate(10)
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
    
def periodic_display_screen():
    while True:
        # Call display_screen only if the user is not typing
        if help == False:
            display_screen(help)  # Refresh display
        time.sleep(get_refresh_rate())  # Sleep for the refresh rate (e.g., 15 seconds)


def display_screen(help = False, startup=False):
        clear_screen()
        with memory_lock: 
            homeTitle = "Home"
            homeLines = [
                f"RAM Watcher: {returnToggle(get_watcher())}",
                f"RAM used: {dictToInt(memory_usage_data)} MB",
                f"Threshold: {get_threshold()} MB",
                f"Application: {APPLICATION_NAME}",
                (f"Notifications: {returnToggle(get_notification())}",
                f"Timer: {display_timer(get_interval())}")
            ]

            helpTitle = "Help"
            helpLines = [
            "RAM Watcher: (o)",
            "RAM used: (ur a bitch)",
            "Threshold: (t)",
            "Application: (a)",
            ("Notifications: (n)",
            "Timer: (ns)")
            ]

            if startup:
                print_graphic(create_separator(homeTitle, *homeLines))
            elif help:
                print(create_separator(helpTitle, *helpLines))
            else:
                print(create_separator(homeTitle, *homeLines))

            print(f"{GREEN}SHIFT{RESET} for help / refresh / clear\n{RED}e{RESET} to quit gracefully...")
        
def is_terminal_focused():
    # Get the current active window handle
    active_window_handle = ctypes.windll.user32.GetForegroundWindow()

    # Get the window title of the active window
    window_title = ctypes.create_string_buffer(512)
    ctypes.windll.user32.GetWindowTextA(active_window_handle, window_title, 512)

    terminal_titles = [b"RAM_Watcher"]
    return any(title in window_title.value for title in terminal_titles)

def handle_shift_event(e):
    global help
    global last_shift_event_time

    current_time = time.time()
    if (current_time - last_shift_event_time) < debounce_interval:
        # Ignore this event as it is within the debounce interval
        return

    if is_terminal_focused():
        help = not help  # Toggle help state
        display_screen(help)
        

    # Update the last processed time
    last_shift_event_time = current_time


def change_number_validation(number, setter):
    # Check for empty input

    while True:
        if number == "":
            print('Empty response, would you still like to set a value? (y/n)')
            emptyResponse = input("")
            if emptyResponse == 'y':
                emptyResponse = input("Set Number: ")
                change_number_validation(emptyResponse, setter)
                break
            elif emptyResponse == 'n':
                break
            else:
                print("I'm done with you")
                break
        else:
            # Attempt to convert input to a float
            try:
                number = int(number)  # Convert to float
                if setter == set_interval:
                    number = number*60         
                setter(number)
                print('Setting value...')
                time.sleep(0.5)
                break
            except ValueError:
                print('You must input a whole number!\nExiting...')
                time.sleep(0.5)
                break


def handle_language_refresh_rate_change(refresh):
    if refresh == 10:
        return "Standard Refresh rate is 10 seconds , do you really wanna change that (this could displace the notification timer)?"
    else:
        return f"Modified Refresh Rate is {refresh}, wanna change this again?"
    


def print_center(stdscr, text):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = w // 2 - len(text) // 2
    y = h // 2
    stdscr.addstr(y, x, text)
    stdscr.refresh()

def handle_commands(stdscr, command_type: Command_Menu):
    handling = True
    while handling:
        handling = False

        if command_type == Command_Menu.EXIT:
            print_center(stdscr, f"Exiting the program {GREEN}GRACEFULLY{RESET}.\n")
            stdscr.refresh()
            time.sleep(1)
            curses.endwin()  # Ensure curses cleanup
            handling = False
            sys.exit(0)  # Use sys.exit() to terminate properly

        elif command_type == Command_Menu.RAM_USED:
           
            print_center(stdscr, f"{handle_language_refresh_rate_change(get_refresh_rate())} y/n\n")
            # stdscr.addstr(f"{handle_language_refresh_rate_change(get_refresh_rate())} y/n\n")
            stdscr.refresh()
            response = stdscr.getstr().decode("utf-8").lower().strip()
            if response == 'y':
                print_center(stdscr,"Right then, select a time in seconds to refresh RAM here: ")
                stdscr.refresh()
                number = stdscr.getstr().decode("utf-8").strip()
                change_number_validation(number, set_refresh_rate)

        elif command_type == Command_Menu.RAM_WATCHER:
            print_center(stdscr, "Toggling RAM_Watcher\n")
            stdscr.refresh()
            set_watcher(not get_watcher())


        elif command_type == Command_Menu.THRESHOLD:
            stdscr.addstr(f"What would you like to change the {GREEN}threshold{RESET} ({get_threshold()}) to: ")
            stdscr.refresh()
            number = stdscr.getstr().decode("utf-8").strip()
            change_number_validation(number, set_threshold)

        elif command_type == Command_Menu.APPLICATION:
            stdscr.addstr("This doesn't change. You a bitch for thinking I'd put in this much effort\n")
            stdscr.refresh()

        elif command_type == Command_Menu.NOTIFICATIONS:
            stdscr.addstr("(Don't see why you would turn this off as it's the whole point of this app but fuck it)\n")
            stdscr.refresh()
            time.sleep(2)
            stdscr.addstr("Toggling Notification\n")
            stdscr.refresh()
            set_notification(not get_notification())

        elif command_type == Command_Menu.NOTIFICATIONS_TIMER:
            stdscr.addstr(f"What would you like to change the {GREEN}timer{RESET} ({display_timer(get_interval())}) to (min): ")
            stdscr.refresh()
            number = stdscr.getstr().decode("utf-8").strip()
            change_number_validation(number, set_interval)

        elif command == "":
            stdscr.addstr("That's an empty command sir!\n")
            handling = True

        else:
            stdscr.addstr(f"Unknown command: {command}\n")
            handling = True

        stdscr.refresh()
        time.sleep(0.5)
    
            
    # Show main some way curses.wrapper(main)


def monitor_threads():
    monitor_thread = threading.Thread(target=monitor_memory, args=(APPLICATION_NAME,), daemon=True)
    monitor_thread.start()

# Function to run both threads
def run_threads():
    
     # Start listening for shift key event
    keyboard.on_press_key("shift", handle_shift_event)

    # command threads
    command_thread = threading.Thread(target=handle_commands, daemon=True)
    command_thread.start()

    # Keep the main thread alive
    command_thread.join()
    # monitor_thread.join()

def refresh_threads():
    display_thread = threading.Thread(target=periodic_display_screen, daemon=True)
    display_thread.start()
     
def startup():
    # On start up do this
    clear_screen()
    print('Launching RAM Watcher - Jay steele')
    time.sleep(1)
    # Call the function
    print_graphic(graphic)
    time.sleep(1)
    clear_screen()
    display_screen(False, True)



