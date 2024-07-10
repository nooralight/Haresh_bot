from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup the Chrome WebDriver with the path to Chromium binary
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--disable-gpu')  # Disable GPU acceleration
options.add_argument('--no-sandbox')  # Bypass OS security model
options.binary_location = '/usr/bin/chromium-browser'  # Path to Chromium binary

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

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

# Select the language
language = driver.find_element(By.ID, "ddlLenguaje")
for option in language.find_elements(By.TAG_NAME, "option"):
    if option.get_attribute("value") == "en-US":
        option.click()
        break

# Click the login button
login_button = driver.find_element(By.ID, "btnLogin")
login_button.click()

# Wait for the new page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# Give additional time for page elements to load if necessary
time.sleep(5)

# Get the page source of the new page
page_source = driver.page_source

# Print the page title or any other information you need
print(driver.title)

# You can also use BeautifulSoup to parse the new page content
from bs4 import BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')
print(soup.title.text)

# Example: Print all text on the new page
print(soup.get_text())

# Close the browser
driver.quit()
