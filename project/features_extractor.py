import re
import socket
import whois
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException



def url_features(url: str):
    features = []
    # Setup Selenium headless browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
    except WebDriverException:
        driver = None


    # --- 21. RightClick (detect JS disable) ---
    try:
        if driver:
            disable_rclick = driver.execute_script(
                "return (typeof document.oncontextmenu === 'function');"
            )
            features.append(-1 if disable_rclick else 1)
        else:
            features.append(1)
    except:
        features.append(1)


    # --- 22. popUpWindow ---
    try:
        if driver:
            popup_detect = driver.execute_script(
                "return (window.open.toString().includes('[native code]') === false);"
            )
            features.append(-1 if popup_detect else 1)
        else:
            features.append(1)
    except:
        features.append(1)



    # --- 23. Iframe ---
    try:
        if driver:
            iframe_count = len(driver.find_elements("tag name", "iframe"))
            features.append(-1 if iframe_count > 0 else 1)
        else:
            features.append(1)
    except:
        features.append(1)





    # --- 24. Age of domain ---
    try:
        domain_info = whois.whois(url)
        creation_date = domain_info.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if isinstance(creation_date, str):
            creation_date = datetime.strptime(creation_date.split()[0], "%Y-%m-%d")

        age_days = (datetime.now() - creation_date).days if creation_date else 0
        features.append(1 if age_days >= 180 else -1)
        # print(f"Domain age (days): {age_days}") 

    except Exception as e:
        print(f"WHOIS error for {url}: {e}")
        features.append(-1)





    # --- 25. DNS Record ---
    try:
        hostname = url.split("//")[-1].split("/")[0]
        socket.gethostbyname(hostname)
        features.append(1)
    except:
        features.append(-1)



    # --- 26. Google Index ---
    try:
        query = f"https://www.google.com/search?q=site:{url}"
        r = requests.get(query, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if "did not match any documents" in r.text:
            features.append(-1)
        else:   
            features.append(1)
    except:
        features.append(-1)


    if driver:
        driver.quit()

    return features


