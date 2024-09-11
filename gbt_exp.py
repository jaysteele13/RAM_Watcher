import keyboard
import threading
import os
import re
from art import *
import queue
from monitor import *
import ctypes
from constants import APPLICATION_NAME, RED, RESET, BLUE, GREEN
import curses
import time

# Queue for communication between threads
command_queue = queue.Queue()

def get_refresh_rate():
    return refresh_rate

def set_refresh_rate(rate: int):
    global refresh_rate
    refresh_rate = rate

# Initialize variables
current_process = None
help = False
memory = None
timeout_duration = 1200
refresh_rate = 15
last_capslock_event_time = 0
debounce_interval = 0.5

# Set initial defaults
set_threshold(1250)
set_interval(1200)
set_watcher(True)
set_notification(True)

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

def dictToInt(memory):
    memory_usage_str = str(memory)
    match = re.search(r'\d+', memory_usage_str)
    if match:
        return float(match.group())
    else:
        return "Retrieving RAM"

def returnToggle(toggle):
    return "On" if toggle else "Off"

def display_timer(interval):
    return f"{int(interval/60)} min" if interval == 60 else f"{int(interval/60)} mins"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_screen(stdscr, help=False, startup=False):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    stdscr.clear()
    curses.curs_set(1)
    stdscr.keypad(True)

    height, width = stdscr.getmaxyx()

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
        "RAM used: (your message)",
        "Threshold: (t)",
        "Application: (a)",
        "Notifications: (n)",
        "Timer: (ns)"
    ]

    while True:
        stdscr.clear()
        dynamic_content = create_separator(homeTitle, *homeLines) if not help else create_separator(helpTitle, *helpLines)
        for idx, line in enumerate(dynamic_content.splitlines()):
            stdscr.addstr(idx, 0, line)

        stdscr.addstr(height - 3, 0, "CAPS LOCK for help / clear", curses.color_pair(1))
        stdscr.addstr(height - 2, 0, "e to quit gracefully...", curses.color_pair(2))

        stdscr.refresh()

        curses.echo()
        user_input = stdscr.getstr(height - 1, 0).decode("utf-8").strip()
        curses.noecho()

        if user_input.lower() == 'e':
            break
        elif user_input.lower() == 'caps lock':
            help = not help
        elif user_input.lower() == 'clear':
            help = False
            startup = False

        time.sleep(0.1)

def is_terminal_focused():
    active_window_handle = ctypes.windll.user32.GetForegroundWindow()
    window_title = ctypes.create_string_buffer(512)
    ctypes.windll.user32.GetWindowTextA(active_window_handle, window_title, 512)

    terminal_titles = [b"Python", b"cmd", b"Terminal", b"Windows PowerShell", b"RAM_Watcher"]
    return any(title in window_title.value for title in terminal_titles)

def handle_capslock_event(e):
    global help
    global last_capslock_event_time

    current_time = time.time()
    if (current_time - last_capslock_event_time) < debounce_interval:
        return

    if is_terminal_focused():
        help = not help
        curses.wrapper(display_screen)

    last_capslock_event_time = current_time

def handle_commands():
    while True:
        command = input("").strip().lower()
        if command == "e":
            command_queue.put(f"Exiting the program {GREEN}GRACEFULLY{RESET}.")
            os._exit(0)
        elif command == "ur a bitch":
            command_queue.put("Standard Refresh rate is 15 seconds, do you really want to change that? y/n")
            response = input("").strip().lower()
            if response == 'y':
                command_queue.put("Are you sure? (Type: 'aye mate would ye fuck up')")
                if input("").strip().lower() == 'aye mate would ye fuck up':
                    command_queue.put("Select a time in seconds to refresh RAM here")
                    number = input("")
                    change_number_validation(number, set_refresh_rate)
        elif command == "o":
            command_queue.put("Toggling RAM_Watcher")
            set_watcher(not get_watcher())
        elif command == "t":
            command_queue.put(f"What would you like to change the {GREEN}threshold{RESET} ({get_threshold()}) to: ")
            number = input("")
            change_number_validation(number, set_threshold)
        elif command == "a":
            command_queue.put("This doesn't change.")
        elif command == "n":
            command_queue.put("Toggling Notification")
            set_notification(not get_notification())
        elif command == "ns":
            command_queue.put(f"What would you like to change the {GREEN}timer{RESET} ({display_timer(get_interval())}) to (min): ")
            number = input("")
            change_number_validation(number, set_interval)
        elif command == "":
            command_queue.put("That's an empty command!")
        else:
            command_queue.put(f"Unknown command: {command}")

        time.sleep(0.5)

        curses.wrapper(display_screen)

def run_threads():
    keyboard.on_press_key("caps lock", handle_capslock_event)
    command_thread = threading.Thread(target=handle_commands, daemon=True)
    command_thread.start()
    command_thread.join()

def startup():
    clear_screen()
    print('Launching RAM Watcher')
    time.sleep(1)
    print_graphic(graphic)
    time.sleep(1)
    clear_screen()
    curses.wrapper(display_screen)

if __name__ == "__main__":
    startup()
    run_threads()
