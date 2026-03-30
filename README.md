# QR Geoposition Tracker

```
        ╔═══╗ ╔═══╗           ╔═══════════════════════════════╗
        ║▓▓▓║ ║▓▓▓║           ║                               ║
        ║▓ ▓║▄║▓ ▓║           ║   QR  GEOPOSITION  TRACKER    ║
        ╚═══╝ ╚═══╝           ║                               ║
        ▓▓▓▓▓▓▓▓▓▓▓           ║   scan  ·  locate  ·  track   ║
        ╔═══╗ ╔═══╗           ║                               ║
        ║▓ ▓║ ║▓ ▓║           ╚═══════════════════════════════╝
        ╚═══╝ ╚═══╝
```

## How it works

```
Reader scans QR  →  Phone asks "Allow location?"  →  GPS saved to Excel  →  Reader sees your webpage
                                                      (if denied, reader
                                                       still gets redirected)
```

---

## Quick Install

You need:
- A Linux server (VPS) — Ubuntu, Debian, Amazon Linux, CentOS, or RHEL
- A domain name pointed to the server (A record)
- A computer with Git, Python 3.12+, and Ansible installed (Mac, Linux, or Windows with WSL)

### Step 1. Get the code

```bash
git clone https://github.com/Neanderthal/users_geoposition.git
cd users_geoposition
```

### Step 2. Set up your campaigns

Open `campaigns.yaml` and add your entries:

```yaml
campaigns:
  spring-ad:
    label: "Spring Newspaper Ad"
    redirect_url: "https://your-site.com/spring-promo"
```

- The key (`spring-ad`) becomes part of the QR link — keep it short, no spaces
- `redirect_url` is where readers end up after scanning

### Step 3. Configure the server

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

### Step 4. Deploy

One command installs Docker, sets up HTTPS, and starts the app:

```bash
ansible-playbook -i inventory.ini deploy.yml
```

The playbook auto-detects your server's OS and installs the right packages. Tested on Ubuntu, Debian, Amazon Linux, and CentOS.

### Step 5. Generate QR codes

```bash
cd ..
pip install -r requirements.txt
BASE_URL=https://geo.yourdomain.com python generate_qr.py
```

Print-ready QR images are in the `qr_codes/` folder. Send them to your designer or printer.

That's it. The system is running.

---

## Setup on Windows

Ansible doesn't run natively on Windows. Here's how to set it up:

### Option A: WSL (recommended)

1. Open PowerShell as Administrator and install WSL:

   ```powershell
   wsl --install
   ```

2. Restart your computer, then open the Ubuntu app from the Start menu.

3. Inside WSL, install what you need:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip ansible git
   ```

4. Clone the project and follow the Quick Install steps above — everything works the same inside WSL.

### Option B: Without WSL

If you can't use WSL, you can still deploy manually:

1. Install [Python 3.12+](https://www.python.org/downloads/) and [Git](https://git-scm.com/download/win)

2. Clone the repo and generate QR codes locally:

   ```cmd
   git clone https://github.com/Neanderthal/users_geoposition.git
   cd users_geoposition
   pip install -r requirements.txt
   set BASE_URL=https://geo.yourdomain.com
   python generate_qr.py
   ```

3. SSH into your server and set it up manually:

   ```cmd
   ssh root@geo.yourdomain.com
   ```

   On the server:

   ```bash
   # Install Docker (Ubuntu/Debian)
   curl -fsSL https://get.docker.com | sh

   # Clone and start the app
   git clone https://github.com/Neanderthal/users_geoposition.git /opt/geoposition
   cd /opt/geoposition

   # Edit docker-compose.yml — set BASE_URL and API_KEY
   nano docker-compose.yml

   # Start
   docker compose up -d --build
   ```

   Then install Nginx and Certbot for HTTPS — see `ansible/templates/nginx.conf.j2` for the config to copy.

---

## Downloading the collected data

Replace `your-secret` with the `api_key` you set earlier:

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

## Supported server operating systems

The Ansible playbook auto-detects the OS and adapts. To add support for a new distro, create a file in `ansible/vars/` (e.g. `Suse.yml`) with the correct package names.

| OS | Tested | Notes |
|---|---|---|
| Ubuntu 22.04 / 24.04 | Yes | Docker from official APT repo |
| Debian 11 / 12 | Yes | Docker from official APT repo |
| Amazon Linux 2023 | Yes | Docker from Amazon repos, Compose/Buildx installed as binaries |
| CentOS / RHEL 8+ | Yes | Same as Amazon Linux path |

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Location not captured | Browser blocks geolocation over HTTP | Make sure your domain uses HTTPS (the Ansible setup handles this) |
| 404 when scanning | Campaign ID in URL doesn't match `campaigns.yaml` | Check for typos, redeploy after editing |
| Excel file is empty | Readers are denying the location prompt | Expected — they still get redirected, you just don't get their coordinates |
| Ansible fails at certificate | Domain DNS not pointing to server | Add an A record pointing your domain to the server IP, wait a few minutes |
| `ansible-playbook` not found | Ansible not installed | `pip install ansible` or use WSL on Windows |
| SSH connection timeout | Firewall blocking port 22 | Check your cloud provider's security group / firewall rules |

---

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
│   ├── vars/
│   │   ├── Debian.yml       # Package names for Debian/Ubuntu
│   │   └── RedHat.yml       # Package names for Amazon Linux/CentOS
│   ├── templates/           # Nginx and Docker configs
│   ├── inventory.example.ini
│   └── vars.example.yml
├── generate_qr.py           # QR code generator
├── campaigns.yaml           # Your campaigns
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```
