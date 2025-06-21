import io
import logging
import gzip
import httpx
import xarray as xr
import matplotlib
import tempfile
import os
import numpy as np
import psutil
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
proc = psutil.Process(os.getpid())

MRMS_URL = (
    "https://mrms.ncep.noaa.gov/2D/ReflectivityAtLowestAltitude/"
    "MRMS_ReflectivityAtLowestAltitude.latest.grib2.gz"
)


# Log memory usage at various steps
def log_mem(step: str):
    mem = proc.memory_info().rss / (1024**2)  # in MiB
    logger.info(f"[MEMORY] {step}: {mem:.1f} MiB")


# Fetch and decode the MRMS radar data
async def fetch_and_decode():
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(MRMS_URL)
        resp.raise_for_status()
    log_mem("after download")
    compressed = io.BytesIO(resp.content)
    logger.info(
        "fetch_and_decode: downloaded %d bytes, compressed=%r",
        len(resp.content),
        compressed,
    )
    with gzip.open(compressed, "rb") as f:
        data = f.read()
    log_mem("after decompress to raw bytes")

    # Write the decompressed data to a .grib2 file
    tmp = tempfile.NamedTemporaryFile(suffix=".grib2", delete=False)
    log_mem("after write temp .grib2")

    try:
        tmp.write(data)
        tmp.flush()
        tmp.close()
        logger.info("Wrote decompressed GRIB2 to %s", tmp.name)

        # Open the GRIB2 file with xarray
        ds = xr.open_dataset(tmp.name, engine="cfgrib")
        log_mem("after open_dataset")
        # Load all data into memory
        refl = ds["unknown"].data
        refl = np.where(refl < 0, np.nan, refl)
        log_mem("after loading reflectivity array")
        max_dbz = np.nanmax(refl)
        logger.info(f"Maximum reflectivity in this slice: {max_dbz:.1f} dBZ")
        lats = ds["latitude"].data
        lons = ds["longitude"].data
        log_mem("after loading coords")
        # Adjust longitudes to be in the range [-180, 180]
        lons = np.where(lons > 180, lons - 360, lons)
        min_lat, max_lat = float(np.nanmin(lats)), float(np.nanmax(lats))
        min_lon, max_lon = float(np.nanmin(lons)), float(np.nanmax(lons))
        logger.info(
            f"Dataset bounds → lat: {min_lat:.8f} … {max_lat:.8f},  lon: {min_lon:.8f} … {max_lon:.8f}"
        )
        logger.info(
            "Loaded from disk: refl=%s, lats=%s, lons=%s",
            refl.shape,
            lats.shape,
            lons.shape,
        )
    finally:
        os.unlink(tmp.name)

    return refl, lats, lons


# Render the radar data as a PNG image
async def render_png(refl, lats, lons):
    # fig, ax = plt.subplots(figsize=(8, 6))
    # ax.pcolormesh(lons, lats, refl, cmap="turbo", vmin=0, vmax=75)
    # ax.set_axis_off()
    # buf = io.BytesIO()
    # plt.savefig(buf, bbox_inches="tight", pad_inches=0, transparent=True)
    # buf.seek(0)
    # plt.close(fig)
    # return buf
    norm = mcolors.Normalize(vmin=0, vmax=75)
    cmap = cm.get_cmap("turbo")
    rgba = cmap(norm(refl))  # shape (ny, nx, 4), float32
    img = (rgba * 255).astype("uint8")  # convert to uint8

    # Pillow to save PNG
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="PNG")
    buf.seek(0)
    return buf
