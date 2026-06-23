import time
import requests
import re
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from screenshot_manager import take_screenshot, clear_old_screenshots
from video_recorder import start_recording, stop_recording, clear_old_recording

clear_old_screenshots()

clear_old_recording()

# launch chrome browser and open the registrtion (sign up) site
driver = webdriver.Chrome()

start_recording(driver)

driver.maximize_window()
driver.get("https://authorized-partner.vercel.app/")

print("Opening Website.....")

wait = WebDriverWait(driver, 10)

# base URL for Mail.tm temporary email service
MAIL_TM_API = "https://api.mail.tm"

print("Creating temporary email.....")

# define mailbox
def create_mailbox():
    # fetch available email domain from Mail.tm
    domains = requests.get(f"{MAIL_TM_API}/domains").json()

    active_domain = None

    # find the first active domain
    for domain in domains["hydra:member"]:
        if domain["isActive"]:
            active_domain = domain["domain"]
            break

    if not active_domain:
        raise Exception("No active domain found")
    
    # use timestamp to generate a unique email address and password
    stamp = str(int(time.time()))

    address = f"qaauth{stamp}@{active_domain}"
    password = f"Mail{stamp}!aA1"

    # create temporary mailbox account
    requests.post(
        f"{MAIL_TM_API}/accounts",
        json={
            "address" : address,
            "password" : password
        }
    )

    # authenticate and obtain access token for mailbox operations
    token_response = requests.post(
        f"{MAIL_TM_API}/token",
        json={
            "address" : address,
            "password" : password
        }
    ).json()

    return {
        "address" : address,
        "password" : password,
        "token" : token_response["token"]
    }

# def 
def wait_for_email(token, timeout = 120):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    start_time = time.time()

    # poll mailbox every 5 seconds until email arrives
    while time.time() - start_time < timeout:
        response = requests.get(
            f"{MAIL_TM_API}/messages",

            headers=headers
        )

        messages = response.json()

        # return the latest email once available
        if messages["hydra:member"]:
            return messages["hydra:member"][0]
        
        print("Waiting for email.....")

        time.sleep(5)

    raise TimeoutError("No email received withing timeout period")

# create mailbox
mailbox = create_mailbox()

print("Temporary Email: ", mailbox["address"])

# take screenshot of the page after filling in the details, before clicking the Next Button
take_screenshot(driver, "registration_page")

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

# take screenshot of the page after filling in the details, before clicking the Next Button
take_screenshot(driver, "register")

# wait for Continue button
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Continue')]")
    )
).click()

print("Continue clicked.....")

# ---------------------personal details----------------------------
# generate unique Nepal-format mobile number
stamp = str(int(time.time() * 1000))[-8:]
phone_number = f"85{stamp}"[:10]

user_data = {
    "firstName": "Kim",
    "lastName": "Namjoon",
    "email": mailbox["address"],    #dynamic email
    "phoneNumber": phone_number,    #dynamic Nepal-format mobile number
    "password": "Test@12345",
    "confirmPassword": "Test@12345"
}

# populate personal details form using the dictionary values
for field_name, value in user_data.items():
    wait.until(
        EC.visibility_of_element_located(
            (By.NAME, field_name)
        )
    ).send_keys(value)

print("Personal Details filled.....")

# take screenshot of the page after filling in the details, before clicking the Next Button
take_screenshot(driver, "personal_details")

# wait for Next buttom
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Next')]")
    )
).click()

print("Next button that leads to Agency Details section clicked.....")

message = wait_for_email(mailbox["token"])

print("Verification email received...")

# retrieve complete email content
email_data = requests.get(
    f"{MAIL_TM_API}/messages/{message['id']}",
    headers={
        "Authorization": f"Bearer {mailbox['token']}"
    }
).json()

print("Extracting OTP.....")

# extract first 6-digit OTP from the email body
otp_match = re.search(r"\b\d{6}\b", email_data["text"])

if not otp_match:
    raise Exception("OTP not found in email.")

otp_code = otp_match.group()

print("OTP: ", otp_code)

# enter the oTP
wait.until(
    EC.visibility_of_element_located(
        (By.CSS_SELECTOR, 'input[data-input-otp="true"]')
    )
).send_keys(otp_code)

print("OTP code filled in.....")

# take screenshot of the page after filling in the details, before clicking the Next Button
take_screenshot(driver, "email_verification")

# enter Verify Code
wait.until(
    EC.visibility_of_element_located(
        (By.XPATH, "//button[contains(text(), 'Verify Code')]")
    )
).click()

print("Verify button clicked.....")

# -----------------------agency details---------------------------
agency_data = {
    "agency_name" : "Global Data Corporation",
    "role_in_agency" : "Data Analyst",
    "agency_email" : "datacorp@global.com",
    "agency_website" : "www.globaldatacorporation.com",
    "agency_address" : "Baneshwor"
}

region = "Nepal"

# filling in the values in agency details section
for field_name, value in agency_data.items():
    wait.until(
        EC.visibility_of_element_located(
            (By.NAME, field_name)
        )
    ).send_keys(value)

# open Region of Operation dropdown
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[@role='combobox']")
    )
).click()

# select region
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, f"//span[text()='{region}']")
    )
).click()

print(" Nepal Region selected from dropdown")

# take screenshot of the page after filling in the details, before clicking the Next Button
take_screenshot(driver, "agency_details")

# wait for Next Button
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Next')]")
    )
).click()


print("Next button that leads to Professional Experience Section clicked.....")

# --------------------------Professional Experience----------------------
experience_data = {
    "number_of_students_recruited_annually" : "750",
    "focus_area" : "Undergraduate, Graduate, Doctorate",
    "success_metrics" : "95%"
}

# yoe = years of experience
yoe = "7 years"

print(" 7 years selected for years of experience dropdown.....")

# open Years of Experience dropdown
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[@role='combobox']")
    )
).click()

# select years of experience
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, f"//*[text()='{yoe}']")
    )
).click()

# filling in the values in personal experience section
for field_name, value in experience_data.items():
    wait.until(
        EC.visibility_of_element_located(
            (By.NAME, field_name)
        )
    ).send_keys(value)

# select service provided, checkbox
# using list for selecting multiple services
services_provided = [
    "Career Counseling",
    "Admission Applications",
    "Test Prepration"
]

# checking in the services provided
for service in services_provided:
    wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH, f"//label[text()='{service}']/preceding-sibling::button"
            )
        )
    ).click()

print("select services.....")

# take screenshot of the page after filling in the details, before clicking the Next Button
take_screenshot(driver, "professional_experience")

# wait for Next Button
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Next')]")
    )
).click()

print("Next button that leads to Verifictaion and Preferences section clicked.....")

# ------------------------------Verification and Preferences---------------------
verification_data = {
    "business_registration_number" : "87B125876",
    "certification_details" : "ICEF Certified Education Agent"
}

countries = ["Australia", "Canada", "India", "Nepal", "France", "United Kingdom", "United States of America"]

# filling in the values in verification and preferences section
for field_name, value in verification_data.items():
    wait.until(
        EC.visibility_of_element_located(
            (By.NAME, field_name)
        )
    ).send_keys(value)

# multi-select preferred countries
for country in countries:
    # open Preferred Countries dropdown
    dropdown = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@role='combobox']")
        )
    )
    
    dropdown.click()

    # select countries
    option = wait.until(
        EC.element_to_be_clickable(
            ( By.XPATH,f"//div[span[normalize-space()='{country}']]")
        )
    )

    driver.execute_script("arguments[0].click();", option)

print(" select country from dropdown.....")

# select Preferred Institution Types
institution_types = ["Universities", "Colleges"]

# checking in Institution Types
for institution in institution_types:
    wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH, f"//label[text()='{institution}']/preceding-sibling::button"
            )
        )
    ).click()

print(" select institutions.....")

# resolve PDF path relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "documents" / "QA Intern Task.pdf"

# upload supporting business document
upload_input = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@type='file']")
    )
)

upload_input.send_keys(str(file_path))

# take screenshot of the page after filling in the details, before clicking the Next Button
take_screenshot(driver, "verification_preferences")

# wait for Submit Button
# submit the completed application form
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Submit')]")
    )
).click()

# take screenshot of the page after filling in the details, before clicking the Next Button
take_screenshot(driver, "verification_preferences")

print("Submit button clicked.....")

# wait for profile page
wait.until(
    EC.url_contains("/admin/profile")
)

wait.until(
    lambda current_driver: current_driver.execute_script("return document.readyState") == "complete"
)

wait.until(
    lambda current_driver: any(
        profile_text in current_driver.find_element(By.TAG_NAME, "body").text
        for profile_text in [
            user_data["firstName"],
            user_data["lastName"],
            agency_data["agency_name"],
            user_data["email"],
        ]
    )
)

time.sleep(2)

# take screenshot of the admin profile page after successful registration
take_screenshot(driver, "profile_page")

print(".....Registration Completed. Account has been created Successfully.....")

stop_recording()

driver.quit()
