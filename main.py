import socket

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from apps.api import api_app

app = FastAPI(title=f"Front ODS {socket.gethostname()}")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/api", api_app, name="api")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return RedirectResponse(request.url_for('get_sources'))


@app.get("/sources/", response_class=HTMLResponse)
def get_sources(request: Request):
    return templates.TemplateResponse(request=request, name="sources.html")


@app.get("/sources/{hostname}/{source}/")
def get_source(request: Request, hostname: str, source: str):
    return templates.TemplateResponse(request=request, name="source.html")


@app.get("/records/{hostname}/{source}/")
def get_source(request: Request, hostname: str, source: str):
    return templates.TemplateResponse(request=request, name="records.html")


@app.get("/employees/")
def add_employees(request: Request):
    return templates.TemplateResponse(request=request, name="employees.html")
