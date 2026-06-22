import time
import requests
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("Opening Website.....")

driver = webdriver.Chrome()

driver.maximize_window()
driver.get("https://authorized-partner.vercel.app/")

wait = WebDriverWait(driver, 10)

MAIL_TM_API = "https://api.mail.tm"

print("Creating temporary email.....")

# define mailbox
def create_mailbox():
    domains = requests.get(f"{MAIL_TM_API}/domains").json()

    active_domain = None

    for domain in domains["hydra:member"]:
        if domain["isActive"]:
            active_domain = domain["domain"]
            break

    if not active_domain:
        raise Exception("No active domain found")
    
    stamp = str(int(time.time()))

    address = f"qaauth{stamp}@{active_domain}"
    password = f"Mail{stamp}!aA1"

    requests.post(
        f"{MAIL_TM_API}/accounts",
        json={
            "address" : address,
            "password" : password
        }
    )

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

    while time.time() - start_time < timeout:
        response = requests.get(
            f"{MAIL_TM_API}/messages",

            headers=headers
        )

        messages = response.json()

        if messages["hydra:member"]:
            return messages["hydra:member"][0]
        
        print("Waiting for email.....")

        time.sleep(5)

    raise TimeoutError("No email received withing timeout period")

# create mailbox
mailbox = create_mailbox()

print("Temporary Email: ", mailbox["address"])

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

# personal details 
user_data = {
    "firstName": "Kim",
    "lastName": "Namjoon",
    "email": mailbox["address"],    #dynamic email
    "phoneNumber": "9841232456",    #send_keys() expects a string
    "password": "Test@12345",
    "confirmPassword": "Test@12345"
}

for field_name, value in user_data.items():
    wait.until(
        EC.visibility_of_element_located(
            (By.NAME, field_name)
        )
    ).send_keys(value)

print("personal details filled.....")

# wait for Next buttom
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Next')]")
    )
).click()

print("Next button clicked.....")

message = wait_for_email(mailbox["token"])

print("Verification email received...")

email_data = requests.get(
    f"{MAIL_TM_API}/messages/{message['id']}",
    headers={
        "Authorization": f"Bearer {mailbox['token']}"
    }
).json()

print("Extracting OTP.....")

# extract otp
otp_match = re.search(r"\b\d{6}\b", email_data["text"])

otp_code = otp_match.group()

print("OTP: ", otp_code)

# enter the oTP
wait.until(
    EC.visibility_of_element_located(
        (By.CSS_SELECTOR, 'input[data-input-otp="true"]')
    )
).send_keys(otp_code)

print("OTP code filled in.....")

# enter Verify Code
wait.until(
    EC.visibility_of_element_located(
        (By.XPATH, "//button[contains(text(), 'Verify Code')]")
    )
).click()

print("Verify button clicked.....")

input("Press Enter to close the browser.....")
driver.quit()