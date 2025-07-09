# 🖥️ GraphScript Desktop Service

This is the desktop runtime service for GraphScript, built using PyWebView. It serves the frontend (React + TSX) in a native desktop window with added capabilities like vibrancy, frameless UI, and JS–Python interop.

## 🚀 Features
-	Loads the GraphScript editor from a local dev server
-	Transparent and frameless window with macOS-style vibrancy
-	Python JS API bridge to interact with frontend
-	Controlled via a lightweight API class

## 📁 Project Structure

```sh
gs-desktop-service/
├── main.py          # Main entry point
├── api.py           # JS API exposed to frontend
└── README.md
```

## ▶️ Run

- Make sure your frontend dev server (vite, react, etc.) is running at localhost:3000.

```sh
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
python3 main.py
```

