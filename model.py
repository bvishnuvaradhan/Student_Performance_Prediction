import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import numpy as np

# Synthetic Data with proper ranges
# Study hours per day: 0-24, Attendance %: 0-100, Previous score: 0-100
np.random.seed(42)
study_hours = np.random.rand(100) * 12  # 0-12 hours per day
attendance = np.random.rand(100) * 100  # 0-100%
previous_score = np.random.rand(100) * 100  # 0-100
# Add some boundary cases to guide the model
study_hours = np.append(study_hours, [0, 12, 12, 6])
attendance = np.append(attendance, [0, 100, 100, 75])
previous_score = np.append(previous_score, [0, 100, 95, 80])
X = np.column_stack([study_hours, attendance, previous_score])

# Normalize study hours to 0-1 range for linear regression
study_hours_normalized = X[:, 0] / 12
X_normalized = np.column_stack([study_hours_normalized, attendance, previous_score])

# Linear formula: Previous score (0.70), Attendance (0.20), Study hours normalized (0.10)
y = (X_normalized[:, 1] * 0.20) + (X_normalized[:, 2] * 0.70) + (X_normalized[:, 0] * 0.10) * 100
y = np.clip(y, 0, 100)

# Train linear regression model
model = LinearRegression()
model.fit(X_normalized, y)
joblib.dump(model, 'student_model.pkl')
print("✅ Model trained and saved!")
print(f"Model coefficients: Study hours={model.coef_[0]:.4f}, Attendance={model.coef_[1]:.4f}, Previous Score={model.coef_[2]:.4f}")

# Test predictions (normalized study hours: 0-12 → 0-1)
test_cases = [
    ([12/12, 100, 100], "12 hrs, 100% attendance, 100 prev score"),
    ([12/12, 100, 98], "12 hrs, 100% attendance, 98 prev score"),
    ([8/12, 75, 85], "8 hrs, 75% attendance, 85 prev score"),
    ([0/12, 0, 0], "0 hrs, 0% attendance, 0 prev score"),
]
print("\nTest Predictions:")
for inputs, desc in test_cases:
    pred = model.predict([inputs])[0]
    print(f"  {desc}: → {round(pred, 2)}%")

