# Ubuntu 24.04 LTS Installation

This deployment uses Docker Compose. PostgreSQL, Django/Gunicorn, the continuous
email collector, daily report cron process, and Nginx run as separate containers.

## 1. Prepare the server

Use Ubuntu **24.04 LTS** and a sudo-enabled account. Point the DNS records for
`db.krissdrilling.com` and `www.db.krissdrilling.com` to the server before the
HTTPS step.

```bash
sudo apt update
sudo apt install -y ca-certificates curl git certbot ufw
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Log out and back in so the Docker group change takes effect. Then verify:

```bash
docker --version
docker compose version
```

## 2. Deploy the application

```bash
sudo mkdir -p /opt/kriss-rig-app
sudo chown "$USER":"$USER" /opt/kriss-rig-app
git clone <YOUR_REPOSITORY_URL> /opt/kriss-rig-app
cd /opt/kriss-rig-app
cp .env.example .env
chmod 600 .env
```

Generate secrets and place the output in `.env`:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
python3 -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
nano .env
```

Set at minimum `DJANGO_SECRET_KEY`, `EMAIL_COLLECTION_FERNET_KEY`, all `DB_*`
values, `ALLOWED_HOSTS`, and the outbound SMTP settings. Do not reuse the Django
secret as the Fernet key.

For AI-assisted extraction (Claude Opus 4.8), also set `ANTHROPIC_API_KEY`. Leave
`EMAIL_REPORTS_AI_EXTRACTOR` blank to fall back to rules-only classification — the
system runs fully without an API key, just without the AI upgrade layer.

Build and start the core services:

```bash
docker compose build
docker compose up -d db app email_collector cron
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser
docker compose ps
```

At this point the application is available temporarily at
`http://SERVER_IP:8000`.

## 3. Configure HTTPS

Allow only SSH, HTTP, and HTTPS through the firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

Issue the certificate before starting the Nginx production profile:

```bash
sudo certbot certonly --standalone \
  -d db.krissdrilling.com \
  -d www.db.krissdrilling.com \
  --agree-tos \
  --email it.admin@krissdrilling.com \
  --no-eff-email

docker compose --profile production up -d
```

Verify `https://db.krissdrilling.com`. Test renewal with:

```bash
sudo certbot renew --dry-run
```

Certbot renews the host certificate, but Nginx must reload it. Add this deploy
hook:

```bash
sudo tee /etc/letsencrypt/renewal-hooks/deploy/reload-kriss-nginx.sh >/dev/null <<'EOF'
#!/bin/sh
cd /opt/kriss-rig-app
docker compose --profile production exec -T nginx nginx -s reload
EOF
sudo chmod 750 /etc/letsencrypt/renewal-hooks/deploy/reload-kriss-nginx.sh
```

## 4. Configure report mailboxes

1. Sign in as the Django superuser.
2. Open `/admin/email_reports/emailaccount/` and add each mailbox.
3. Add approved addresses/domains under **Sender registries**.
4. Add expected schedules under **Expected reports**.
5. Open `/email-collection/` to verify mailbox health and processing status.

Credential payloads are entered as JSON and encrypted before database storage.

IMAP password or app-password example:

```json
{"password":"application-specific-password"}
```

OAuth2 example for Microsoft Graph, Microsoft IMAP, Gmail API, or Gmail IMAP:

```json
{
  "access_token":"initial-access-token",
  "refresh_token":"long-lived-refresh-token",
  "client_id":"oauth-client-id",
  "client_secret":"oauth-client-secret",
  "tenant_id":"microsoft-tenant-id"
}
```

For Graph shared mailboxes, select **Microsoft Graph API**, enter the shared
mailbox address, and enable **shared mailbox**. The Azure application must have
the appropriate delegated or application mail permissions. Gmail API accounts
need a scope that can read messages; removing the unread label also requires a
modify scope.

## 5. Verify automation

```bash
docker compose logs --tail=100 email_collector
docker compose exec app python manage.py monitor_email_reports --once
docker compose exec app python manage.py check_missing_reports
docker compose exec app python manage.py check --deploy
```

Send a test report from an approved sender. Confirm that the original `.eml`,
attachments, extraction result, processing history, acknowledgement, and
dashboard record are created.

## Operations

Update the deployment:

```bash
cd /opt/kriss-rig-app
git pull
docker compose build
docker compose up -d
docker compose exec app python manage.py migrate
```

Backup PostgreSQL:

```bash
mkdir -p /opt/backups
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  | gzip > "/opt/backups/rig_app_$(date +%F_%H%M).sql.gz"
```

Also back up the Docker `media_data` volume because it contains the archived
emails and attachments.
