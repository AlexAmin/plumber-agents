# PowerPoint Automation Script

## Overview
This script automates opening Microsoft PowerPoint on macOS, creates a new presentation, and types text by clicking in the center of the screen.

## Files
- `powerpoint_automation.py` - New simplified script (recommended)
- `main.py` - Original script (deprecated)

## Issues Fixed

### Original Error
```
AttributeError: module 'pygetwindow' has no attribute 'getAllWindows'
```

### Root Cause
The `pygetwindow` library has limited support on macOS. The method `getAllWindows()` doesn't exist on macOS - only `getAllTitles()` is available, and even that has limited functionality.

### Solution
Replaced `pygetwindow` dependency entirely with AppleScript, which is the native macOS automation technology. This provides:
- More reliable process detection
- Better window activation
- Native macOS integration
- No dependency on third-party libraries with limited macOS support

## How It Works (New Script)

### Step 1: Launch PowerPoint
```python
subprocess.run(["open", "-a", "Microsoft PowerPoint"])
```
Uses macOS `open` command to launch PowerPoint.

### Step 2: Wait for PowerPoint to be Ready
```python
def wait_for_powerpoint(timeout=30):
    # Uses AppleScript to check if PowerPoint process exists
    script = '''
    tell application "System Events"
        return (name of processes) contains "Microsoft PowerPoint"
    end tell
    '''
```
Polls every 0.5 seconds with a 30-second timeout to detect when PowerPoint is running. Includes extra 3-second wait for full initialization.

### Step 3: Bring PowerPoint to Front
```python
def bring_powerpoint_to_front():
    # Uses AppleScript to bring PowerPoint to front
    script = '''
    tell application "Microsoft PowerPoint"
        activate
    end tell
    '''
```
Ensures PowerPoint is the active application before sending keyboard commands.

### Step 4: Create New Presentation with CMD+N
```python
pyautogui.hotkey('command', 'n')
```
Simulates the CMD+N keyboard shortcut to create a new presentation. Waits 3 seconds for the new presentation to load.

### Step 5: Click in Center of Screen
```python
screen_width, screen_height = pyautogui.size()
center_x = screen_width // 2
center_y = screen_height // 2
pyautogui.click(center_x, center_y)
```
Gets screen dimensions and clicks in the exact center. This ensures the cursor is positioned in the text box, even if auto-focus didn't work.

### Step 6: Type Text
```python
pyautogui.write('Hello World', interval=0.1)
```
Types the text with a 0.1-second delay between characters.

## Requirements

### Python Packages
```bash
pip install pyautogui
```

### System Requirements
- macOS (uses AppleScript)
- Microsoft PowerPoint installed
- Python 3.x

### Permissions
You may need to grant accessibility permissions:
1. System Preferences > Security & Privacy > Privacy
2. Select "Accessibility" from the left sidebar
3. Add your terminal or Python to the allowed apps

## Usage

```bash
python powerpoint_automation.py
```

Or make it executable:
```bash
chmod +x powerpoint_automation.py
./powerpoint_automation.py
```

## Expected Behavior

1. Script launches PowerPoint
2. Waits up to 30 seconds for PowerPoint to be ready
3. Brings PowerPoint window to front
4. Sends CMD+N to create a new presentation
5. Waits for presentation to fully load
6. Clicks in the center of the screen to ensure cursor is in text box
7. Types "Hello World" character by character

## Troubleshooting

### PowerPoint doesn't activate
- Ensure PowerPoint is installed in /Applications
- Check that you have accessibility permissions enabled

### CMD+N doesn't create new presentation
- Increase the sleep time after bringing PowerPoint to front
- Make sure no modal dialogs are blocking PowerPoint
- Try running the script when PowerPoint is not already open

### Text doesn't appear
- The script clicks in the center of the screen - make sure PowerPoint window is maximized or at least centered
- Increase the sleep time after clicking
- Check accessibility permissions

### Timeout error
- Increase the timeout parameter in `wait_for_powerpoint(timeout=30)` if your system is slow
- Check if PowerPoint is installed correctly

## Key Features of New Script

1. **Clean slate approach** - Completely rewritten for simplicity
2. **AppleScript for detection** - Uses native macOS APIs to detect PowerPoint
3. **CMD+N keyboard shortcut** - Simulates the standard new presentation command
4. **Center click strategy** - Clicks in center of screen to ensure cursor placement
5. **Verbose logging** - Each step prints clear status messages
6. **Better error handling** - Try/except blocks with meaningful error messages
7. **Proper timeouts** - All subprocess calls have 5-second timeouts to prevent hanging
8. **Clear step-by-step flow** - 6 well-defined steps that are easy to debug

## Future Enhancements

Possible improvements:
- Add command-line arguments for custom text
- Support for multiple slides
- Error recovery (retry logic)
- Cross-platform support (Windows/Linux)
- Image insertion
- Slide formatting options