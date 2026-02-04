from functools import lru_cache

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .routers import fide, knsb
from .rating.exceptions import PlayerNotFoundError

app = FastAPI()

def player_not_found_handler(request: Request, exc: PlayerNotFoundError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.args}
    )

app.include_router(fide.router)
app.include_router(knsb.router)

app.add_exception_handler(PlayerNotFoundError, player_not_found_handler)

@app.get('/')
def index():
    return {"msg": "Hallo Papa!"}
