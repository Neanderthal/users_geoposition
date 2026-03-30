# QR Geoposition Tracker

Print a QR code in a newspaper or flyer. When a reader scans it, the system silently records their GPS location into an Excel file, then sends them to your webpage. No names, no cookies, no personal data — just coordinates and a timestamp.

## How it works

```
Reader scans QR  →  Phone asks "Allow location?"  →  GPS saved to Excel  →  Reader sees your webpage
                                                      (if denied, reader
                                                       still gets redirected)
```

---

## Quick Install

You need: a Linux server (VPS) with a domain name pointed to it, and a computer with Ansible installed.

**Step 1.** Get the code:

```bash
git clone https://github.com/Neanderthal/users_geoposition.git
cd users_geoposition
```

**Step 2.** Set up your campaigns — open `campaigns.yaml` and add your entries:

```yaml
campaigns:
  spring-ad:
    label: "Spring Newspaper Ad"
    redirect_url: "https://your-site.com/spring-promo"
```

- The key (`spring-ad`) becomes part of the QR link — keep it short, no spaces
- `redirect_url` is where readers end up after scanning

**Step 3.** Configure the server — go into the `ansible/` folder and fill in two files:

```bash
cd ansible
cp inventory.example.ini inventory.ini
cp vars.example.yml vars.yml
```

In `inventory.ini`, put your server address:

```ini
[geoposition]
geo.yourdomain.com ansible_user=root
```

In `vars.yml`, fill in your details:

```yaml
domain: geo.yourdomain.com       # your domain
email: you@example.com           # for the free TLS certificate
api_key: pick-a-secret-password  # needed to download the Excel files later
app_dir: /opt/geoposition        # where the app lives on the server
```

**Step 4.** Deploy — one command does everything (installs Docker, sets up HTTPS, starts the app):

```bash
ansible-playbook -i inventory.ini deploy.yml
```

**Step 5.** Generate QR codes to print:

```bash
cd ..
pip install -r requirements.txt
BASE_URL=https://geo.yourdomain.com python generate_qr.py
```

Your print-ready QR images are in the `qr_codes/` folder. Send them to your designer or printer.

That's it. The system is running.

---

## Downloading the collected data

Open this URL in a browser or use the command below — replace `your-secret` with the `api_key` you set earlier:

```bash
curl -H 'X-Api-Key: your-secret' \
  https://geo.yourdomain.com/api/download/spring-ad \
  -o spring-ad.xlsx
```

The Excel file has three columns:

| timestamp | latitude | longitude |
|---|---|---|
| 2026-03-30T11:04:24+00:00 | 51.5074 | -0.1278 |

To see which campaigns have data:

```bash
curl -H 'X-Api-Key: your-secret' https://geo.yourdomain.com/api/campaigns
```

---

## Adding a new campaign later

1. Add a new entry to `campaigns.yaml`
2. Redeploy: `cd ansible && ansible-playbook -i inventory.ini deploy.yml`
3. Regenerate QR codes: `BASE_URL=https://geo.yourdomain.com python generate_qr.py`
4. Print the new QR from `qr_codes/`

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Location not captured | Browser blocks geolocation over HTTP | Make sure your domain uses HTTPS (the Ansible setup handles this) |
| 404 when scanning | Campaign ID in URL doesn't match `campaigns.yaml` | Check for typos, redeploy after editing |
| Excel file is empty | Readers are denying the location prompt | Expected — they still get redirected, you just don't get their coordinates |
| Ansible fails at certificate | Domain DNS not pointing to server | Add an A record pointing your domain to the server IP, wait a few minutes |

## Project structure

```
├── app/
│   ├── main.py              # Web server (FastAPI)
│   ├── storage.py           # Saves GPS data to Excel
│   ├── config.py            # Settings
│   └── templates/
│       └── locate.html      # The page readers see (briefly)
├── ansible/
│   ├── deploy.yml           # One-click server setup
│   ├── inventory.example.ini
│   ├── vars.example.yml
│   └── templates/           # Nginx and Docker configs
├── generate_qr.py           # QR code generator
├── campaigns.yaml           # Your campaigns
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```
