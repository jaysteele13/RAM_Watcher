import psutil
import time
from plyer import notification
import threading
from datetime import datetime, timedelta
from constants import GREEN, RESET, APPLICATION_NAME
from queue import Queue
from exp_save_var import load_config
import os

# Store the current memory usage data
memory_usage_data = {}
storage_usage_data = {}
# Default threshold in MB
threshold = 1255
notificationToggle= True
watcherToggle = True
interval = 600 # 30 MINS
total_memory = 0
refresh_rate = 10

load_config()

def get_refresh_rate():
    return refresh_rate

def set_refresh_rate(rate: int):
    global refresh_rate
    refresh_rate = rate

def set_interval(time: int):
    global interval
    interval = time


def get_interval():
    return interval

def set_threshold(memory):
    global threshold
    threshold = memory


def get_threshold():
    return threshold

def set_watcher(toggle):
    global watcherToggle
    watcherToggle = toggle


def get_watcher():
    return watcherToggle

def set_notification(toggle):
    global notificationToggle
    notificationToggle = toggle


def get_notification():
    return notificationToggle

# Function to monitor memory usage
memory_lock = threading.Lock()
notification_lock = threading.Lock()

# default 10 second refresh
def monitor_memory_and_storage(queue: Queue, app_name=APPLICATION_NAME):

    # globals
    global memory_usage_data
    global storage_usage_data

    # split up notification time
    last_notification_time = datetime.now() - timedelta(seconds=get_interval())


    while get_watcher():
        total_memory = 0
        total_disk_usage = 0
        # Iterate over all processes to find the target application
        app_paths = []

        # Calculate memory usage
        for proc in psutil.process_iter(['name', 'memory_info', 'exe']):
            if proc.info['name'] == app_name:
                memory_usage = proc.info['memory_info'].rss / (1024 * 1024) * 0.9  # Convert to MB and adjust
                total_memory += memory_usage
                app_path = proc.info['exe']
                if app_path:
                    # need this to get path to find ssd usage
                    app_dir = os.path.dirname(app_path)
                    print(f"Found {app_name} process at path: {app_path}")
                    app_paths.append(app_dir)
                

        total_memory *= 0.6

            # Calculate disk usage for the specified paths related to the app
        # Calculate disk usage for the directories associated with the app
        for path in app_paths:
            try:
                disk_usage = psutil.disk_usage(path)
                print(f"Total Disk usage for {path}: {disk_usage.used / (1024 * 1024):.2f} MB")
                print(f"Disk usage for per m/s: {disk_usage.used / (1024 * 1024):.2f} MB")
            except FileNotFoundError:
                print(f"Path {path} not found.")
            except PermissionError:
                print(f"Permission denied for accessing {path}.")
            except NotADirectoryError:
                print(f"Path {path} is not a directory.")
            except Exception as e:
                print(f"An error occurred: {e}")

        # Safely update the global memory_usage_data using a lock
        with memory_lock:
            memory_usage_data[app_name] = round(total_memory)
            storage_usage_data[app_name] = round(total_disk_usage)
            queue.put(memory_usage_data[app_name])
            # queue.put(storage_usage_data[app_name])
            
        # Print total memory and storage usage
        print(f"Total Memory Usage: {total_memory:.2f} MB")
        print(f"Total Storage Usage: {total_disk_usage:.2f} MB")
                
        # Check if total memory usage exceeds the threshold
        if get_notification() and (total_memory)> threshold:
            current_time = datetime.now()
            
            with notification_lock:
                # Send a desktop notification
                if current_time >= last_notification_time + timedelta(seconds=get_interval()):
                    notification.notify(
                        title=f"High Memory Usage Alert: {app_name}",
                        message=f"Total memory usage is {total_memory:.2f} MB, exceeding the threshold of {threshold} MB!",
                        app_name="Monitor Ram",
                        app_icon='C:\\Users\\jayst\\Documents\\Code\\Jay_Having_fun\\RAM_Watcher\\braveIcon.ico',
                        timeout=5
                    )
                    last_notification_time = current_time
                    print(f"{GREEN}ALERT{RESET}: {app_name} memory usage was above {threshold} MB!")
                   
        # Wait for the next check
        time.sleep(get_refresh_rate())


import psutil
import time

def get_disk_io_rate(interval=1):
    """
    Measure the disk I/O rate (read and write speed) in MB/s over a specified interval.

    Args:
    - interval (float): Time interval in seconds over which to measure the rate.

    Returns:
    - read_speed (float): Disk read speed in MB/s.
    - write_speed (float): Disk write speed in MB/s.
    """
    # Get initial disk I/O counters
    io_counters_start = psutil.disk_io_counters()
    
    # Wait for the specified interval
    time.sleep(interval)
    
    # Get disk I/O counters after the interval
    io_counters_end = psutil.disk_io_counters()
    
    # Calculate the difference in read and write bytes
    read_bytes = io_counters_end.read_bytes - io_counters_start.read_bytes
    write_bytes = io_counters_end.write_bytes - io_counters_start.write_bytes
    
    # Convert bytes per second to MB/s
    read_speed = read_bytes / (1024 * 1024 * interval)  # MB/s
    write_speed = write_bytes / (1024 * 1024 * interval)  # MB/s
    
    return read_speed, write_speed

# Measure and display disk usage rate in real-time
try:
    while True:
        read_speed, write_speed = get_disk_io_rate(interval=1)
        print(f"Read Speed: {read_speed:.2f} MB/s, Write Speed: {write_speed:.2f} MB/s")
except KeyboardInterrupt:
    print("Stopped monitoring disk usage.")
