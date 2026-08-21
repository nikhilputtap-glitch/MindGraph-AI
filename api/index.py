from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def read_root():
    return HTMLResponse("<h1>MindGraph AI - Vercel Deployment Success!</h1>")