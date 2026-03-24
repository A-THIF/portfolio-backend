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
        <title>Portfolio Analytics</title>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        <style>
            body {{ background:#0a0a0a; color:#eee; font-family: 'Inter', sans-serif; padding: 40px; }}
            .container {{ max-width: 1000px; margin: auto; }}
            table {{ width:100%; border-collapse: collapse; background: #111; border-radius: 8px; overflow: hidden; }}
            th {{ background: #1a1a1a; padding: 15px; text-align: left; color: #888; text-transform: uppercase; font-size: 12px; }}
            td {{ padding: 15px; border-top: 1px solid #222; }}
            tr:hover {{ background: #1d1d1d; }}
            .stats-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            .page-link {{ color: #555; text-decoration: none; padding: 5px 10px; border-radius: 4px; border: 1px solid #333; margin-right: 5px; }}
            .page-link.active {{ background: #4CAF50; color: white; border-color: #4CAF50; }}
            #chart {{ background: #111; border-radius: 12px; padding: 20px; border: 1px solid #222; }}
        </style>
      </head>
      <body>
        <div class="container">
            <div class="stats-bar">
                <h1>🚀 Visitor Logs</h1>
                <div>Total: <strong>{total_visitors}</strong></div>
            </div>
            
            <table>
                <thead><tr><th>Visitor Name</th><th>Hits</th><th>Last Active</th></tr></thead>
                <tbody>{rows if rows else "<tr><td colspan='3'>No data yet</td></tr>"}</tbody>
            </table>

            <div style="margin-top: 20px;">{pagination}</div>

            <h3 style="margin-top: 50px; color: #888;">Traffic Overview</h3>
            <div id="chart" style="width:100%; height:400px;"></div>
        </div>

        <script>
            var chartDom = document.getElementById('chart');
            var myChart = echarts.init(chartDom, 'dark');
            
            fetch('/admin/stats?token={token}')
                .then(res => res.json())
                .then(data => {{
                    myChart.setOption({{
                        backgroundColor: 'transparent',
                        tooltip: {{ trigger: 'axis' }},
                        xAxis: {{ type: 'category', data: data.dates, boundaryGap: false }},
                        yAxis: {{ type: 'value', splitLine: {{ lineStyle: {{ color: '#222' }} }} }},
                        series: [{{
                            name: 'Unique Visitors',
                            type: 'line',
                            smooth: true,
                            data: data.counts,
                            areaStyle: {{ color: 'rgba(76, 175, 80, 0.2)' }},
                            itemStyle: {{ color: '#4CAF50' }},
                            lineStyle: {{ width: 3 }}
                        }}]
                    }});
                }});

            // Resize chart on window resize
            window.addEventListener('resize', function() {{ myChart.resize(); }});
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=full_html)