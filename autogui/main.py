#!/usr/bin/env python3
"""
PowerPoint Automation Script
Opens PowerPoint, creates a new presentation, and types text in the center.
"""

import pyautogui
import time
import subprocess
import sys

def wait_for_powerpoint(timeout=30):
    """
    Wait for PowerPoint to be running and ready.
    Returns True if PowerPoint is detected, False if timeout.
    """
    print("Waiting for PowerPoint to be ready...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Check if PowerPoint process is running
            script = '''
            tell application "System Events"
                return (name of processes) contains "Microsoft PowerPoint"
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.stdout.strip() == "true":
                print("PowerPoint is running!")
                return True

        except Exception as e:
            print(f"Error checking PowerPoint: {e}")

        time.sleep(0.5)

    return False

def bring_powerpoint_to_front():
    """Activate PowerPoint window."""
    print("Activating PowerPoint window...")
    try:
        script = '''
        tell application "Microsoft PowerPoint"
            activate
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True, timeout=5)
        time.sleep(1)  # Wait for activation
        return True
    except Exception as e:
        print(f"Error activating PowerPoint: {e}")
        return False

def main():
    print("=" * 50)
    print("PowerPoint Automation Script")
    print("=" * 50)

    # Step 1: Open PowerPoint
    print("\n[Step 1] Opening PowerPoint...")
    subprocess.run(["open", "-a", "Microsoft PowerPoint"])

    # Step 2: Wait for PowerPoint to be ready
    print("\n[Step 2] Waiting for PowerPoint to be ready...")
    if not wait_for_powerpoint(timeout=30):
        print("ERROR: Timed out waiting for PowerPoint.")
        sys.exit(1)

    # Give PowerPoint extra time to fully initialize
    print("Giving PowerPoint time to fully initialize...")
    time.sleep(3)

    # Step 3: Bring PowerPoint to front
    print("\n[Step 3] Bringing PowerPoint to front...")
    if not bring_powerpoint_to_front():
        print("ERROR: Could not activate PowerPoint.")
        sys.exit(1)

    # Step 4: Create new presentation with CMD+N
    print("\n[Step 4] Creating new presentation (CMD+N)...")
    pyautogui.hotkey('command', 'n')
    print("Sent CMD+N, waiting for new presentation to load...")
    time.sleep(3)  # Wait for new presentation to appear

    # Step 5: Get screen size and click in center
    print("\n[Step 5] Clicking in center of screen...")
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2

    print(f"Screen size: {screen_width}x{screen_height}")
    print(f"Clicking at: ({center_x}, {center_y})")

    pyautogui.click(center_x, center_y)
    time.sleep(0.5)  # Wait for click to register

    # Step 6: Type the text
    print("\n[Step 6] Typing 'Hello World'...")
    pyautogui.write('Hello World', interval=0.1)

    print("\n" + "=" * 50)
    print("Script completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)