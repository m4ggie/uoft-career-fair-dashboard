from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time

# --- Helpers ---
def split_field(field_value, delimiter=","):
    if not field_value or field_value.strip() == "":
        return ["Not specified"]
    return [x.strip() for x in field_value.split(delimiter) if x.strip()]

def split_opportunities(op_value):
    if not op_value or op_value.strip() == "":
        return ["Not specified"]
    return [x.strip() for x in re.split(r",| and ", op_value) if x.strip()]

# --- Selenium setup ---
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

URL = "https://studentlife.utoronto.ca/uoft-career-fair/attending-employers/"
driver.get(URL)

# --- Scroll to load all employers ---
SCROLL_PAUSE = 2
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

time.sleep(5)  # wait for JS to finish rendering

# --- Scrape cards and panels ---
cards = driver.find_elements(By.CSS_SELECTOR, ".wp-block-kadence-infobox")
panels = driver.find_elements(By.CLASS_NAME, "kt-accordion-panel-inner")

employers = []

for idx, card in enumerate(cards):
    # Company name
    try:
        name_elem = card.find_element(By.CSS_SELECTOR, ".kt-blocks-info-box-title")
        employer_name = name_elem.text.strip()
    except:
        employer_name = "Unknown"

    # Company link
    try:
        link_elem = card.find_element(By.CSS_SELECTOR, "a.kt-blocks-info-box-link-wrap")
        employer_link = link_elem.get_attribute("href")
    except:
        employer_link = "Not specified"

    # Default data
    employer_data = {
        "Employer": employer_name,
        "Link": employer_link,
        "Level of Study": "Not specified",
        "Hiring For": "Not specified",
        "Target Programs": "Not specified",
        "Industry": "Not specified",
        "Opportunities": "Not specified"
    }

    # Corresponding panel
    try:
        panel = panels[idx]
        panel_text = panel.get_attribute("innerText")
        lines = panel_text.splitlines()

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key.lower() == "level of study":
                    employer_data["Level of Study"] = "|".join(split_field(value))
                elif key.lower() == "hiring for":
                    employer_data["Hiring For"] = "|".join(split_field(value))
                elif key.lower() == "target programs":
                    employer_data["Target Programs"] = "|".join(split_field(value))
                elif key.lower() == "industry":
                    employer_data["Industry"] = value if value else "Not specified"
                elif key.lower() == "opportunities":
                    employer_data["Opportunities"] = "|".join(split_opportunities(value))
    except:
        pass

    employers.append(employer_data)

# --- Save to CSV ---
df = pd.DataFrame(employers)
df.to_csv("uoft_career_fair_employers.csv", index=False)
print(f"✅ Scraped {len(employers)} employers and saved to CSV.")

driver.quit()
