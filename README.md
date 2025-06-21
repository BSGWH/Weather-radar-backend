# Weather Radar API

A Dockerized FastAPI service that fetches the latest MRMS Reflectivity-at-Lowest-Altitude (RALA) GRIB2 data, decodes it with **xarray/cfgrib**, renders it as a PNG, and serves it at `/api/v1/radar/radar.png`. Designed for both local development (Docker Compose) and deployment on Render.

---

## 🚀 Features

- **Live MRMS data**: Fetches and decodes the latest GRIB2 file on every request
- **Server-side rendering**: Generates PNG via Matplotlib
- **Self-contained environment**: Conda-managed dependencies + Docker image
- **Flexible deployment**:
  - Local: Docker Compose
  - Cloud: Docker on [Render.com](https://render.com)

---

## 🔧 Prerequisites

- **Git** (to clone this repo)
- **Docker** & **Docker Compose**

---

## 📥 Installation & Local Development

### 1. Clone the repo

```bash
git clone https://github.com/BSGWH/Weather-radar-backend.git
cd Weather-radar-backend
```

### 2. Run with Docker Compose

```bash
docker compose up
```

Service will be available at http://localhost:8000/api/v1/radar/radar.png
