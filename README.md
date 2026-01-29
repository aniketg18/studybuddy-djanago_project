# StudyBuddy Finder API 📚🤝

StudyBuddy Finder is a Django-based backend project designed to help students find and connect with compatible study partners.  
The platform supports user registration, profile management, and a mini chat feature for educational discussions.

This project focuses on learning real-world backend development concepts using Django, REST APIs, and WebSocket-based communication.

---

## 🚀 Features
- User Registration & Authentication
- User profile management
- Study buddy discovery
- Mini chat feature for discussion on study materials and educational topics
- RESTful API architecture
- ASGI-based server setup
- Clean Git version control using `.gitignore`

---

## 💬 Mini Chat Feature
- Enables users to connect and chat with their study buddies
- Intended strictly for **educational discussions**
- Helps students collaborate, clarify doubts, and share study resources
- Implemented using ASGI-compatible setup

---


![image alt](https://github.com/aniketg18/studybuddy-djanago_project/blob/7ec34a7210dd581545b80c0fc7d468ef4497aeda/chat.png)

## 🛠️ Tech Stack
- Python
- Django
- Django REST Framework
- Daphne (ASGI server)
- SQLite (development database)
- Git & GitHub

---

## 📂 Project Structure (Simplified)
studybuddy/
│── manage.py
│── studybuddy/
│ ├── settings.py
│ ├── urls.py
│ ├── asgi.py
│ └── wsgi.py
│── api.py
│ ├── models.py
│ ├── views.py
│ └── urls.py
│ ├── models.py
│ └── admin.py
│ ├── forms.py
│ └── serializer.py
│ ├── routing.py
│ └── apps.py
│── templates
│ ├── base.html
│ ├── login.html
│ ├── profile.html
│ ├── register.html
│ ├── home.html
│ ├── chat.html
│── .gitignore
│── README.md

---

## ⚙️ Setup Instructions

These steps are for anyone who wants to run this project locally.

1. Clone the repository
git clone https://github.com/aniketg18/studybuddy-djanago_project.git

2. Navigate to the project directory
cd studybuddy-djanago_project

3. Create a virtual environment (recommended)
python -m venv venv

4. Activate the virtual environment
Windows
venv\Scripts\activate

5. Install required dependencies
pip install django djangorestframework daphne

6. Apply database migrations
python manage.py migrate

7. Run the development server (ASGI using Daphne)
python -m daphne -p 8000 studybuddy.asgi:application

The server will start at:
http://127.0.0.1:8000/


🧩 Initial Project Setup Notes
The project initially uses a register app to handle user registration and authentication.
ASGI is used to support real-time features like chat.
SQLite is used for development simplicity.

📌Note
This project was built with the help of:
Official Django documentation
Online developer resources
ChatGPT for guidance, debugging, and learning support
The goal of this project is learning, skill development, and showcasing backend concepts clearly and honestly.

🙋‍♂️ Author
Aniket Gaikwad
GitHub: https://github.com/aniketg18
LinkedIn: https://www.linkedin.com/in/aniket-gaikwad-ai-ml/

---

## 5️⃣ After pasting → push it
```bash
git add README.md
git commit -m "Update README with setup, ASGI server, chat feature, and transparency note"
git push origin main








   
