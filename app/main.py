from fastapi import FastAPI
from app.radar.router import router as radar_router
from fastapi.middleware.cors import CORSMiddleware
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
app = FastAPI()

app.include_router(radar_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
