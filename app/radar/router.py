from fastapi import Response, HTTPException, APIRouter
from app.radar.service import fetch_and_decode, render_png

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/radar", tags=["radar"])


@router.get("/radar.png")
async def radar_image():
    logger.info("Received request for radar image")
    try:
        logger.info("Fetching and decoding radar data")
        refl, lats, lons = await fetch_and_decode()
        png = await render_png(refl, lats, lons)
        return Response(content=png.read(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
