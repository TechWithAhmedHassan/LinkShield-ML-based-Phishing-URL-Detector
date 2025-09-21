# 🛡️ Phishing URL Detection Using Random Forest

[![Medium Article](https://img.shields.io/badge/Read-Medium-green)](https://medium.com/@techwithahmedhassan/a-feature-based-approach-for-phishing-url-detection-using-random-forest-482cd5f605a1)

## 📌 Overview
Phishing remains one of the most effective cyber-attacks because it preys on human trust.  
This project builds a **feature-based, interpretable phishing detection pipeline** that extracts **24 URL & page-level features**, trains a **Random Forest Classifier**, and evaluates it using standard metrics.

Our pipeline prioritizes:
- **Explainability** → Clear reasons why a URL is flagged.
- **Lightweight design** → Works in near-real-time.
- **Resilience** → Handles missing/failed API calls gracefully.

---

## 📂 Dataset
- **Source:** Kaggle dataset (URLs only were used for validation).  
- **Benign URLs:** Top domains & curated lists.  
- **Malicious URLs:** Open phishing repositories.  
- **Final Features Extracted:** **24** (originally 30, but 6 API-dependent ones were dropped).

---

## ⚙️ Features Extracted
Each feature is encoded as `-1`, `0`, or `1`.  
Examples:

- `having_IP_Address` → Checks if URL uses raw IP.  
- `URL_Length` → Long URLs often indicate phishing.  
- `Prefix_Suffix` → Dashes in domains mimic brands.  
- `having_Sub_Domain` → Multiple nested subdomains.  
- `SSLfinal_State` → Valid or invalid SSL certificate.  
- `Request_URL`, `URL_of_Anchor`, `Links_in_tags` → External resource usage.  
- `Submitting_to_email` → Forms posting to `mailto:`.  
- `PopUpWindow`, `Redirect_on_mouseover`, `RightClick` → Dynamic phishing tricks (via Selenium).  
- `Domain_registration_length`, `Age_of_domain`, `DNS_Record` → WHOIS metadata.  

---

## 🏗️ Pipeline / Methodology
1. **Normalization**
   - Lowercasing, removing trailing slashes, cleaning encodings.  
2. **Static Feature Extraction**
   - Directly from URL string (fast, cheap).  
3. **HTML Parsing**
   - Analyzing anchors, tags, and resources using `requests + BeautifulSoup`.  
4. **Dynamic Checks (Selenium)**
   - Detect popups, hidden iframes, JS redirection, disabled right-click.  
5. **WHOIS & Metadata**
   - Domain age, registrar, DNS records (`python-whois`).  
   - Missing values preserved as `-1`.  

---

## 🧠 Model
- **Algorithm:** RandomForestClassifier  
- **Params:** `n_estimators=100`, `class_weight="balanced"`, `random_state=42`  
- **Train/Test Split:** Stratified, preserving phishing/legit ratios.  

### 📊 Evaluation Metrics
- Accuracy  
- Confusion Matrix  
- Precision, Recall, F1-score  

Random Forest also provides **feature importance scores**, which make predictions interpretable:
> “This URL is suspicious mainly because it uses an IP address, has too many subdomains, and the SSL certificate is invalid.”

---

## 🖼️ Frontend
We built a **Streamlit-based app** where users can:
- Enter a URL
- Extract features via our pipeline
- Get a **prediction: Safe ✅ / Phishing 🚨**
- See feature-based explanation

---

## 🔑 Key Learnings
- **WHOIS unreliability** → Missing WHOIS often signals phishing.  
- **API dependency issues** → External APIs were flaky/paid, so we dropped them.  
- **Selenium slowness** → Optimized via two-phase analysis (fast static + selective dynamic).  
- **Data imbalance** → Fixed with `class_weight="balanced"` and stratified splits.  
- **Interpretability vs. Complexity** → Random Forest chosen over black-box deep learning.  

---

## 📌 Why Feature Extraction Matters
- **Transparent** → Analysts understand the reasons.  
- **Scalable** → Static features run in near real-time.  
- **Resilient** → Pipeline works even with partial missing data.  

---

## 🚀 Future Work
- Improve dynamic analysis (Selenium optimization).  
- Experiment with ensemble models (RF + XGBoost).  
- Expand dataset with more diverse phishing samples.  

---

## 👨‍💻 Team Members
- [**Ahmed (Team Lead)**](https://www.linkedin.com/in/ahmedhassan731/): Pipeline architecture, supervised feature extraction, model dev.  
- [**Mohsin Aleem**](https://www.linkedin.com/in/m-mohsin-aleem-8a35a8267): HTML parsing, Selenium checks, feature engineering.  
- [**Muhammad Ali Hassan**](https://www.linkedin.com/in/muhammad-ali-hassan-70a416310/): Preprocessing, WHOIS integration, dataset validation, article writing.  


---

## 📖 Reference
Full write-up available here:  
👉 [Medium Blog](https://medium.com/@techwithahmedhassan/a-feature-based-approach-for-phishing-url-detection-using-random-forest-482cd5f605a1)
