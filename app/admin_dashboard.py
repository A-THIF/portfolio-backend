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

    visitors = db.query(Visitor).order_by(Visitor.last_visit.desc())\
        .offset((page - 1) * per_page).limit(per_page).all()

    # Updated rows: Clicking the row navigates to the user detail
    rows = "".join([
        f"""
        <tr onclick="window.location='/admin/user/{v.id}?token={token}'" style="cursor:pointer;">
            <td style="color:#4CAF50; font-weight:bold;">{v.name}</td>
            <td>{v.visit_count}</td>
            <td>{v.last_visit.strftime('%b %d, %H:%M') if v.last_visit else 'N/A'}</td>
        </tr>
        """
        for v in visitors
    ])

    pagination = "".join([
        f"<a href='?token={token}&page={p}' class='page-btn {'active' if p==page else ''}'>{p}</a>"
        for p in range(1, total_pages + 1)
    ])

    full_html = f"""
    <html>
      <head>
        <title>Admin Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        <style>
            body {{ background:#0a0a0a; color:#eee; font-family: sans-serif; padding: 20px; }}
            .container {{ max-width: 900px; margin: auto; }}
            table {{ width:100%; border-collapse: collapse; background: #111; margin: 20px 0; }}
            th, td {{ padding: 12px; border: 1px solid #333; text-align: left; }}
            tr:hover {{ background: #222; }}
            .active {{ font-weight: bold; color: #4CAF50; border: 1px solid #4CAF50; padding: 2px 8px; }}
            #chart {{ width: 100%; height: 400px; min-height: 400px; margin-top: 40px; background: #111; border: 1px solid #333; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>🚀 Visitor Dashboard</h1>
            <p>Total Unique Visitors: {total_visitors}</p>
            <table>
                <thead><tr><th>Name</th><th>Hits</th><th>Last Active</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            <div>Page: {" ".join([f"<a href='?token={token}&page={p}' class='{'active' if p==page else ''}' style='color:#00BFFF; margin-right:10px;'>{p}</a>" for p in range(1, total_pages+1)])}</div>
            
            <h3>Traffic Trend</h3>
            <div id="chart"></div>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                var myChart = echarts.init(document.getElementById('chart'), 'dark');
                fetch('/admin/stats?token={token}')
                    .then(res => res.json())
                    .then(data => {{
                        myChart.setOption({{
                            backgroundColor: 'transparent',
                            xAxis: {{ type: 'category', data: data.dates }},
                            yAxis: {{ type: 'value' }},
                            series: [{{ data: data.counts, type: 'line', smooth: true, color: '#4CAF50' }}]
                        }});
                    }});
            }});
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=full_html)