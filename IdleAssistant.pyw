import pyautogui
import keyboard
import random
import time
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image
import os
import sys

pyautogui.FAILSAFE = False

app_running = True
active = False
activity_start_time = 0.0

START_DELAY = 5.0
MOVE_TOLERANCE = 5

action_lock = threading.Lock()
expected_pos = None

def resource_path(name):
    """Resolve a bundled resource path (works with PyInstaller onefile)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

def activity_allowed():
    """True once activity is started and the start delay has elapsed."""
    return active and (time.time() - activity_start_time) >= START_DELAY

def random_mouse_movement():
    """Randomly move the mouse while activity is allowed."""
    global expected_pos
    screen_width, screen_height = pyautogui.size()
    while app_running:
        if not activity_allowed():
            time.sleep(0.2)
            continue
        x = random.randint(0, screen_width - 1)
        y = random.randint(0, screen_height - 1)
        with action_lock:
            if not activity_allowed():
                continue
            pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.5))
            expected_pos = pyautogui.position()
        time.sleep(random.uniform(1, 5))

def random_alt_tab():
    """Randomly perform Alt+Tab while activity is allowed."""
    while app_running:
        if not activity_allowed():
            time.sleep(0.2)
            continue
        pyautogui.hotkey('alt', 'tab')
        time.sleep(random.uniform(10, 30))

def random_ctrl_tab():
    """Randomly perform Ctrl+Tab while activity is allowed."""
    while app_running:
        if not activity_allowed():
            time.sleep(0.2)
            continue
        pyautogui.hotkey('ctrl', 'tab')
        time.sleep(random.uniform(15, 45))

def random_keystrokes():
    """Randomly perform keystrokes while activity is allowed."""
    keys = ['a', 's', 'd', 'f', 'q', 'w', 'e', 'r', 't', 'y', '1', '2', '3', '4', 'space']
    while app_running:
        if not activity_allowed():
            time.sleep(0.2)
            continue
        pyautogui.press(random.choice(keys))
        time.sleep(random.uniform(5, 15))

def random_left_click():
    """Randomly perform left mouse clicks while activity is allowed."""
    global expected_pos
    screen_width, screen_height = pyautogui.size()
    while app_running:
        if not activity_allowed():
            time.sleep(0.2)
            continue
        x = random.randint(0, screen_width - 1)
        y = random.randint(0, screen_height - 1)
        with action_lock:
            if not activity_allowed():
                continue
            pyautogui.click(x, y)
            expected_pos = pyautogui.position()
        time.sleep(random.uniform(2, 5))

def monitor_user_move(icon):
    """Stop activity if the user moves the mouse after activity started."""
    global active
    while app_running:
        if activity_allowed() and expected_pos is not None:
            if action_lock.acquire(timeout=0.5):
                try:
                    current = pyautogui.position()
                    moved = (abs(current[0] - expected_pos[0]) > MOVE_TOLERANCE or
                             abs(current[1] - expected_pos[1]) > MOVE_TOLERANCE)
                    if moved:
                        active = False
                        try:
                            icon.notify("Activity stopped (mouse moved)", "Idle Assistant")
                        except Exception:
                            pass
                finally:
                    action_lock.release()
        time.sleep(0.2)

def monitor_exit(icon):
    """Monitor for the ESC key press to exit the application."""
    global app_running, active
    while app_running:
        if keyboard.is_pressed('esc'):
            active = False
            app_running = False
            icon.stop()
            break
        time.sleep(0.1)

def start_activity(icon, item):
    """Start activity; it begins after START_DELAY seconds."""
    global active, activity_start_time, expected_pos
    expected_pos = None
    activity_start_time = time.time()
    active = True
    try:
        icon.notify("Activity starts in 5 seconds", "Idle Assistant")
    except Exception:
        pass

def stop_activity(icon, item):
    """Stop activity but keep the tray icon running."""
    global active
    active = False

def exit_app(icon, item):
    """Stop everything and exit the application."""
    global app_running, active
    active = False
    app_running = False
    icon.stop()

def setup_tray_icon():
    """Create a system tray icon."""
    icon_image = Image.open(resource_path("icon.ico"))

    menu = Menu(
        MenuItem('Start', start_activity, enabled=lambda item: not active),
        MenuItem('Stop', stop_activity, enabled=lambda item: active),
        MenuItem('Exit', exit_app)
    )

    return Icon("Idle Assistant", icon_image, "Idle Assistant", menu)

def start_background_tasks(icon):
    """Start all background worker threads."""
    targets = [
        (random_mouse_movement, ()),
        (random_alt_tab, ()),
        (random_ctrl_tab, ()),
        (random_keystrokes, ()),
        (random_left_click, ()),
        (monitor_user_move, (icon,)),
        (monitor_exit, (icon,)),
    ]
    for target, args in targets:
        threading.Thread(target=target, args=args, daemon=True).start()

def main():
    tray_icon = setup_tray_icon()
    start_background_tasks(tray_icon)
    tray_icon.run()

if __name__ == "__main__":
    main()
