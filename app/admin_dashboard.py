from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.databases.database import SessionLocal
from app.models.visitor import Visitor # Import your Visitor model
import os

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    token = request.query_params.get("token")
    admin_secret = os.getenv("ADMIN_SECRET")

    if not token or token != admin_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 📊 FETCH REAL DATA FROM NEON DB
    visitor_count = db.query(Visitor).count()
    all_visitors = db.query(Visitor).order_by(Visitor.last_visit.desc()).limit(10).all()

    # Create rows for the table
    rows = "".join([f"<tr><td>{v.name}</td><td>{v.visit_count}</td><td>{v.last_visit}</td></tr>" for v in all_visitors])

    html_content = f"""
    <html>
      <head>
        <title>Admin Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        <style>
            body {{ font-family: sans-serif; background: #1a1a1a; color: white; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #444; padding: 10px; text-align: left; }}
            th {{ background: #333; }}
        </style>
      </head>
      <body>
        <h1>🚀 Portfolio Admin Panel</h1>
        <div style="background: #222; padding: 15px; border-radius: 8px;">
            <h3>Total Unique Visitors: {visitor_count}</h3>
        </div>

        <table>
            <thead><tr><th>Name</th><th>Visits</th><th>Last Seen</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>

        <div id="main" style="width: 600px;height:400px;margin-top:30px;"></div>
        
        <script>
          // Basic ECharts setup test
          var myChart = echarts.init(document.getElementById('main'), 'dark');
          myChart.setOption({{
            title: {{ text: 'Visitor Overview' }},
            tooltip: {{}},
            xAxis: {{ data: ['Total Visitors'] }},
            yAxis: {{}},
            series: [{{ name: 'Count', type: 'bar', data: [{visitor_count}] }}]
          }});
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)