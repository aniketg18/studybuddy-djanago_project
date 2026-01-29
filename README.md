# StudyBuddy Finder API 📚🤝

StudyBuddy Finder is a Django-based backend project designed to help students find and connect with compatible study partners.  
The platform supports user registration, profile management,real-time chat, discovery, search, and productivity tools.

This project focuses on learning real-world backend development concepts using Django, REST APIs, WebSocket-based and tested with Postman.

---

## 🚀 Features
- 📝 User Registration & Authentication – secure signup/login
- 👤 User Profile – editable interests, skills (known & to-learn), location
- 🔎 Discover Page – view & connect with study partners by interests/skills/location
- 💬 Mini Chat – real-time messaging via WebSocket (ASGI), tested with Postman
- 📍 Search & Filter – find users easily by location, interests, or skills
- 🏠 Home Page Features – notes, to-do list, track study tasks, stay productive
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

---

👤 User Profile Features
- Add/edit interests, skills, and location
- Skills divided into what you know & what you want to learn
- Profiles can be found by others or used to discover compatible study partners
- Location-based & interest-based matching for easier connection

---

![image alt](https://github.com/aniketg18/studybuddy-djanago_project/blob/20151308c9c9f03494711c78328c251a86cb63dd/user%20profile.png)

---

🔎 Discover Page
- Browse other users’ profiles
- Filter by location, interests, or skills
- Helps find mutual-interest partners quickly
- Connect directly with compatible users

---

![image alt](https://github.com/aniketg18/studybuddy-djanago_project/blob/20151308c9c9f03494711c78328c251a86cb63dd/discover%20page.png)

---

🏠 Home Page Features
- 📓 Notes – write, edit, and organize study material
- ✅ To-Do List – track tasks and maintain discipline
- 📊 Progress Tracking – mark completed tasks or topics
- ⚡ Quick Access – chat & discover features right from home
- Boosts productivity & organization

---

![image alt](https://github.com/aniketg18/studybuddy-djanago_project/blob/20151308c9c9f03494711c78328c251a86cb63dd/homepage.png)

---

## 🛠️ Tech Stack
- Python
- Django
- Django REST Framework
- Daphne (ASGI server)
- SQLite (development database)
- Git & GitHub

---

# 🔧 Backend Architecture & API Flow
## 1️⃣ REST API Endpoints & Methods
The project uses a fully RESTful API architecture to manage user profiles, discover page, friend requests, notes, and chat. All endpoints are tested via Postman for correctness

| Operation             | Endpoint                     | HTTP Method | Purpose                                        |
| --------------------- | ---------------------------- | ----------- | ---------------------------------------------- |
| Fetch user profiles   | `/api/users/`                | GET         | Retrieve user list or single profile           |
| Update profile        | `/api/users/<id>/`           | PATCH       | Update fields like interests, skills, location |
| Send friend request   | `/api/friends/`              | POST        | Create a new friend request record             |
| Accept friend request | `/api/friends/<id>/accept/`  | PATCH       | Mark request as accepted in DB                 |
| Add notes / to-do     | `/api/notes/`, `/api/todos/` | POST        | Add productivity items                         |
| Fetch chat messages   | `/api/chats/<room_id>/`      | GET         | Retrieve chat history                          |
| Send chat message     | `/api/chats/<room_id>/`      | POST        | Send new message via REST (for fallback)       |

The API supports GET, POST, PATCH, and DELETE operations to provide full CRUD functionality for all models. PATCH is primarily used for partial updates, such as updating a user profile or accepting a friend request.

## 2️⃣ Search & Filter Logic
### Structure:
- The Discover Page allows users to find potential study partners using location, interests, and skills as filters.
- The API returns serialized user cards containing: Name, Interests, Skills, Location. These cards are used in the frontend to display profiles.
- /api/users/?location=Mumbai&interests=Python
- Filtering is implemented using Django ORM queries and DRF serializers to ensure efficient and accurate results.

## 3️⃣ Friend Request Workflow
### Structure:
- Sending a Request:- 
Users send a friend request via POST /api/friends/. Requests are stored in the FriendRequest model with status='pending'.
- Accepting a Request:- 
The recipient accepts via PATCH /api/friends/<id>/accept/. The connection is permanent in the database and updates the status to accepted.
- Chat Activation:- 
Only after acceptance can users initiate real-time chat. Chat rooms are dynamically created per connection, with messages stored in ChatMessage model.
- Database Notes:- 
Friend requests and chat messages are persisted permanently to allow historical retrieval and maintain connection integrity.

## 4️⃣ Superadmin / Admin Panel
### Structure:
- Short explanation:- 
Django Admin (superuser) is used to monitor and manage all models during development. It allows viewing and debugging UserProfile, FriendRequest, and ChatMessage tables.
- production vs development:- 
While superadmin is useful for testing and monitoring, normal user interactions with friend requests and chat are handled entirely via API

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








   
