from fastapi import FastAPI,HTTPException,Request
from data.sites import sites
from fastapi.templating import Jinja2Templates



app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        {"request": request},
        "home.html",
    )

@app.get("/map")
def map_page(request: Request):
    return templates.TemplateResponse(
        {"request": request},
        "georgia_suitability_map.html",
        
    )

@app.get("/findings")
def findings(request: Request):
    return templates.TemplateResponse(
        {
            "request": request,
            "sites": sites
        },
        "findings.html",
    )

@app.get("/sites/{site_id}")
def get_site(site_id: int):
    if site_id-1 in sites:
        return sites[site_id-1]
    raise HTTPException(status_code=404, detail="Site not found")

@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse(
        {"request": request},
        "about.html",
    )