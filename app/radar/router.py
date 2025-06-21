from fastapi import Response, HTTPException, APIRouter, Request
from app.radar.service import fetch_and_decode, render_png
from functools import lru_cache
from datetime import datetime, timedelta
import psutil
import logging
import os
from slowapi import Limiter
from slowapi.util import get_remote_address


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/radar", tags=["radar"])
limiter = Limiter(key_func=get_remote_address)


cache = {}

proc = psutil.Process(os.getpid())


def log_mem(step: str):
    mem = proc.memory_info().rss / (1024**2)  # in MiB
    logger.info(f"[MEMORY] {step}: {mem:.1f} MiB")


@router.get("/radar.png")
@limiter.limit("10/minute")
async def radar_image(request: Request):
    cache_key = "radar_image"
    now = datetime.now()

    if cache_key in cache:
        cached_data, timestamp = cache[cache_key]
        if now - timestamp < timedelta(minutes=2):
            logger.info("Returning cached radar image")
            return Response(content=cached_data, media_type="image/png")
    logger.info("Received request for radar image")
    try:
        logger.info("Fetching and decoding radar data")
        refl, lats, lons = await fetch_and_decode()
        log_mem("after fetch_and_decode")
        png = await render_png(refl, lats, lons)
        log_mem("after render_png")
        png_data = png.read()
        log_mem("after read png data")
        cache[cache_key] = (png_data, now)
        return Response(content=png_data, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
