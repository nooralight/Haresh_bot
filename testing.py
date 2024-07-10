from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
import time
from bs4 import BeautifulSoup

# Setup the Chrome WebDriver with the path to Chromium binary
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--disable-gpu')  # Disable GPU acceleration
options.add_argument('--no-sandbox')  # Bypass OS security model
options.binary_location = '/usr/bin/chromium-browser'  # Path to Chromium binary

# Specify the path to Chromedriver
service = ChromeService(executable_path='/usr/bin/chromedriver')

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=options)

# Open the login page
driver.get("https://app-clubdepadelbida.matchpoint.com.es/Login.aspx")

# Wait for the username input to be present
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

# Fill in the username
username = driver.find_element(By.ID, "username")
username.send_keys("scrap")

# Fill in the password
password = driver.find_element(By.ID, "password")
password.send_keys("1a2b3c4d@")



# Click the login button
login_button = driver.find_element(By.ID, "btnLogin")
login_button.click()

# Wait for the new page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# Give additional time for page elements to load if necessary
time.sleep(5)

# Get the page source of the new page
page_source = driver.page_source

# Extract text from the specified section using XPath
texts = driver.find_elements(By.XPATH, '//g[@id="CuerpoTabla"]//text')

# Extract the text values
extracted_texts = [text.text for text in texts]


# Example: Write all text on the new page to a text file
with open('output.txt', 'w', encoding='utf-8') as file:
    # Print the extracted texts
    for text in extracted_texts:
        file.write(text+"\n")

print("File has been")

# Close the browser
driver.quit()
