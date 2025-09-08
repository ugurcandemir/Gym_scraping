from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import random
import pandas as pd
import time
import os

options = Options()
options.add_argument("--headless")   

service = Service() 
driver = webdriver.Firefox(service=service, options=options)

try:
    driver.get("https://www.macfit.com/kulupler")
    select_element = driver.find_element(By.TAG_NAME, "select")
    options_list = select_element.find_elements(By.TAG_NAME, "option")
    city_links = [opt.get_attribute("value") for opt in options_list if "kulupler/" in opt.get_attribute("value")]

    for link in city_links:
        print(link)
except :
    pass

gyms_by_city = {}

try:
    for city_url in city_links:
        driver.get(city_url)
        time.sleep(2)  

        city_name = city_url.rstrip("/").split("/")[-1]

        branch_cards = driver.find_elements(
            By.CSS_SELECTOR, "div.our-informations-grid-card.branchitem a.grid-image"
        )
        branch_links = [card.get_attribute("href") for card in branch_cards]

        gyms_by_city[city_name] = branch_links
        print(f"{city_name}: {len(branch_links)} gyms found")
except :
    pass

for city, links in gyms_by_city.items():
    print(f"\nCity: {city}")
    for link in links:
        print("  ", link)

OUTPUT_CSV = "macfit_gyms.csv"
OUTPUT_XLSX = "macfit_gyms.xlsx"

# --- Load existing data or create empty ---
if os.path.exists(OUTPUT_CSV):
    df_existing = pd.read_csv(OUTPUT_CSV, encoding="utf-8-sig")
    scraped_urls = set(df_existing["Gym_URL"].tolist())
    print(f"Resuming... already scraped {len(scraped_urls)} gyms.")
else:
    df_existing = pd.DataFrame(columns=["City", "Gym_URL", "Address"])
    scraped_urls = set()
    df_existing.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    df_existing.to_excel(OUTPUT_XLSX, index=False)
    print("Created new empty CSV/Excel.")

# --- Scraping loop ---
try:
    for city, gym_links in gyms_by_city.items():
        for gym_url in gym_links:

            # Skip already scraped gyms
            if gym_url in scraped_urls:
                continue

            driver.get(gym_url)

            try:
                # Wait up to 10 seconds until address is available
                address_el = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "p.contact-detail-content"))
                )
                address = address_el.text.strip()
            except:
                address = None

            # Save immediately
            new_row = pd.DataFrame([{
                "City": city,
                "Gym_URL": gym_url,
                "Address": address
            }])

            # Append to CSV
            new_row.to_csv(OUTPUT_CSV, mode="a", index=False, header=False, encoding="utf-8-sig")

            # Append to Excel (rewrite whole file each time to avoid corruption)
            df_existing = pd.concat([df_existing, new_row], ignore_index=True)
            df_existing.to_excel(OUTPUT_XLSX, index=False)

            scraped_urls.add(gym_url)
            print(f"✅ Saved {city} → {gym_url} → {address}")

            # Random delay (2–5s) to avoid blocking
            time.sleep(random.uniform(2, 5))

finally:
    driver.quit()

