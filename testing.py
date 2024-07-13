from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import time

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
WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# Give additional time for page elements to load if necessary
time.sleep(40)
# Switch to the iframe
iframe = driver.find_element(By.ID, "iframeContenido")
driver.switch_to.frame(iframe)

# Wait for the iframe content to load
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "CuerpoTabla")))

# Get the page source of the iframe content
iframe_page_source = driver.page_source


# Parse the iframe content with BeautifulSoup
iframe_soup = BeautifulSoup(iframe_page_source, 'html.parser')

# Extract the div elements with class 'ui-selectable' inside 'contenedor'
reservas_container = iframe_soup.find('div', {'class': 'myReservas'}).find('div', {'id': 'contenedor'})
selectable_divs = reservas_container.find('div', {'class': 'ui-selectable'}).find_all('div', {'id':'selectable'})

each_routine = selectable_divs.find_all('div', {'class':'imanEvento ui-draggable ui-draggable-handle'})



# Example: Write all text on the new page to a text file
# with open('output.txt', 'w', encoding='utf-8') as file:
#     file.write(iframe_page_source)

# Write the extracted divs' content to a text file
with open('output.txt', 'w', encoding='utf-8') as file:
    for div in each_routine:
        file.write(div.prettify())
        file.write('\n\n')


# Close the WebDriver
driver.quit()
