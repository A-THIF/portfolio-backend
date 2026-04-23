from fastapi import APIRouter, Request, HTTPException, Depends, Cookie
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.databases.database import SessionLocal
from app.models.visitor import Visitor
from app.utils.security import verify_token
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# C:\Users\parve\Documents\Projects\portfolio-backend\app\admin_dashboard.py

@router.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    db: Session = Depends(get_db),
    admin_session: str = Cookie(None) 
):
    # 1. SECURITY: Only the hidden "admin_session" cookie allows entry
    if not admin_session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    payload = verify_token(admin_session)
    if not payload or payload.get("role") != "admin":
         raise HTTPException(status_code=403, detail="Forbidden")

    # 2. LOGIC: Get data for the specific page
    page = int(request.query_params.get("page", 1) or 1)
    per_page = 10
    total_visitors = db.query(Visitor).count()
    total_pages = max(1, (total_visitors + per_page - 1) // per_page)
    visitors = db.query(Visitor).order_by(Visitor.last_visit.desc()).offset((page - 1) * per_page).limit(per_page).all()

    # 3. CLEAN ROWS: Fixed - no token in the location string
    rows = "".join([
        f"<tr onclick=\"window.location='/admin/user/{v.id}'\" style='cursor:pointer;'>"
        f"<td>{v.name}</td><td>{v.visit_count}</td><td>{v.last_visit.strftime('%b %d')}</td></tr>"
        for v in visitors
    ])

    # 4. CLEAN PAGINATION: Fixed - Only passing the page number (?page=X)
    pagination_links = " ".join([
        f"<a href='?page={p}' class='{'active' if p==page else 'page-btn'}'>{p}</a>" 
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
                <thead><tr><th>Name</th><th>Hits</th><th>Date</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            
            <div class="pagination">{pagination_links}</div>
            
            <h3 style="margin-top:40px; color: #888;">Traffic Trend</h3>
            <div class="chart-container"><canvas id="visitorChart"></canvas></div>
        </div>

        <script>
            // Fetch stats for the chart
            fetch('/public/stats').then(res => res.json()).then(data => {{
                new Chart(document.getElementById('visitorChart').getContext('2d'), {{
                    type: 'line',
                    data: {{
                        labels: data.dates,
                        datasets: [{{ 
                            label: 'Visitors', 
                            data: data.counts, 
                            borderColor: '#4CAF50', 
                            backgroundColor: 'rgba(76, 175, 80, 0.1)', 
                            fill: true, 
                            tension: 0.4,
                            borderWidth: 3
                        }}]
                    }},
                    options: {{ 
                        responsive: true, 
                        maintainAspectRatio: false,
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