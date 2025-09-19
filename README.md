# PhishSense 🔒  
*A Machine Learning Approach for Phishing URL Detection*

PhishSense is a lightweight machine-learning system designed to detect **phishing websites** based on their URL characteristics.  
It extracts meaningful features from URLs (such as length, entropy, suspicious keywords, and subdomain patterns) and applies machine learning models to classify them as **benign** or **phishing**.

---

## 🚀 Features
- URL-based feature extraction (length, tokens, entropy, presence of IPs, etc.)
- Multiple ML models: Logistic Regression, Random Forest, LightGBM
- Model evaluation with Accuracy, Precision, Recall, F1-Score, ROC-AUC
- Real-time API integration using **Flask / FastAPI**
- Well-structured pipeline for training, testing, and deployment
- Modular code (easy to extend with new models/features)

---


---

## 📊 Dataset
The project expects a dataset in the following format:

| url                               | label |
|-----------------------------------|-------|
| http://secure-paypal-login.com    |   1   |
| https://www.google.com            |   0   |
| http://update-your-bank-info.biz  |   1   |

- **label**: `1 = phishing`, `0 = benign`  
- You can use open datasets such as [PhishTank](https://phishtank.org/) or [Kaggle Phishing URLs Dataset](https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning).

---

## ⚙️ Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/phishsense.git
cd phishsense
pip install -r requirements.txt

