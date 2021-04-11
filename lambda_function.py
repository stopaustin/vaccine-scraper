# Resources on connecting to Selenium in Lambda:
# https://manivannan-ai.medium.com/python-selenium-on-aws-lambda-b4b9de44b8e1
# https://stackoverflow.com/questions/65429877/aws-lambda-container-running-selenium-with-headless-chrome-works-locally-but-not/65635150#65635150?newreg=0f00d8b26b244cb38a7b6c052568ca80
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os
import time
import requests
import pytz
import shutil
import csv

BIN_DIR = "/tmp/bin"
CURR_BIN_DIR = os.getcwd() + "/bin"

IFTTT_KEY = os.environ.get('IFTTT_KEY')
IFTTT_URL = "https://maker.ifttt.com/trigger/notifier/with/key/" + IFTTT_KEY
tz_IL=pytz.timezone('America/Chicago')

ZIP_CODES = os.environ.get('ZIP_CODES')
TEXT_QUERY = "Appointments unavailable"

# Moves binaries to /tmp/bin to grant Lambda execution privileges
def _init_bin(executable_name):
    if not os.path.exists(BIN_DIR):
        os.makedirs(BIN_DIR)

    print("Copying binaries for " + executable_name + " in /tmp/bin")

    currfile = os.path.join(CURR_BIN_DIR, executable_name)
    newfile = os.path.join(BIN_DIR, executable_name)

    shutil.copy2(currfile, newfile)

    print("Giving new binaries permissions for lambda")

    os.chmod(newfile, 0o775)

def lambda_handler(event, context):

    _init_bin("headless-chromium")
    _init_bin("chromedriver")

    # Set up driver
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    # chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    # chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument('--homedir=/tmp')
    # chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
    chrome_options.binary_location = "/tmp/bin/headless-chromium"

    driver = webdriver.Chrome(executable_path='/tmp/bin/chromedriver', chrome_options=chrome_options)

    # Set up driver - FOR LOCAL TESTING
    # PATH = r"C:\Program Files (x86)\chromedriver.exe"
    # driver = webdriver.Chrome(PATH)

    zip_code_list = ZIP_CODES.split(",")
    appointments_found = ""

    driver.get("https://www.walgreens.com/findcare/vaccination/covid-19?ban=covid_vaccine_landing_schedule")
    
    time.sleep(1)

    appointment_button = driver.find_element_by_css_selector("span.btn.btn__blue")
    appointment_button.click()
    print('button clicked')

    time.sleep(5)
    print('page loaded')

    location_input = driver.find_element_by_id("inputLocation")
    search_button = driver.find_element_by_css_selector("button.btn")

    for zip_code in zip_code_list:
        print("Searching zip code " + zip_code)
        
        try: 
            location_input.click()
            location_input.send_keys(Keys.CONTROL, 'a')
            location_input.send_keys(zip_code)
            print('zip entered')

            search_button.click()
            print('zip searched')
        except Exception as e:
            print('Error during zip search:')
            print (e)

        time.sleep(2)

        try:
            unavailable_text = driver.find_element_by_xpath("//*[contains(text(),'"+ TEXT_QUERY +"')]").text
            print(unavailable_text + " - text found, try again later")
        except Exception as e:
            print (e)
            print(TEXT_QUERY + " - text NOT found. Appointments available!")
            appointments_found = appointments_found + zip_code + " "

    current_time = datetime.now(tz_IL).strftime("%H:%M") + " CT"

    if appointments_found != "":
        # Send notification
        notification_status = 'VACCINE APPOINTMENTS AVAILABLE @ ' + appointments_found
        params = { "value1" : notification_status, "value2" : '0', "value3" : current_time }
        requests.get(url = IFTTT_URL, params = params)
    else:
        notification_status = 'No vaccine appointments available'
    
    driver.quit()

    return {
        'statusCode': 200,
        'body': notification_status,
        'time': current_time
    }