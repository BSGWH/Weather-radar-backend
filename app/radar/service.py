import io
import logging
import gzip
import httpx
import xarray as xr
import matplotlib
import tempfile
import os
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

MRMS_URL = (
    "https://mrms.ncep.noaa.gov/2D/ReflectivityAtLowestAltitude/"
    "MRMS_ReflectivityAtLowestAltitude.latest.grib2.gz"
)


# Fetch and decode the MRMS radar data
async def fetch_and_decode():
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(MRMS_URL)
        resp.raise_for_status()
    compressed = io.BytesIO(resp.content)
    logger.info(
        "fetch_and_decode: downloaded %d bytes, compressed=%r",
        len(resp.content),
        compressed,
    )
    with gzip.open(compressed, "rb") as f:
        data = f.read()

    # Write the decompressed data to a .grib2 file
    tmp = tempfile.NamedTemporaryFile(suffix=".grib2", delete=False)

    try:
        tmp.write(data)
        tmp.flush()
        tmp.close()
        logger.info("Wrote decompressed GRIB2 to %s", tmp.name)

        # Open the GRIB2 file with xarray
        ds = xr.open_dataset(tmp.name, engine="cfgrib")
        # Load all data into memory
        refl = ds["unknown"].data
        refl = np.where(refl < 0, np.nan, refl)
        max_dbz = np.nanmax(refl)
        logger.info(f"Maximum reflectivity in this slice: {max_dbz:.1f} dBZ")
        lats = ds["latitude"].data
        lons = ds["longitude"].data
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
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pcolormesh(lons, lats, refl, cmap="turbo", vmin=0, vmax=75)
    ax.set_axis_off()
    buf = io.BytesIO()
    plt.savefig(buf, bbox_inches="tight", pad_inches=0, transparent=True)
    buf.seek(0)
    plt.close(fig)
    return buf
