 🏎️ Nelson Speed Finder

A Python Flask web app that displays speed limits and nearby speed cameras for streets in Nelson, Lancashire (UK).
Users can type a street name (e.g. Manchester Road) to view its speed limit, exact location, and nearby cameras on an interactive map.

🌍 Features

🔍 Search for any street in Nelson, Lancashire

🗺️ View the location on an interactive OpenStreetMap

🚦 Displays real speed limit data using OpenStreetMap’s Overpass API

🎥 Shows nearby speed cameras within a 400 m radius

🧭 Clean and responsive web interface built with Flask + Leaflet.js

💻 How to Run Locally

1️⃣ Clone this repository

git clone https://github.com/anumayub21/NelsonSpeedApp.git
cd NelsonSpeedApp


2️⃣ Create a virtual environment

python -m venv venv
venv\Scripts\activate


3️⃣ Install the required dependencies

pip install -r requirements.txt


4️⃣ Run the Flask app

python app.py


5️⃣ Open your browser and visit:

http://127.0.0.1:5000


✅ You’ll now see the Nelson Speed Finder web app running locally.

📁 Project Structure
NelsonSpeedApp/
├── app.py
├── requirements.txt
├── Procfile
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── camera.png
    └── cameras.json

🧠 Technologies Used

Python 3 — Flask web framework

HTML / CSS / JavaScript — frontend

Leaflet.js — interactive mapping

OpenStreetMap / Overpass API — geolocation and speed data

🏫 Author

Anum Ayub
BSc Computer Science — University of Bradford
GitHub: @anumayub21

💬 Notes

This project was created for educational and demonstration purposes.
It shows how Flask can integrate with external APIs to build real-world web applications that visualize location-based data.
