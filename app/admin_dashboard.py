from fastapi import APIRouter, Request, Response, HTTPException, Depends, Cookie
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.databases.database import SessionLocal
from app.models.visitor import Visitor
from app.utils.security import verify_token
import os
from user_agents import parse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard_bootstrap(request: Request, admin_session: str = Cookie(None)):
    if admin_session:
        payload = verify_token(admin_session)
        if payload and payload.get("role") == "admin":
            return RedirectResponse(url="/admin-dashboard/view")
    """
    Step 1: Serves a bootstrap page that reads the JWT from the URL fragment
    and exchanges it for a first-party cookie on this domain.
    The actual dashboard is at /admin-dashboard/view (protected by cookie).
    """
    return HTMLResponse(content="""
    <html>
      <head><title>Authenticating...</title>
        <style>
          body { background:#0a0a0a; color:#eee; font-family:monospace;
                 display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
          #msg { text-align:center; }
        </style>
      </head>
      <body>
        <div id="msg">🔐 Authenticating...</div>
        <script>
          const token = window.location.hash.slice(1);
          const msg = document.getElementById('msg');

          if (!token) {
            msg.innerHTML = '❌ No token in URL. Close this tab and log in again.';
          } else {
            fetch('/admin/set-session', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
              body: JSON.stringify({ token: token })
            })
            .then(async res => {
              if (res.ok) {
                msg.innerHTML = '✅ Auth OK — redirecting...';
                window.location.replace('/admin-dashboard/view');
              } else {
                // Show the actual error from backend
                const text = await res.text();
                msg.innerHTML = '❌ Auth failed (' + res.status + '): ' + text;
              }
            })
            .catch(err => {
              msg.innerHTML = '❌ Network error: ' + err.message;
            });
          }
        </script>
      </body>
    </html>
    """)


@router.post("/admin/set-session")
async def set_admin_session(request: Request, response: Response): # No db dependency
    try:
        body = await request.json()
        token = body.get("token", "")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    if not token:
        raise HTTPException(status_code=400, detail="No token provided")
    
    payload = verify_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Invalid or non-admin token")
    
    # Set First-Party Cookie
    response.set_cookie(
        key="admin_session",
        value=token,
        httponly=True,
        samesite="strict", # This works because we are on the same domain
        secure=True,
        max_age=3600,
        path="/"
    )
    return {"ok": True}


@router.get("/admin-dashboard/view", response_class=HTMLResponse)
async def admin_dashboard_view(
    request: Request,
    db: Session = Depends(get_db),
    admin_session: str = Cookie(None)
):
    """
    Step 3: The actual dashboard, protected by the first-party cookie.
    """
    # Validate cookie directly (simpler than Depends here for HTML routes)
    if not admin_session:
        return HTMLResponse(
            content="<h1>Unauthorized</h1><a href='/admin-dashboard'>Login again</a>",
            status_code=401
        )
    
    payload = verify_token(admin_session)
    if not payload or payload.get("role") != "admin":
        return HTMLResponse(
            content="<h1>Forbidden</h1>",
            status_code=403
        )

    # Your existing dashboard logic
    page = int(request.query_params.get("page", 1) or 1)
    per_page = 10
    total_visitors = db.query(Visitor).count()
    total_pages = max(1, (total_visitors + per_page - 1) // per_page)
    visitors = (
        db.query(Visitor)
        .order_by(Visitor.last_visit.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    rows = ""
    for v in visitors:
        ua = parse(v.user_agent or "")
        device_info = f"{ua.browser.family} ({ua.os.family})"

        rows += (
            f"<tr onclick=\"window.location='/admin/user/{v.id}'\" style='cursor:pointer;'>"
            f"<td>{v.name}</td>"
            f"<td><small style='color:#888'>{v.email if v.email else '---'}</small></td>"
            f"<td>{v.visit_count}</td>"
            f"<td><span title='{v.user_agent}' style='font-size:0.8em; color:#00BFFF;'>{device_info}</span></td>"
            f"<td>{v.last_visit.strftime('%b %d')}</td>"
            f"</tr>"
        )

    pagination_links = " ".join([
        f"<a href='?page={p}' class='{'active' if p == page else 'page-btn'}'>{p}</a>"
        for p in range(1, total_pages + 1)
    ])

    full_html = f"""
    <html>
      <head>
        <title>Portfolio Analytics</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background:#0a0a0a; color:#eee; font-family: sans-serif; padding: 20px; display: flex; justify-content: center; }}
            .container {{ width: 100%; max-width: 900px; }}
            h1 {{ color: #4CAF50; border-bottom: 2px solid #222; padding-bottom: 10px; }}
            table {{ width:100%; border-collapse: collapse; background: #111; margin-top: 20px; border-radius: 12px; overflow: hidden; }}
            th, td {{ padding: 15px; border: 1px solid #222; text-align: left; }}
            th {{ background: #181818; color: #888; font-size: 12px; text-transform: uppercase; }}
            tr:hover {{ background: #1d1d1d; transition: 0.2s; }}
            .pagination {{ margin: 20px 0; display: flex; gap: 10px; }}
            .active {{ color: #4CAF50; font-weight: bold; border: 1px solid #4CAF50; padding: 5px 12px; border-radius: 4px; text-decoration: none; }}
            .page-btn {{ color: #00BFFF; padding: 5px 12px; text-decoration: none; border: 1px solid #333; border-radius: 4px; }}
            .page-btn:hover {{ background: #222; }}
            .chart-container {{ height:400px; width:100%; background: #111; padding: 20px; border-radius: 12px; border: 1px solid #333; margin-top: 20px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>🚀 Visitor Dashboard</h1>
            <table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Hits</th>
            <th>Device</th>
            <th>Date</th>
        </tr>
    </thead>
    <tbody>{rows}</tbody>
</table>
            <div class="pagination">{pagination_links}</div>
            <h3 style="margin-top:40px; color: #888;">Traffic Trend</h3>
            <div class="chart-container"><canvas id="visitorChart"></canvas></div>
        </div>
        <script>
            fetch('/public/stats').then(res => res.json()).then(data => {{
                new Chart(document.getElementById('visitorChart').getContext('2d'), {{
                    type: 'line',
                    data: {{
                        labels: data.dates,
                        datasets: [{{ 
                            label: 'Visitors', data: data.counts,
                            borderColor: '#4CAF50', backgroundColor: 'rgba(76,175,80,0.1)',
                            fill: true, tension: 0.4, borderWidth: 3
                        }}]
                    }},
                    options: {{ 
                        responsive: true, maintainAspectRatio: false,
                        scales: {{
                            y: {{ grid: {{ color: '#222' }}, ticks: {{ color: '#555' }} }},
                            x: {{ grid: {{ color: '#222' }}, ticks: {{ color: '#555' }} }}
                        }}
                    }}
                }});
            }});
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=full_html)
