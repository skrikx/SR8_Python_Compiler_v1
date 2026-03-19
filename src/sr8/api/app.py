from __future__ import annotations

from fastapi import FastAPI

from sr8.api.routes import router
from sr8.version import __version__

app = FastAPI(title="SR8 API", version=__version__)
app.include_router(router)
