from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

# --- Helper functions ---
def split_field(field_value, delimiter=","):
    if not field_value or field_value.strip() == "":
        return ["Not specified"]
    return [x.strip() for x in field_value.split(delimiter) if x.strip()]

def split_opportunities(op_value):
    if not op_value or op_value.strip() == "":
        return ["Not specified"]
    # Split by comma or " and "
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

    # Parse accordion panel
    try:
        panel = panels[idx]
        panel_html = panel.get_attribute("innerHTML")
        soup = BeautifulSoup(panel_html, "html.parser")
        paragraphs = soup.find_all("p")

        for p in paragraphs:
            # Get full paragraph text
            full_text = p.get_text(" ", strip=True)

            # Remove all <strong> tags to get clean value
            for s in p.find_all("strong"):
                s.extract()
            value = p.get_text(" ", strip=True)

            # Regex-based detection using original full_text
            if full_text.lower().startswith("level of study:"):
                employer_data["Level of Study"] = "|".join(split_field(value))
            elif full_text.lower().startswith("hiring for:"):
                employer_data["Hiring For"] = "|".join(split_field(value))
            elif full_text.lower().startswith("target programs:"):
                employer_data["Target Programs"] = "|".join(split_field(value))
            elif full_text.lower().startswith("industry:"):
                employer_data["Industry"] = value if value else "Not specified"
            elif full_text.lower().startswith("opportunities:"):
                employer_data["Opportunities"] = "|".join(split_opportunities(value))

    except Exception as e:
        print(f"Error parsing panel for {employer_name}: {e}")

    employers.append(employer_data)
    import pandas as pd

# Load your scraped CSV
df = pd.read_csv("uoft_career_fair_employers.csv")

# Shift the Employer column up by 1
df["Employer"] = df["Employer"].shift(-1)

# Drop the last row (which will now have NaN in Employer)
df = df[:-1]

# Save the fixed CSV
df.to_csv("uoft_career_fair_employers.csv", index=False)
print("✅ Fixed Employer column and saved CSV.")




driver.quit()
