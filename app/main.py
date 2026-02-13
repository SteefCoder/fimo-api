from fastapi import FastAPI

from .routers import fide, knsb


description = """
An API to find and calculate chess ratings.

You can get rating and player information from all players registered with FIDE (the World Chess Federation)
and the KNSB (the Dutch Chess Federation, Koninklijke Nederlandse Schaakbond).

You can also calculate your new expected (KNSB-)rating based on the games you have played in the last month.
"""

app = FastAPI(
    title="FiMO chess API",
    description=description,
    version="0.0.1",
    license_info={
        "name": "GPLv3",
        # "identifier": "GPL-3.0-or-later",
        "url": "https://www.gnu.org/licenses/gpl-3.0.html"
    },
    docs_url=None,
    redoc_url="/docs",
)

app.include_router(fide.router)
app.include_router(knsb.router)
