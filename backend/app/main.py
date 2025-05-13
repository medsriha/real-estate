from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from app.api.v1.router import api_router
from app.core.config import settings

# Configure logging
os.makedirs(settings.LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{settings.LOGS_DIR}/main.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("real-estate-api")

app = FastAPI(title=settings.PROJECT_NAME)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.RELOAD) 