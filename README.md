# Student Predictor (EduPredict)

Simple full-stack demo app that predicts student scores from study hours, attendance and previous score. Built with Flask, MongoDB and a small ML model.

## Features
- Predict student score using a trained model (`student_model.pkl`).
- Per-user accounts with signup/login, profile and ability to delete account and their predictions.
- User dashboard showing personal prediction history and chart.
- Admin (master) account can view all users' predictions and an aggregated chart.
- Accessibility improvements and responsive UI (Bootstrap + Chart.js).

## Tech
- Python 3.8+
- Flask
- MongoDB (Atlas)
- scikit-learn, joblib
- Bootstrap 5, Chart.js

## Quick start
1. Copy `.env.example` to `.env` and fill in values (do NOT commit `.env`).
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Start the app:
```bash
python app.py
```
4. Open http://127.0.0.1:5000 and sign up or login as admin.

## Deploying to Render (easy)
1. Ensure `gunicorn` is in `requirements.txt` (already included).
2. This repo contains a `Procfile` with the start command for Gunicorn.
3. On https://render.com create a new **Web Service**, connect your GitHub repo and set the build and start commands as default. Add the required environment variables from your `.env` to Render's dashboard.
4. Deploy — Render will provide a public URL.

## Environment variables
Use `.env` with:
```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=
ADMIN_EMAIL=
FLASK_SECRET_KEY=
MONGO_URI=
```

## Notes
- The project includes a deterministic LinearRegression based model trained on synthetic data so perfect inputs map to 100%.
- For production: use a proper user store, hashed passwords (already used), HTTPS, and rotate credentials if leaked.

## License
This project is released under the MIT License — see `LICENSE`.

---
Generated and curated by the project owner.
