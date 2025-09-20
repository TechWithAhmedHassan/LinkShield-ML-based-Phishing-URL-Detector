1. Import libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# 2. Load dataset
# Replace "phishing.csv" with your dataset file name
df = pd.read_csv(r"./Dataset/dataset.csv")
print(df['Result'].value_counts())

#3 Blance the dataset by removing some rows with Result == 1
# Select all rows where Results == 1
rows_with_1 = df[df["Result"] == 1]
# Randomly select 1000 rows to drop
rows_to_drop = rows_with_1.sample(n=1000, random_state=42)
# Drop those rows from df
df = df.drop(rows_to_drop.index)
print(df["Result"].value_counts())
