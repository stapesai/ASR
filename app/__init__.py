# Path: app/__init__.py

from fastapi import FastAPI
import uvicorn
from app.routers.v1 import router as v1_router
# from app.routers.v2 import router as v2_router
from app.config import settings

app = FastAPI(
    docs_url=None,
)

# Include versioned routers
app.include_router(v1_router, prefix="/v1", tags=["v1"])
# app.include_router(v2_router, prefix="/v2", tags=["v2"])

# Include the latest version router as the default (v2 in this case)
# app.include_router(v2_router, tags=["default"])

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
