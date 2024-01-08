# contents of scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from database import create_connection, insert_country, get_country_id, insert_roadtrip, roadtrip_exists
import json


def load_country_codes():
    with open('countries.json', 'r') as file:
        return json.load(file)

def get_country_url(country_name):
    country_codes = load_country_codes()
    country_code = country_codes.get(country_name, "")
    url = f"https://www.comptoirdesvoyages.fr/voyage-pays/{country_name.lower()}/{country_code}"
    return url

def get_country_rating(url):
    driver = setup_driver()
    driver.get(url)
    try:
        rating_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".module__avis__score"))
        )
        rating = rating_element.text
        return rating
    except TimeoutException:
        print("Pas de note.")
        return "Pas de note disponible"
    finally:
        driver.quit()

def get_roadtrip_duration(url):
    driver = setup_driver()
    driver.get(url)
    try:
        WebDriverWait(driver, 30).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".module__tripCard__card__duration"))
        )
        duration_elements = driver.find_elements(By.CSS_SELECTOR, ".module__tripCard__card__duration")
        roadtrip_durations = [driver.execute_script("return arguments[0].innerText;", element).strip() for element in duration_elements]
        return roadtrip_durations
    except TimeoutException:
        print("Le chargement des durées de roadtrip a pris trop de temps.")
        return []
    finally:
        driver.quit() 


def get_roadtrip_prices(url):
    driver = setup_driver()
    driver.get(url)
    try:
        WebDriverWait(driver, 30).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".module__tripCard__card__price"))
        )
        prices_elements = driver.find_elements(By.CSS_SELECTOR, ".module__tripCard__card__price")
        roadtrip_prices = [driver.execute_script("return arguments[0].innerText;", element).strip() for element in prices_elements]
        return roadtrip_prices
    except TimeoutException:
        print("Le chargement des prix de roadtrip a pris trop de temps.")
        return []
    finally:
        driver.quit() 


def get_roadtrip_names(url):

    driver = setup_driver()
    driver.get(url)
    try:
        WebDriverWait(driver, 30).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a.module__tripCard__card__link"))
        )
        roadtrip_elements = driver.find_elements(By.CSS_SELECTOR, "a.module__tripCard__card__link")
        roadtrip_names = [driver.execute_script("return arguments[0].innerText;", element).strip() for element in roadtrip_elements]
        return roadtrip_names
    except TimeoutException:
        print("Le chargement des noms de roadtrip a pris trop de temps.")
        return []
    finally:
        driver.quit()
 


def setup_driver():    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

''' def get_roadtrip_img(url):
    driver = setup_driver()
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "picture.component_picture img"))
        )
        image_elements = driver.find_elements(By.CSS_SELECTOR, "picture.component_picture img")
        if image_elements:
            img_srcset = image_elements[0].get_attribute('srcset')
            img_url = img_srcset.split(',')[0].strip().split(' ')[0]
            return img_url
        else:
            print("Aucune image trouvée.")
            return None
    except TimeoutException:
        print("Le chargement de l'image a pris trop de temps.")
        return None
    finally:
        driver.quit()

def get_roadtrip_description(base_url, roadtrip_path):
    roadtrip_url = f"{base_url}{roadtrip_path}"
    driver = setup_driver()
    driver.get(roadtrip_url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".module__columnText__descriptif > p"))
        )
        description_element = driver.find_element(By.CSS_SELECTOR, ".module__columnText__descriptif > p")
        description_text = description_element.text
        print(description_text)
        return description_text
    except TimeoutException:
        print("Le chargement de la page ou la présence de la description a pris trop de temps.")
        return None
    except Exception as e:
        print(f"Une erreur est survenue lors de la récupération de la description : {e}")
        return None
    finally:
        driver.quit()'''
            
            
def get_destinations():
    driver = setup_driver()
    driver.get('https://www.comptoirdesvoyages.fr/')
    driver.set_window_size(1686, 1055)
    try:
        decline_cookies_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
        )
        decline_cookies_button.click()
        print("Cookies declined.")

        destinations_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".header__destination-btn > span"))
        )
        destinations_button.click()
        print("Clicked 'Toutes nos destinations'.")

        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".popin-destination__list__item"))
        )
        
        destination_items = driver.find_elements(By.CSS_SELECTOR, ".popin-destination__list__item a")
        destinations = [item.text for item in destination_items]
        return destinations
    
    except TimeoutException as e:
        print("Bouton 'Toutes nos destinations' pas trouvé.")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        driver.quit()

def save_roadtrip_to_db(country_name, roadtrip_name, duration, price):
    conn = create_connection("/Users/simondaniel/Desktop/Scraping-project/scraper/data.db")
    with conn:
        country_id = get_country_id(conn, country_name)
        if not country_id:
            country_id = insert_country(conn, country_name, None) 

        insert_roadtrip(conn, country_id, roadtrip_name, duration, price)

def scrape_and_save_roadtrips(country_name):
    url = get_country_url(country_name)
    roadtrip_names = get_roadtrip_names(url)
    roadtrip_durations = get_roadtrip_duration(url)
    roadtrip_prices = get_roadtrip_prices(url)

    base_url = "https://www.comptoirdesvoyages.fr"

    for i, roadtrip_name in enumerate(roadtrip_names):
        duration = roadtrip_durations[i] if i < len(roadtrip_durations) else "Unknown"
        price = roadtrip_prices[i] if i < len(roadtrip_prices) else "Unknown"
        roadtrip_path = get_roadtrip_path(roadtrip_name) 
        #description = get_roadtrip_description(base_url, roadtrip_path) if roadtrip_path else "No description"

        save_roadtrip_to_db(country_name, roadtrip_name, duration, price)

def pays_roadtrip(url,country_name):

    roadtrip_names = get_roadtrip_names(url)
    roadtrip_durations = get_roadtrip_duration(url)
    roadtrip_prices = get_roadtrip_prices(url)

    conn = create_connection("/Users/simondaniel/Desktop/Scraping-project/scraper/data.db")

    country_id = insert_country(conn, country_name, None) 

    for i, name in enumerate(roadtrip_names):
        duration = roadtrip_durations[i] if i < len(roadtrip_durations) else None
        price = roadtrip_prices[i] if i < len(roadtrip_prices) else None
        if not roadtrip_exists(conn, name, country_name):
            insert_roadtrip(conn, country_id, name, duration, price)

    conn.close()