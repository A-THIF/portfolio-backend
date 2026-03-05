from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

@router.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    # Get token from query parameter (you can also use headers)
    token = request.query_params.get("token")

    admin_secret = os.getenv("ADMIN_SECRET")

    if not token or token != admin_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Render your HTML admin dashboard (or serve an HTML file)
    html_content = """
    <html>
      <head><title>Admin Dashboard</title></head>
      <body>
        <h1>Welcome to Admin Dashboard</h1>
        <p>Only you can see this page.</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)