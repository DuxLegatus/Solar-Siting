from fastapi import FastAPI,HTTPException,Request
from fastapi.staticfiles import StaticFiles
from data.sites import sites
from fastapi.templating import Jinja2Templates



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )

@app.get("/map")
def map_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="georgia_suitability_map.html"
    )

@app.get("/findings")
def findings(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="findings.html",
        context={"sites": sites}
    )

@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html"
    )

@app.get("/sites/{site_id}")
def get_site(site_id: int):
    if site_id - 1 in sites:
        return sites[site_id - 1]
    raise HTTPException(status_code=404, detail="Site not found")