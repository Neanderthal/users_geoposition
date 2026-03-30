# QR Geoposition Tracker

Generates QR codes for print media (newspapers, flyers). When scanned, the QR code opens a page that captures the reader's GPS coordinates, saves them to an XLSX file, and redirects to your content URL. No personal data is collected — only timestamp, latitude, and longitude.

## Requirements

- A VPS with Ubuntu/Debian
- Domain name pointed to the server
- Python 3.12+ on your local machine (for QR code generation)

## One-Click Deployment (Ansible)

### 1. Configure

```bash
cd ansible
cp inventory.example.ini inventory.ini
cp vars.example.yml vars.yml
```

Edit `inventory.ini` — set your server host and SSH user:

```ini
[geoposition]
geo.yourdomain.com ansible_user=root
```

Edit `vars.yml`:

```yaml
domain: geo.yourdomain.com
email: you@example.com       # Let's Encrypt
api_key: your-secret-key     # for download API
app_dir: /opt/geoposition
```

Edit `campaigns.yaml` (in project root) with your campaigns:

```yaml
campaigns:
  spring-ad-2026:
    label: "Spring 2026 Newspaper Ad"
    redirect_url: "https://your-site.com/spring-promo"
```

### 2. Deploy

```bash
ansible-playbook -i inventory.ini deploy.yml
```

This installs Docker, Nginx, Certbot (TLS), deploys the app, and starts everything. Done.

### 3. Generate QR codes

```bash
cd ..
pip install -r requirements.txt
BASE_URL=https://geo.yourdomain.com python generate_qr.py
```

Print-ready PNGs are saved to `qr_codes/`.

## Manual Installation

If you prefer not to use Ansible:

### 1. Clone and configure

```bash
git clone <repo-url> users_geoposition
cd users_geoposition
```

### 2. Set environment variables

Edit `docker-compose.yml`:

```yaml
environment:
  - BASE_URL=https://geo.yourdomain.com
  - API_KEY=your-secret-key
```

### 3. Start

```bash
docker compose up -d --build
```

The app listens on port `8000`. Put it behind a reverse proxy with TLS (see `ansible/templates/nginx.conf.j2` for an example).

## Download API

All API endpoints require the `X-Api-Key` header.

### List campaigns

```bash
curl -H 'X-Api-Key: your-secret-key' https://geo.yourdomain.com/api/campaigns
```

Response:

```json
{
  "spring-ad-2026": {"label": "Spring 2026 Newspaper Ad", "has_data": true}
}
```

### Download XLSX

```bash
curl -H 'X-Api-Key: your-secret-key' \
  https://geo.yourdomain.com/api/download/spring-ad-2026 \
  -o spring-ad-2026.xlsx
```

Returns the XLSX file with columns: `timestamp`, `latitude`, `longitude`.

## Campaign Management

### Adding a campaign

1. Add entry to `campaigns.yaml`
2. Restart: `docker compose restart`
3. Generate QR: `BASE_URL=https://geo.yourdomain.com python generate_qr.py`
4. Print the PNG from `qr_codes/`

### Redeploying after changes

```bash
cd ansible
ansible-playbook -i inventory.ini deploy.yml
```

Or manually:

```bash
git pull
docker compose up -d --build
```

## How the Scan Flow Works

1. User scans QR code in newspaper
2. Browser opens `https://geo.yourdomain.com/track/spring-ad-2026`
3. Page requests GPS permission (shows a loading spinner)
4. If allowed — coordinates are sent to the server and saved to XLSX
5. User is redirected to the campaign's `redirect_url`
6. If denied or timed out (8s) — user is redirected anyway, no data saved

## Troubleshooting

**Geolocation not working:**
Browser geolocation requires HTTPS. Verify your TLS certificate is valid.

**404 on scan:**
Campaign ID in URL must match a key in `campaigns.yaml`. Restart container after editing.

**Empty XLSX:**
Users may be denying location permission. Test on a mobile device with GPS enabled.

**Ansible fails at certbot:**
Ensure your domain DNS A record points to the server and port 80 is open.
