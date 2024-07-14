from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import pytz

from db_booking import insert_new_another_booking, update_another_booking, check_booking_exist

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


def increase_date_by_days(days: int) -> str:
    # Get today's date
    # Define the timezone for Spain
    spain_tz = pytz.timezone('Europe/Madrid')
    today_date = datetime.now(spain_tz)
    
    # Increase the date by the specified number of days
    future_date = today_date + timedelta(days=days)
    
    # Return the new date in 'YYYY-MM-DD' format
    return future_date.strftime('%Y-%m-%d')

def check_date(input_date: str) -> bool:
    # Get today's date without time component
    # Define the timezone for Spain
    spain_tz = pytz.timezone('Europe/Madrid')
    today_date = datetime.now(spain_tz).date()
    
    # Convert input_date string to a date object
    input_date_obj = datetime.strptime(input_date, '%Y-%m-%d').date()
    
    # Compare input date with today's date
    if input_date_obj == today_date:
        return True
    elif input_date_obj > today_date:
        return True
    else:
        return False

def get_sync_bookings():
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

    # Get today's date
    # Define the timezone for Spain
    spain_tz = pytz.timezone('Europe/Madrid')
    today_date = datetime.now(spain_tz).strftime('%Y-%m-%d')

    for ind in range(8):

        if ind > 0:
            today_date = increase_date_by_days(ind)
            # Wait for the iframe content to load
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ctl01_CC_ImageButtonAvanzarFechaDrch")))
            # Click the login button
            next_button = driver.find_element(By.ID, "ctl01_CC_ImageButtonAvanzarFechaDrch")
            next_button.click()
        print(f"Today date: {today_date}")
        # Wait for the iframe content to load
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "CuerpoTabla")))

        # Get the page source of the iframe content
        iframe_page_source = driver.page_source


        # Parse the iframe content with BeautifulSoup
        iframe_soup = BeautifulSoup(iframe_page_source, 'html.parser')

        # Extract the div elements with class 'ui-selectable' inside 'contenedor'
        reservas_container = iframe_soup.find('div', {'class': 'myReservas'}).find('div', {'id': 'contenedor'})
        selectable_divs = reservas_container.find('div', {'class': 'ui-selectable'})

        another_selectable_divs = selectable_divs.find_all('div', {'id':'selectable'})

        for ext_div in another_selectable_divs:
            each_routine = ext_div.find_all('div', {'class': 'imanEvento ui-draggable ui-draggable-handle'})

            for div in each_routine:
                evento_div = div.find('div', {'class': 'evento cursorNormal'})
                booking_text = evento_div.find('div', {'class':'eventoSuperior'})
                if evento_div:
                    evento_id = evento_div.get('id')
                    evento_columna = evento_div.get('columna')
                    evento_style = evento_div.get('style')
                    pedal_dict = {"1": "Pádel 1", "2": "Pádel 2", "3":"Pádel 3", "4": "Pádel 4", "5":"Pádel 5", "6":"Pádel 6"}
                    state = "unknown"
                    if "rgb(249, 231, 182)" in evento_style or "rgb(250, 210, 143)" in evento_style:
                        state = "Searching"
                    elif "rgb(238, 164, 164)" in evento_style:
                        state = "Open"
                
                    # event_info = f"ID: {evento_id}, Columna: {evento_columna}, Style: {evento_style}\n"
                    print("******   New Booking   ******")
                    print(f"Match number: {evento_id}\nCourt: {pedal_dict[evento_columna]}\nStatus: {state}")
                    if state== "Searching" or state == "Open":
                        
                        for br in booking_text.find_all('br'):
                            br.replace_with('\n')
                        # Extract text from each child element within the div
                        text_list = [element.get_text(separator='\n', strip=True) for element in booking_text]
                        serial = 0
                        for item in text_list:
                            if item.startswith('Partida'):
                                del text_list[serial]
                            serial+= 1
                        # Join the text list with newline characters
                        # joined_text = "\n".join(text_list)
                        first_line = text_list[0].strip().split(" ")
                        timetable = first_line[0].strip()
                        player_count = first_line[-1].strip()
                        player_occupied = 0
                        total_player = 0
                        if len(player_count[1:-1].split("/")) == 2:
                            player_occupied = int(player_count[1:-1].split("/")[0])
                            total_player = int(player_count[1:-1].split("/")[1][0])
                        else:
                            total_player = int(player_count[1:-1][0])
                        print(f"player_occupied: {player_occupied}")
                        print(f"player count: {player_count}")
                        players_lines = []
                        
                        for item in text_list[1:]:
                            if '\n' in item:
                                players_lines = item.split("\n")
                            else:
                                players_lines.append(item)
                        
                        print(f"Time period: {timetable}")
                        print(f"Player capacity: {player_count}")
                        print("Players")
                        print(players_lines)

                        # Check if booking exist in the server
                        is_exist = check_booking_exist(today_date)
                        if is_exist:
                            update_another_booking(is_exist.id,today_date, timetable, pedal_dict[evento_columna], evento_id, total_player, player_occupied, players_lines, state)
                        else:
                            insert_new_another_booking(today_date, timetable, pedal_dict[evento_columna], evento_id, total_player, player_occupied, players_lines, state)


    driver.quit()



if __name__ == '__main__':
    while True:
        get_sync_bookings()
        time.sleep(1800)