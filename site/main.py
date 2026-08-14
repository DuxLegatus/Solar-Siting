from tempfile import template

from fastapi import FastAPI,HTTPException,Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from data.sites import sites

import markdown
templates = Jinja2Templates(directory="templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def home(request: Request):
    with open("../docs/methodology.md", "r", encoding="utf-8") as file:
        text = file.read()
        text = text.replace("document", "section")
        text = text.replace("validation_summary.md", "findings")

        methodology = markdown.markdown(
            text,
            extensions=[
                "tables",
                "fenced_code",
                "attr_list"
            ]
        )

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "methodology": methodology
        }
    )

@app.get("/map")
def map_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="georgia_suitability_map.html"
    )



@app.get("/sites/{site_id}")
def get_site(site_id: int):
    if site_id - 1 in sites:
        return sites[site_id - 1]
    raise HTTPException(status_code=404, detail="Site not found")