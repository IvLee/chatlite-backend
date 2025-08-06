# Chat Lite AI

A lightweight, SMS-style AI chatbot built with **Angular 20** (frontend) and **Flask + Python** (backend) using the **OpenAI API**.

## 🚀 Live Demo
Frontend (GitHub Pages): [https://ivlee.github.io/chatlite-frontend/](https://ivlee.github.io/chatlite-frontend/)  
Backend (Render): Private API endpoint

> **Note:** Backend may take up to ~30 seconds to wake up on free Render tier.

---

## ✨ Features
- **SMS-style chat UI** – User and AI messages in compact chat bubbles.
- **Dark/Light mode toggle** – Saved in backend config.
- **Persistent chat history** – Stored in backend.
- **Custom AI roles** – Change chatbot personality with `/role` command.
- **Built-in commands**:
  - `/clear` → Clear chat history
  - `/forget` → Clear chat history but keep current role
  - `/reset` → Reset chat history **and** role/theme to defaults
- **About & Instructions modals** – Accessible from hamburger menu.
- **Mobile-friendly** – Centered, scrollable chat layout.

---

## 🛠 Tech Stack
**Frontend:**  
- Angular 20  
- TypeScript  
- HTML5, CSS3

**Backend:**  
- Flask (Python)  
- Flask-CORS  
- OpenAI API  
- Python-dotenv

**Deployment:**  
- Frontend → GitHub Pages  
- Backend → Render

---

## 📦 Installation & Local Setup

### 1. Clone the repositories
```bash
# Backend
git clone https://github.com/YOUR_USERNAME/chatlite-backend.git
cd chatlite-backend

# Frontend
git clone https://github.com/YOUR_USERNAME/chatlite-frontend.git
cd chatlite-frontend
```

### 2. Backend Setup
```bash
cd chatlite-backend
pip install -r requirements.txt
```

Create a `.env` file:
```
BOT_ROLE=Sarcastic and witty but still helpful assistant
OPENAI_API_KEY=your_openai_api_key_here
```

Run backend:
```bash
python app.py
```

### 3. Frontend Setup
```bash
cd chatlite-frontend
npm install
ng serve
```

### 4. Access locally
- Frontend: `http://localhost:4200`
- Backend: `http://localhost:5000`

---

## 📜 License
MIT License
