from pathlib import Path
from datetime import datetime

# resolve path relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = BASE_DIR / "screenshots"
# ensures the directory exists
SCREENSHOT_DIR.mkdir(exist_ok=True) 

# take screenshots and save in date_time_name format
def take_screenshot(driver, name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filepath = SCREENSHOT_DIR / f"{timestamp}_{name}.png"

    driver.save_screenshot(str(filepath))

    print(f"Screenshot saved: {filepath}")

# clear old screenshots from the screenshot folder everytime the script runs
def clear_old_screenshots():
    for screenshot in SCREENSHOT_DIR.glob("*.png"):
        screenshot.unlink()
        