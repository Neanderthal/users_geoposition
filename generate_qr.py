#!/usr/bin/env python3
"""Generate print-ready QR codes for all campaigns defined in campaigns.yaml."""

from pathlib import Path

import qrcode
import yaml

BASE_DIR = Path(__file__).resolve().parent
CAMPAIGNS_FILE = BASE_DIR / "campaigns.yaml"
OUTPUT_DIR = BASE_DIR / "qr_codes"


def main() -> None:
    with open(CAMPAIGNS_FILE) as f:
        data = yaml.safe_load(f)

    campaigns = data.get("campaigns", {})
    if not campaigns:
        print("No campaigns found in campaigns.yaml")
        return

    # Read BASE_URL from environment or prompt
    import os

    base_url = os.getenv("BASE_URL", "").rstrip("/")
    if not base_url:
        base_url = input("Enter the public BASE_URL (e.g. https://geo.example.com): ").rstrip("/")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for campaign_id, config in campaigns.items():
        url = f"{base_url}/track/{campaign_id}"
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        out_path = OUTPUT_DIR / f"{campaign_id}.png"
        img.save(str(out_path))
        print(f"  {config.get('label', campaign_id)}")
        print(f"    URL: {url}")
        print(f"    QR:  {out_path}")
        print()

    print(f"Generated {len(campaigns)} QR code(s) in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
