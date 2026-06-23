# Task Overview:

Automate the signup process on the following site:
https://authorized-partner.vercel.app/

The project uses Selenium and a disposable 'mail.tm' inbox to retrieve the email OTP automatically. 
No manual action is required during the signup flow.

## Prerequisites:
- Python 3.12 or any compatible Python version
- Selenium
- Google Chrome
- Internet access to:
    - https://authorized-partner.vercel.app/
    - https://api.mail.tm

## Run
python signup_automation_script.py

To generate report:
pip install pytest   
pip install pytest-html  
pytest src/signup_automation_script.py \ --html=reports/report.html

## Environment

- Language: Python 3.12
- Selenium: 4.32.2
- Chrome: Latest
- OS: Windows 11

## Test Data

The script generates unique data for email.
- Email: disposable 'mail.tm' account, generated at run time, right after opening the link and before further processing.

## Notes

- The site requires email OTP verification.
The automation creates a disposable inbox, polls for the OTP email, extacts the six-digit code, and submits it.

- The final signup page requires at least one uploaded document.

- Successful registration completion is verified by navigation to the site profile page.