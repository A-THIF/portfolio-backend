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

    try: 
        page = int(request.query_params.get("page", 1))
    except:
        page = 1
    per_page = 10  # Hardcoded to 10 as per your requirement
    
    total_visitors = db.query(Visitor).count()
    total_pages = max(1, (total_visitors + per_page - 1) // per_page)

    # Fetch 10 rows for the current page
    visitors = db.query(Visitor).order_by(Visitor.last_visit.desc())\
        .offset((page - 1) * per_page).limit(per_page).all()

    # Generate Table Rows
    rows = "".join([
        f"<tr><td><a href='/admin/user/{v.id}?token={token}'>{v.name}</a></td>"
        f"<td>{v.visit_count}</td>"
        f"<td>{v.last_visit.strftime('%Y-%m-%d %H:%M')}</td></tr>"
        for v in visitors
    ])

    # Generate Pagination Links
    pagination = "".join([
        f"<a href='?token={token}&page={p}' style='margin:5px; {'font-weight:bold;' if p==page else ''}'>{p}</a>"
        for p in range(1, total_pages + 1)
    ])

   # Combined the response into a single variable to avoid return errors
    full_html = f"""
    <html>
      <head>
        <title>Portfolio Admin</title>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        <style>
            body {{ background:#1a1a1a; color:white; font-family:sans-serif; padding:20px; }} 
            table {{ width:100%; border-collapse:collapse; margin-top:20px; }} 
            th, td {{ border:1px solid #444; padding:12px; text-align:left; }}
            th {{ background:#333; }}
            tr:hover {{ background:#252525; }}
        </style>
      </head>
      <body>
        <h1>🚀 Admin Dashboard</h1>
        <div style="background:#222; padding:10px; border-radius:5px; margin-bottom:20px;">
            Total Visitors: <strong>{total_visitors}</strong> | Page {page} of {total_pages}
        </div>
        <table>
            <thead><tr><th>Name (Click for Detail)</th><th>Visits</th><th>Last Seen</th></tr></thead>
            <tbody>{rows if rows else "<tr><td colspan='3'>No visitors found</td></tr>"}</tbody>
        </table>
        <div style="margin-top:15px; background:#222; padding:10px; border-radius:5px;">{pagination}</div>
        <div id="chart" style="width:100%; height:350px; margin-top:30px; background:#222; border-radius:8px;"></div>
        <script>
            var myChart = echarts.init(document.getElementById('chart'), 'dark');
            fetch('/admin/stats?token={token}')
                .then(res => res.json())
                .then(data => {{
                    if (data.dates.length === 0) return;
                    myChart.setOption({{
                        backgroundColor: 'transparent',
                        title: {{ text: 'Visitor Activity', left: 'center' }},
                        tooltip: {{ trigger: 'axis' }},
                        xAxis: {{ type: 'category', data: data.dates }},
                        yAxis: {{ type: 'value' }},
                        series: [{{ 
                            data: data.counts, 
                            type: 'line', 
                            smooth: true, 
                            areaStyle: {{ opacity: 0.3 }},
                            itemStyle: {{ color: '#4CAF50' }} 
                        }}]
                    }});
                }});
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=full_html)