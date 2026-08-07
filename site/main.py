from fastapi import FastAPI
from routers import analysis,sites,pages    

app = FastAPI()



app.include_router(analysis.router)
app.include_router(sites.router)
app.include_router(pages.router)