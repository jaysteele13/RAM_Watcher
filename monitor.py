import psutil
import time
from plyer import notification
import threading
from constants import APPLICATION_NAME
from datetime import datetime, timedelta
from constants import RED, RESET

# Store the current memory usage data
memory_usage_data = {}
# Default threshold in MB
threshold = 1250  
notificationToggle= True
watcherToggle = True
interval = 1200 # 30 MINS
total_memory = 0
refresh_rate = 10

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
def monitor_memory(app_name=APPLICATION_NAME):
    global memory_usage_data
    last_notification_time = datetime.now() - timedelta(seconds=get_interval())


    while watcherToggle:
        total_memory = 0

        # Calculate memory usage
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'status']):
            if proc.info['name'] == app_name:
                memory_usage = proc.info['memory_info'].rss / (1024 * 1024) * 0.9  # Convert to MB and adjust
                total_memory += memory_usage

        total_memory *= 0.6

        # Safely update the global memory_usage_data using a lock
        with memory_lock:
            memory_usage_data[app_name] = round(total_memory)
        
        # Check if total memory usage exceeds the threshold
        if notificationToggle and (total_memory)> threshold:
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
                    print(f"{RED}ALERT{RESET}: {app_name} memory usage is above {threshold} MB!")
                   
        # Wait for the next check
        time.sleep(get_refresh_rate())


