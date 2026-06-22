import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

driver.maximize_window()
driver.get("https://authorized-partner.vercel.app/")

wait = WebDriverWait(driver, 10)

print("Opening Website.....")

# wait for Get Started button
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Get Started')]")
    )
).click()

print("Get Started button clicked.....")

# wait for checkbox
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[@id='remember']")
    )
).click()

print("Checkbox clicked.....")

# wait for Continue button
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Continue')]")
    )
).click()

print("Continue clicked.....")

# keeps browser open for 10 seconds
time.sleep(10)

input("Press Enter to close the browser.....")
driver.quit()