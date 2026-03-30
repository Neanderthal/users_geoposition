# Users Geoposition

QR code geoposition tracking system. Newspaper QR codes capture reader GPS coordinates into XLSX before redirecting to content.

## Commands

- `docker-compose up --build` — run the service
- `python generate_qr.py` — generate QR code PNGs for all campaigns
- `uvicorn app.main:app --reload` — local dev server

## Structure

- `app/main.py` — FastAPI routes
- `app/storage.py` — XLSX persistence
- `app/config.py` — campaign loading, settings
- `app/templates/locate.html` — browser geolocation page
- `campaigns.yaml` — campaign definitions (id → redirect URL)
- `generate_qr.py` — QR code generator CLI
