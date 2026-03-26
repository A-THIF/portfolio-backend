from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.databases.database import SessionLocal
from app.models.visitor import Visitor
import os

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app/admin_dashboard.py
# ... (Keep your imports)

# C:\Users\parve\Documents\Projects\portfolio-backend\app\admin_dashboard.py

@router.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    token = request.query_params.get("token")
    admin_secret = os.getenv("ADMIN_SECRET_KEY")
    
    if not token or token != admin_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    page = int(request.query_params.get("page", 1) or 1)
    per_page = 10
    total_visitors = db.query(Visitor).count()
    total_pages = max(1, (total_visitors + per_page - 1) // per_page)
    visitors = db.query(Visitor).order_by(Visitor.last_visit.desc()).offset((page - 1) * per_page).limit(per_page).all()

    rows = "".join([
    f"<tr onclick=\"window.location='/admin/user/{v.id}?token={token}'\" style='cursor:pointer;'>"
    f"<td>{v.name}</td><td>{v.visit_count}</td><td>{v.last_visit.strftime('%b %d')}</td></tr>"
    for v in visitors
])


    full_html = f"""
    <html>
      <head>
        <title>Portfolio Analytics</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background:#0a0a0a; color:#eee; font-family: sans-serif; padding: 20px; }}
            .container {{ max-width: 900px; margin: auto; }}
            table {{ width:100%; border-collapse: collapse; background: #111; margin-bottom: 20px; border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 12px; border: 1px solid #222; text-align: left; }}
            tr:hover {{ background: #1d1d1d; }}
            .active {{ font-weight: bold; color: #4CAF50; border: 1px solid #4CAF50; padding: 2px 8px; text-decoration: none; }}
            .page-btn {{ color: #00BFFF; margin-right: 10px; text-decoration: none; }}
            .chart-container {{ position: relative; height:400px; width:100%; background: #111; border: 1px solid #333; padding: 15px; border-radius: 8px; box-sizing: border-box; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>🚀 Visitor Dashboard</h1>
            <table>
                <thead><tr><th>Name</th><th>Hits</th><th>Date</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            <div>Page: {" ".join([f"<a href='?token={token}&page={p}' class='{'active' if p==page else 'page-btn'}'>{p}</a>" for p in range(1, total_pages+1)])}</div>
            
            <h3 style="margin-top:40px;">Traffic Trend (Line Chart)</h3>
            <div class="chart-container">
                <canvas id="visitorChart"></canvas>
            </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const ctx = document.getElementById('visitorChart').getContext('2d');
                const safeToken = encodeURIComponent("{token}");

                fetch('/public/stats')
                    .then(res => res.json())
                    .then(data => {{
                        new Chart(ctx, {{
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
                                    y: {{ beginAtZero: true, grid: {{ color: '#222' }}, ticks: {{ color: '#888' }} }},
                                    x: {{ grid: {{ color: '#222' }}, ticks: {{ color: '#888' }} }}
                                }},
                                plugins: {{ legend: {{ display: false }} }}
                            }}
                        }});
                    }})
                    .catch(err => console.error("Chart failed to load:", err));
            }});
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=full_html)