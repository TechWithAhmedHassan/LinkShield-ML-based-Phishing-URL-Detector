import re
import socket
import ssl
import ipaddress
import requests
import whois
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# --- Helpers ---
def _normalize_input_url(url: str) -> str:
    """Ensure URL has scheme and strip spaces."""
    url = str(url).strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url


def _fetch_page(url: str, timeout: int = 7):
    """Fetch page HTML safely with requests."""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        return r.text, r.text, False
    except Exception:
        return "", "", True


# --- Main feature extractor ---
def url_features(url: str):
    """
    Returns list of 30 features for a given URL.
    """
    # Blank input
    if not (url and str(url).strip()):
        return [-1] * 30

    url_norm = _normalize_input_url(url)
    parsed = urlparse(url_norm)
    hostname = parsed.hostname or ""
    page_domain = hostname.split(":")[0].lower() if hostname else ""

    page_text, page_html, fetch_failed = _fetch_page(url_norm)
    soup = BeautifulSoup(page_html, "lxml") if page_html else BeautifulSoup("", "lxml")

    features = []

    # === Features 1-9 ===
    # 1) having_IP_Address
    try:
        ipaddress.ip_address(page_domain)
        features.append(1)
    except:
        features.append(-1)

    # 2) URL_Length
    length = len(url_norm)
    features.append(1 if length < 6 or length > 75 else -1)

    # 3) Shortening_Service
    shortening_services = {
        'bit.ly', 'tinyurl.com', 'shorturl.at', 'ow.ly', 't.co',
        'goo.gl', 'is.gd', 'buff.ly', 'adf.ly', 'bl.ink',
        'lnkd.in', 'budurl.com', 'clicky.me', 'db.tt', 'qr.ae',
        'cur.lv', 'ity.im', 'q.gs', 'po.st', 'bc.vc',
        'tweez.me', 'v.gd', 'tr.im', 'link.zip', 'rb.gy',
        'short.link', 'tiny.cc', 'x.co', 'mcaf.ee', 'su.pr'
    }
    dom = page_domain[4:] if page_domain.startswith("www.") else page_domain
    features.append(1 if dom in shortening_services else -1)

    # 4) having_At_Symbol
    features.append(1 if "@" in url_norm else -1)

    # 5) double_slash_redirecting
    start_pos = 8 if url_norm.startswith("https://") else (7 if url_norm.startswith("http://") else 0)
    features.append(1 if url_norm.find("//", start_pos) != -1 else -1)

    # 6) Prefix_Suffix
    features.append(1 if "-" in page_domain else -1)

    # 7) having_Sub_Domain
    dot_count = page_domain.count(".")
    features.append(1 if dot_count > 2 else -1)

    # 8) SSLfinal_State
    try:
        if parsed.scheme != "https":
            features.append(-1)
        else:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection((page_domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=page_domain):
                    features.append(-1)
    except:
        features.append(1)

    # 9) Domain_registeration_length
    try:
        domain_info = whois.whois(page_domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if isinstance(creation_date, str):
            creation_date = datetime.strptime(creation_date.split()[0], "%Y-%m-%d")
        age_days = (datetime.now() - creation_date).days if creation_date else -1
        features.append(1 if age_days < 365 else -1)
    except:
        features.append(1)

    # === Features 10-19 ===
    # (Favicon, Port, HTTPS_token, Request_URL, etc.)
    try:
        if fetch_failed:
            features.append(-1)
        else:
            icon_tag = soup.find("link", rel=lambda x: x and "icon" in x.lower())
            if icon_tag and icon_tag.get("href"):
                href = (icon_tag.get("href") or "").strip()
                if href.startswith("//"):
                    href = "http:" + href
                if not href.startswith("http"):
                    features.append(1)
                else:
                    icon_dom = (urlparse(href).hostname or "").split(":")[0].lower()
                    features.append(1 if icon_dom == page_domain and page_domain else -1)
            else:
                features.append(-1)
    except:
        features.append(-1)

    try:
        p = parsed.port
        features.append(1 if (p is None or p in (80, 443)) else -1)
    except:
        features.append(-1)

    try:
        rest = url_norm.split("://", 1)[-1].lower()
        features.append(-1 if "https" in rest else 1)
    except:
        features.append(-1)

    # Request_URL (imgs, scripts, links external/internal)
    try:
        if fetch_failed:
            features.append(-1)
        else:
            tags = []
            tags += soup.find_all("img", src=True)
            tags += soup.find_all("script", src=True)
            tags += soup.find_all("link", href=True)
            total = len(tags)
            if total == 0:
                features.append(1)
            else:
                external = 0
                for t in tags:
                    val = (t.get("src") or t.get("href") or "").strip()
                    if val.startswith("//"):
                        val = "http:" + val
                    if val.startswith("http") and (urlparse(val).hostname or "").split(":")[0].lower() != page_domain:
                        external += 1
                ratio = external / total
                features.append(-1 if ratio > 0.5 else (0 if ratio > 0.22 else 1))
    except:
        features.append(-1)

    # URL_of_Anchor
    try:
        if fetch_failed:
            features.append(-1)
        else:
            anchors = soup.find_all("a", href=True)
            if not anchors:
                features.append(1)
            else:
                suspicious = 0
                total = len(anchors)
                for a in anchors:
                    href = (a.get("href") or "").strip().lower()
                    if href == "" or href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                        suspicious += 1
                    elif href.startswith("http") and (urlparse(href).hostname or "").split(":")[0].lower() != page_domain:
                        suspicious += 1
                ratio = suspicious / total
                features.append(-1 if ratio > 0.5 else (0 if ratio > 0.22 else 1))
    except:
        features.append(-1)

    # Links_in_tags
    try:
        if fetch_failed:
            features.append(-1)
        else:
            tags = []
            tags += soup.find_all("link", href=True)
            tags += soup.find_all("script", src=True)
            tags += soup.find_all("iframe", src=True)
            if not tags:
                features.append(1)
            else:
                ext = 0
                for t in tags:
                    val = (t.get("href") or t.get("src") or "").strip()
                    if val.startswith("//"):
                        val = "http:" + val
                    if val.startswith("http") and (urlparse(val).hostname or "").split(":")[0].lower() != page_domain:
                        ext += 1
                ratio = ext / len(tags)
                features.append(-1 if ratio > 0.5 else (0 if ratio > 0.22 else 1))
    except:
        features.append(-1)

    # SFH
    try:
        if fetch_failed:
            features.append(-1)
        else:
            forms = soup.find_all("form", action=True)
            if not forms:
                features.append(-1)
            else:
                sfh_scores = []
                for f in forms:
                    action = (f.get("action") or "").strip()
                    if action == "" or action.lower() == "about:blank":
                        sfh_scores.append(-1)
                    elif action.startswith("http"):
                        act_dom = (urlparse(action).hostname or "").split(":")[0].lower()
                        sfh_scores.append(1 if act_dom == page_domain and page_domain else -1)
                    else:
                        sfh_scores.append(0)
                if any(x == -1 for x in sfh_scores):
                    features.append(-1)
                elif any(x == 0 for x in sfh_scores):
                    features.append(0)
                else:
                    features.append(1)
    except:
        features.append(-1)

    # Submitting_to_email
    try:
        if fetch_failed:
            features.append(-1)
        else:
            forms = soup.find_all("form", action=True)
            email_flag = 1
            for f in forms:
                action = (f.get("action") or "").lower()
                if action.startswith("mailto:") or ("@" in action and not action.startswith("http")):
                    email_flag = -1
                    break
            features.append(email_flag)
    except:
        features.append(-1)

    # Abnormal_URL
    try:
        if fetch_failed:
            features.append(1 if re.match(r'^[\w.-]+$', page_domain) and page_domain else -1)
        else:
            page_text_lower = soup.get_text(" ", strip=True).lower()
            features.append(1 if page_domain and page_domain in page_text_lower else -1)
    except:
        features.append(-1)

    

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url_norm)
    except WebDriverException:
        driver = None

    # 19) RightClick
    try:
        if driver:
            disable_rclick = driver.execute_script("return (typeof document.oncontextmenu === 'function');")
            features.append(-1 if disable_rclick else 1)
        else:
            features.append(1)
    except:
        features.append(1)

    # 20) PopUpWindow
    try:
        if driver:
            popup_detect = driver.execute_script("return (window.open.toString().includes('[native code]') === false);")
            features.append(-1 if popup_detect else 1)
        else:
            features.append(1)
    except:
        features.append(1)

    # 21) Iframe
    try:
        if driver:
            iframe_count = len(driver.find_elements("tag name", "iframe"))
            features.append(-1 if iframe_count > 0 else 1)
        else:
            features.append(1)
    except:
        features.append(1)

    # 22) Age of domain
    try:
        domain_info2 = whois.whois(page_domain)
        creation_date2 = domain_info2.creation_date
        if isinstance(creation_date2, list):
            creation_date2 = creation_date2[0]
        if isinstance(creation_date2, str):
            creation_date2 = datetime.strptime(creation_date2.split()[0], "%Y-%m-%d")
        age_days2 = (datetime.now() - creation_date2).days if creation_date2 else 0
        features.append(1 if age_days2 >= 180 else -1)
    except:
        features.append(-1)

    # 23) DNS Record
    try:
        socket.gethostbyname(page_domain)
        features.append(1)
    except:
        features.append(-1)

    # 24) Google Index
    try:
        query = f"https://www.google.com/search?q=site:{url_norm}"
        r = requests.get(query, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if "did not match any documents" in r.text:
            features.append(-1)
        else:
            features.append(1)
    except:
        features.append(-1)


    # Cleanup Selenium
    if driver:
        driver.quit()

    # # Make sure length is exactly 30
    # if len(features) != 30:
    #     print(f"⚠️ Warning: got {len(features)} features for URL: {url_norm}")
    #     if len(features) < 30:
    #         features.extend([-1] * (30 - len(features)))
    #     else:
    #         features = features[:30]

    return features


# # --- Test run ---
# if __name__ == "__main__":
#    url = "http://bit.ly/2C@Sm2gc"
#    features = url_features(url)
#    print(features)
# #    print("Total features:", len(features))