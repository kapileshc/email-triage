# EC2 deployment notes

The production design intentionally keeps the t3.micro lightweight:

- React is built in GitHub Actions and copied as static files into the existing Tomcat webapp directory.
- FastAPI runs as one systemd worker on `127.0.0.1:8001`.
- OCR runs in Azure Document Intelligence.
- vector retrieval runs in Qdrant Cloud.
- LLM inference runs in Azure Foundry serverless.
- GitHub Actions installs Python dependencies on EC2 only when `requirements.txt` changes.

## One-time EC2 setup

```bash
sudo mkdir -p /opt/email-triage
sudo chown -R ubuntu:ubuntu /opt/email-triage
sudo cp /opt/email-triage/deploy/email-triage.service /etc/systemd/system/email-triage.service
sudo systemctl daemon-reload
sudo systemctl enable email-triage
```

Create `/opt/email-triage/.env` directly on EC2. Never commit production keys.

If Tomcat is behind Apache/Nginx, proxy `/api/` to `http://127.0.0.1:8001/api/` so the React application can use same-origin API calls.

## Recommended swap for a t3.micro

A 1 GB instance can become memory constrained during package installation or service restarts. A 2 GB swap file is a useful safety net:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

Do this once. Swap is not a replacement for RAM; if steady-state memory remains close to 1 GB, move permanently to a larger instance.

## GitHub Actions secrets

The manual deployment workflow requires repository secrets:

- `EC2_HOST`
- `EC2_USER` (normally `ubuntu`)
- `EC2_SSH_KEY`
- `EC2_APP_DIR` (recommended `/opt/email-triage`)
- `TOMCAT_WEBAPP_DIR` (the directory serving `/email-triage`)

The workflow is manually triggered with `workflow_dispatch`. It runs tests and builds React on GitHub-hosted runners, uploads the resulting application, installs backend dependencies only when `requirements.txt` changes, restarts the FastAPI systemd service, and verifies `/api/health`.
