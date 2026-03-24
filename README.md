
# 🧠 Visitor Analytics Backend for Interactive Portfolio

This project is a **FastAPI-powered backend system** built to support an **interactive, OS-style portfolio experience**.

Instead of a traditional static website, the portfolio behaves like a **desktop environment** — requiring user interaction and authentication.
This backend powers that experience by handling **authentication, visitor tracking, analytics, and real-time notifications**.

---

## 🚀 Features

* 🔐 **JWT Authentication** — Secure login system for users and admin access
* 📊 **Visitor Analytics** — Tracks unique users, visits, and activity history
* 🧑‍💻 **Admin Dashboard** — Paginated table with clickable user drill-down
* 📈 **Traffic Insights** — Graph-based activity tracking over time
* 📬 **Real-time Alerts** — Gmail API integration for visitor notifications
* ⚡ **Rate Limiting** — Prevents abuse and spam requests
* 🌐 **CORS Enabled** — Smooth frontend-backend communication

---

## 🏗️ Architecture

```
User (Browser)
     ↓
Flutter Web (Frontend)
     ↓
FastAPI (Backend)
     ↓
PostgreSQL (Neon Database)

+ Gmail API → Email Notifications
+ Render → Backend Hosting
```

---

## 🌍 Real-World Usage

This backend powers my interactive portfolio:

🔗 **Portfolio:** a-thif.netlify.app
💻 **GitHub:** [https://github.com/A-THIF/portfolio](https://github.com/A-THIF/portfolio)

### What happens when a user visits:

* User logs in through the lock screen
* JWT token is generated for session control
* Visitor data is stored in PostgreSQL
* Activity is tracked (visits, timestamps, device info)
* Admin receives a real-time email notification

### Admin Capabilities:

* 📋 View all visitors (paginated dashboard)
* 🔍 Click any user to view detailed session data
* 📈 Analyze traffic trends through graphs

---

## 🛠️ Tech Stack

* ⚙️ **FastAPI** — Backend framework
* 🗄️ **PostgreSQL (Neon)** — Cloud database
* 🧩 **SQLAlchemy** — ORM
* 🔒 **JWT (Jose)** — Authentication
* ⚡ **SlowAPI** — Rate limiting
* 📬 **Gmail API** — Email notifications
* 🔧 **Pydantic** — Validation & settings
* 🌍 **Render** — Deployment

---

## 📦 Installation

1. Clone the repository

   ```
   git clone https://github.com/A-THIF/portfolio-backend.git
   ```

2. Install dependencies

   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file and add:

   ```
   DATABASE_URL=your_database_url
   ADMIN_SECRET_KEY=your_secret
   GMAIL_REFRESH_TOKEN=your_token
   GMAIL_CLIENT_ID=your_client_id
   ```

4. Run the server

   ```
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## 📂 Project Structure

```
app/
 ├── main.py
 ├── config.py
 ├── routes/
 │    ├── auth.py
 │    ├── admin.py
 ├── models/
 │    ├── visitor.py
 ├── databases/
 │    ├── database.py
 ├── services/
 │    ├── email_service.py
 ├── utils/
 │    ├── security.py
 │    ├── limiter.py
 │    ├── validators.py
```

---

## 🧠 Key Highlights

* Built as part of an **interactive portfolio system**
* Designed to track **real user activity, not dummy data**
* Demonstrates **full-stack thinking (frontend + backend integration)**
* Implements **analytics, security, and automation together**

---

## 📬 Contact

If you have ideas, feedback, or collaboration opportunities:

* 💼 LinkedIn: *(add your link)*
* 📧 Email: *(add your email)*

---

## 💡 Note

This is **Version 1** of the backend.
Future improvements include:

* Advanced analytics (device breakdown, session duration)
* Improved security with full JWT-based admin system
* Real-time dashboards

