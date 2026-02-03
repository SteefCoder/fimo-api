from fastapi import FastAPI

from .routers import fide, knsb

app = FastAPI()

app.include_router(fide.router)
app.include_router(knsb.router)


@app.get('/')
def index():
    return {"msg": "Hallo Papa!"}
