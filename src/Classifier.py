
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# 2. Load dataset
# Replace "phishing.csv" with your dataset file name
df = pd.read_csv(r"../Dataset/dataset.csv")
print(df['Result'].value_counts())

#3 Blance the dataset by removing some rows with Result == 1
#
rows_with_1 = df[df["Result"] == 1]
# Randomly select 1000 rows to drop
rows_to_drop = rows_with_1.sample(n=1000, random_state=42)
# Drop those rows from df
df = df.drop(rows_to_drop.index)
print(df["Result"].value_counts())
print(df.shape)

# Drop index column 
df = df.drop(columns=["index"])
print(df.shape)


# Split features and target
X = df.drop(columns=["Result"])
y = df["Result"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Predictions
y_pred = rf_model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Random Forest Accuracy:", accuracy)

# Confusion Matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

joblib.dump(rf_model, "rf_model.pkl")

new_data = [-1, -1, 1, 1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1]
# Convert into 2D array for prediction
import numpy as np
new_data = np.array(new_data).reshape(1, -1)

# Make prediction
prediction = rf_model.predict(new_data)
probability = rf_model.predict_proba(new_data)

# Get predicted probabilities (in %)
proba_percent = probability[0] * 100

print(f"Chances of being legitimate (-1): {proba_percent[0]:.2f}%")
print(f"Chances of being phishing (1): {proba_percent[1]:.2f}%")

# Final message
if prediction[0] == 1:
    print(f"The model predicts this link is HARMFUL with {proba_percent[1]:.2f}% confidence.")
else:
    print(f"The model predicts this link is SAFE with {proba_percent[0]:.2f}% confidence.")