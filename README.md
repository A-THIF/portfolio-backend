# 🧠 Athif OS: Command Center (Backend)
> **"The secure engine behind the gamified experience."**

This is the **FastAPI-powered heartbeat** of the Athif OS ecosystem. It doesn't just serve data; it manages the high-security "Handshake" between the Flutter frontend and the analytics engine, ensuring every digital footprint is tracked without compromising privacy.

**📡 API Base:** [portfolio-backend-bnhn.onrender.com](https://portfolio-backend-bnhn.onrender.com)  
**🕹️ Paired Frontend:** [Athif OS](https://github.com/A-THIF/portfolio)

---

## 🚀 Core Capabilities

* **🔐 Multi-Stage Auth:** Handles JWT generation for visitors and a specialized "Bridge" flow for Admin access.
* **📊 Analytics Engine:** Tracks unique callssigns, visit frequency, and historical activity patterns.
* **🕵️ User Drill-Down:** Dynamic HTML dashboard for Admins with deep-dive views into individual visitor sessions.
* **📈 Traffic Visualization:** Aggregates database logs into clean JSON streams for Chart.js rendering.
* **📬 Automation:** Integrated Gmail API for real-time alerts whenever a new "explorer" enters the OS.
* **🛡️ Security Hardening:** Implements Rate Limiting (SlowAPI) and `SameSite=Strict` first-party cookies.

---

## 🏗️ Architecture: The "Two-Stage" Flow

To bypass modern browser restrictions on third-party cookies, this backend utilizes a **Fragment-to-Cookie Bridge**:

1.  **Stage 1 (Identity):** Validates credentials and issues a signed JWT.
2.  **Stage 2 (The Bridge):** Serves a bootstrap HTML page that extracts the JWT from a URL `#fragment`.
3.  **Stage 3 (Session):** Sets an `HttpOnly` first-party cookie on the `.onrender.com` domain, locking the session to the browser.

---

## 🛠️ Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Framework** | **FastAPI** | Async Python performance & automatic OpenAPI docs. |
| **Database** | **PostgreSQL (Neon)** | Serverless SQL storage for visitor footprints. |
| **ORM** | **SQLAlchemy** | Type-safe database mapping and queries. |
| **Security** | **JWT (Jose) + Cookies** | Secure identity and session management. |
| **Notifications** | **Gmail API** | Real-time email alerts for visitor activity. |

---

## 📂 Project Structure

```text
app/
 ├── main.py                # Entry point & Middleware config
 ├── admin_dashboard.py     # The "Bridge" & Main Dashboard HTML
 ├── routes/
 │    ├── auth.py           # Login & JWT generation
 │    ├── admin.py          # User detail views & Stats
 ├── models/
 │    ├── visitor.py        # SQLAlchemy Database Schema
 ├── databases/
 │    ├── database.py       # Connection pooling
 ├── services/
 │    ├── email_service.py  # Gmail API automation
 └── utils/
      └── security.py       # JWT signing & Cookie verification
```

🚀 Local Development
Clone & Environment

```Bash

git clone [https://github.com/A-THIF/portfolio-backend.git](https://github.com/A-THIF/portfolio-backend.git)
cd portfolio-backend
```

Install Dependencies

```Bash
pip install -r requirements.txt
```

Configure Environment (.env)
```bash
Code snippet
DATABASE_URL=your_postgres_url
SECRET_KEY=your_jwt_signing_key
ADMIN_NAME=your_username
ADMIN_SECRET_KEY=your_password
GMAIL_REFRESH_TOKEN=your_token
```
Boot the Engine

```Bash
uvicorn main:app --reload
```

🧠 Technical Highlights
Zero-Log Security: Using URL fragments ensures sensitive tokens never appear in the server's access.log.

First-Party Persistence: Transitioned from fragile sessionStorage to robust, secure Cookies for the Admin suite.

Hybrid Responses: Seamlessly serves both JSON API endpoints for Flutter and Server-Side Rendered (SSR) HTML for the Admin dashboard.

📬 Contact & Collaboration
Looking to discuss Agentic AI, Backend Architecture, or Cybersecurity?

LinkedIn: Mohamed Athif N

GitHub: A-THIF
