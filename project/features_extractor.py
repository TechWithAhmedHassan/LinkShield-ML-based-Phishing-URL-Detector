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


    # --- 26. Web Traffic (Placeholder: Alexa API needed) ---
    # -1 = low, 0 = medium, 1 = high
    try:
        # Replace YOUR_API_KEY with your SimilarWeb API key
        api_url = f"https://api.similarweb.com/v1/website/{url}/total-traffic-and-engagement/visits"
        headers = {"Authorization": "Bearer YOUR_API_KEY"}
        params = {"api_key": "YOUR_API_KEY"}
        response = requests.get(api_url, headers=headers, params=params, timeout=5)
        data = response.json()

        # Example: get estimated monthly visits
        visits = data.get("visits", None)

        if visits is None:
            features.append(-1)
        elif visits >= 1000000:   # High traffic threshold
            features.append(1)
        elif visits >= 10000:     # Medium traffic threshold
            features.append(0)
        else:
            features.append(-1)
    except:
        features.append(-1)


    # # --- 27. Page Rank (Deprecated, Placeholder) ---
    
    # API_KEY = "Yss0wskwkk8kwokw84g808s4gsk8wc4o440sswww4"
    # opr_url = "https://openpagerank.com/api/v1.0/getPageRank"

    # params = {
    #     "domains[]": "google.com"
    # }
    # headers = {
    #     "API-OPR": API_KEY
    # }

    # response = requests.get(url, headers=headers, params=params)

    # if response.status_code == 200:
    #     data = response.json()
    #     site = data["response"][0]
    #     # Rule: 1 if rank > 0 else -1
    #     output = 1 if site["page_rank_integer"] > 0 else -1
    #     print(output)
    # else:
    #     print("Error:", response.status_code, response.text) 
    

    # --- 28. Google Index ---
    try:
        query = f"https://www.google.com/search?q=site:{url}"
        r = requests.get(query, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if "did not match any documents" in r.text:
            features.append(-1)
        else:   
            features.append(1)
    except:
        features.append(-1)

    # --- 29. Links pointing to page (Placeholder: Majestic/Ahrefs API) ---
    features.append(0)

    # --- 30. Statistical report (Placeholder: Malicious dataset check) ---
    features.append(-1)

    if driver:
        driver.quit()

    return features


