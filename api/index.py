from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
from supabase import create_client, Client

app = FastAPI()

# Supabase Credentials
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

supabase: Client = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MindGraph AI</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 2.5rem; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; max-width: 400px; width: 100%; border: 1px solid #334155; }
            h1 { color: #38bdf8; margin-bottom: 0.5rem; font-size: 2rem; }
            p { color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem; }
            input { width: 100%; padding: 12px; margin: 8px 0; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; outline: none; }
            input:focus { border-color: #38bdf8; }
            button { width: 100%; padding: 12px; background: #0284c7; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 12px; font-size: 1rem; }
            button:hover { background: #0369a1; }
            #status { margin-top: 15px; font-size: 0.9rem; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>MindGraph AI</h1>
            <p>Authentication Portal</p>
            <form id="loginForm">
                <input type="email" id="email" placeholder="Email Address" required />
                <input type="password" id="password" placeholder="Password" required />
                <button type="submit" id="btn">Sign In</button>
            </form>
            <div id="status"></div>
        </div>

        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const status = document.getElementById('status');
                const btn = document.getElementById('btn');

                btn.innerText = "Signing in...";
                status.style.color = "#38bdf8";
                status.innerText = "Authenticating...";

                try {
                    const response = await fetch('/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: new URLSearchParams({ email, password })
                    });
                    const data = await response.json();

                    if (response.ok && data.status === "success") {
                        status.style.color = "#4ade80";
                        status.innerText = "Login Successful! Welcome, " + data.user;
                        btn.innerText = "Sign In";
                    } else {
                        status.style.color = "#f87171";
                        status.innerText = data.detail || "Authentication Failed!";
                        btn.innerText = "Sign In";
                    }
                } catch (err) {
                    status.style.color = "#f87171";
                    status.innerText = "Server Error. Please try again.";
                    btn.innerText = "Sign In";
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    if not supabase:
        return {"status": "error", "detail": "Supabase Environment Variables are missing!"}
    
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return {"status": "success", "user": res.user.email}
    except Exception as e:
        return {"status": "error", "detail": str(e)}