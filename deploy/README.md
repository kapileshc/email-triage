# EC2 deployment notes

The production design intentionally keeps the t3.micro lightweight:

- React is built in GitHub Actions and copied as static files into the existing Tomcat webapp directory.
- FastAPI runs as one systemd worker on `127.0.0.1:8001`.
- OCR runs in Azure Document Intelligence.
- vector retrieval runs in Qdrant Cloud.
- LLM inference runs in Azure Foundry serverless.

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

GitHub Actions deployment requires repository secrets:

- `EC2_HOST`
- `EC2_USER` (normally `ubuntu`)
- `EC2_SSH_KEY`
- `EC2_APP_DIR` (recommended `/opt/email-triage`)
- `TOMCAT_WEBAPP_DIR` (the directory serving `/email-triage`)
