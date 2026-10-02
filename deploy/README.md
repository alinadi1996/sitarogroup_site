# Sitaro production deployment

Run from the repository root on Linux with Docker Engine and Compose v2.
Use `docker-compose.production.yml` alone: NEVER merge it with the development file.
No deployment or database migration has been performed by this audit.

## Required server configuration

- Configure the server's `.env` yourself using `deploy/production.env.example` as a reference.
  It contains placeholders, not usable credentials. Keep `.env` out of Git; `chmod 600 .env`.
- Generate a NEW secret (the old Compose secret exists in Git history):
  `python -c 'import secrets; print(secrets.token_urlsafe(64))'`.
  Rotating it invalidates existing signed sessions/tokens.
- Set unique `POSTGRES_PASSWORD`, database name/user, and real SMTP credentials/sender.
  STARTTLS: port 587, TLS=true, SSL=false; implicit TLS: 465, TLS=false, SSL=true.
  MAILERS uses Django 6.1's SMTP OPTIONS; legacy EMAIL_* Django settings are not defined.
  The EMAIL_* environment variable names remain supported.
- DNS for `sitarogroup.ir` and `www.sitarogroup.ir` must point to the server.
  Nginx serves these names only; edit its server names/certificate coverage if adding .com.
- Provision a valid TLS certificate covering both names BEFORE starting Nginx.
  `TLS_CERTIFICATE_DIR` must be an absolute server path containing real `fullchain.pem`
  and `privkey.pem`. Do not mount only a Let's Encrypt live directory containing symlinks
  whose archive targets are outside the mount. Arrange renewal, secure copy of renewed
  certificates into this directory, and `docker compose -f docker-compose.production.yml exec nginx nginx -s reload`.
- Permit inbound 80/443 and SSH restricted to your IP through the DigitalOcean firewall.
  Neither web:8000 nor database:5432 is published. Do not expose them separately.
  Use SSH keys, a non-root sudo account, OS security updates and off-server backups.
  Capacity must be sized from measured traffic/media; two workers is an initial setting, not a sizing guarantee.
- Keep Google service-account files under `secrets/` outside the image. An env path alone
  does not mount a host file; add an explicit read-only volume if enabling Search Console.
  Likewise configure support API credentials if enabling AI support.

## First deployment

```sh
docker compose -f docker-compose.production.yml config --quiet
docker compose -f docker-compose.production.yml build web
docker compose -f docker-compose.production.yml up -d --wait db
docker compose -f docker-compose.production.yml run --rm release python manage.py check --deploy
docker compose -f docker-compose.production.yml run --rm release
docker compose -f docker-compose.production.yml run --rm release python manage.py createsuperuser
docker compose -f docker-compose.production.yml up -d --wait web nginx
docker compose -f docker-compose.production.yml exec nginx nginx -t
docker compose -f docker-compose.production.yml ps
curl -I https://sitarogroup.ir/
```

`release` runs migrate then collectstatic, stopping if either fails. Do not run migrations
concurrently or automatically in every Gunicorn worker. Check `showmigrations --plan`
before releases and back up the database before schema changes. On updates, rebuild,
run release, and recreate web/nginx during a maintenance window. Database and media restore
must be tested; rollback may require a database restore, not just an older image.
The audit added `blog/migrations/0006_alter_post_options.py` to reconcile the existing
model's Persian verbose name with migration state. This is metadata-only, not a table/data change.

## Existing data and backups

Production uses NEW project-scoped volumes: postgres_data, static_data, media_data.
It does not automatically reuse the development database or copy repository media.
Before any recreation of existing development containers, inspect their volumes and
export their database with pg_dump; migrate via a verified logical backup/restore.
Do not point PostgreSQL 18 at another major version's data directory.
For PostgreSQL 18 the persistent mount is `/var/lib/postgresql`.

To copy existing media after the release has initialized the volume:
`docker compose -f docker-compose.production.yml cp ./media/. web:/code/media/`.
Then ensure UID/GID 10001 owns the uploaded files (an explicit maintenance container
as root may be needed). Existing volume ownership must also allow UID 10001 to write.
Media here is public: never place private customer files in this directory.

Use scheduled off-server PostgreSQL logical backups plus media backups, encrypted and
with retention/restore drills. Never use `down -v` on production. Changing `.env`
POSTGRES_PASSWORD does NOT rotate credentials of an already initialized PostgreSQL volume.
Pin tested base-image digests for reproducible releases and scan rebuilt images/dependencies.

## Audit limits and remaining issues

- Local `.env` was empty and was NOT edited. Deployment deliberately fails without configuration.
- Docker daemon was unavailable during the audit: Linux image build, Nginx startup,
  PostgreSQL integration, TLS and actual SMTP delivery require server-side validation.
- The old hardcoded key must be rotated; removing it from a file does not remove Git history.
- Python caches and uploaded media are already tracked. Ignore rules prevent NEW files only;
  arrange a deliberate Git-index cleanup without deleting media and back up media first.
- Existing contact submission stores requests; SMTP configuration does not add a contact
  notification workflow. Do not assume messages are emailed unless the view explicitly sends them.
- Built-in health status checks reachability and SELECT 1, not applied migrations or SMTP.
  `check --deploy`, the release command and post-deployment form/email smoke tests are separate gates.
- Public-form rate limiting, abuse protection, upload validation, a restrictive tested CSP,
  external uptime monitoring and dependency vulnerability scanning remain launch tasks.
  HSTS starts at one hour; include-subdomains/preload remain off until all domains support HTTPS.

### Code findings before public launch

- `pages/support.py:95-101` identifies anonymous users with REMOTE_ADDR. Behind Nginx
  this is the proxy address, so anonymous users share a bucket. The default cache in
  `config/settings.py` is process-local, so two Gunicorn workers also have different
  counters. Use a shared Redis cache (add redis dependency/service) and a carefully
  trusted proxy-aware client-IP middleware, or enforce per-IP limits at the edge.
  Never blindly trust client-supplied X-Forwarded-For.
- `tools/views.py:52-66` resolves a hostname to validate public addresses, then urllib
  resolves it again when connecting. DNS rebinding can race that validation. Pin the
  validated IP while preserving TLS hostname verification, or isolate URL-fetching
  with an egress policy denying private/link-local/metadata networks. Redirects must
  receive the same protection. Apply request rate limits before exposing this tool.
- `leads/views.py:15-36` stores contact requests without sending email and without
  rate limiting. Decide on notifications and anti-spam before relying on production mail.
- The bundled database image bootstraps POSTGRES_USER as a superuser. For hardened
  operation provision a separate least-privilege application role/schema and reserve
  the bootstrap admin for administration. Secrets in Docker environment remain readable
  to Docker/server administrators; use protected server access or a secrets manager.
- `tools/views.py` synchronous conversion/network requests occupy workers. The 180s
  Gunicorn timeout and 185s proxy timeout accommodate existing request budgets, but
  queues, CPU/memory limits and load testing are needed before increasing traffic.
- Dependency consistency (`pip check`) passed in the current venv; Gunicorn 26.2.0
  was added to requirements. Its Linux installation and the complete locked dependency
  build could not be tested without Docker. No CVE scan was performed, so this is not
  a vulnerability-free dependency certification. Run pip-audit/container scanning in CI.

### Validation completed locally

Both Compose files passed `config --quiet` using non-secret example/process values.
84 tests passed with an isolated in-memory SQLite database (not PostgreSQL).
The five focused production tests were rerun after tightening placeholder checks;
collectstatic dry-run passed. Migration-state checking found the metadata-only Blog drift
noted above, which was resolved with migration 0006.
`check --deploy` reported only security.W005 / security.W021 (intentional HSTS
include-subdomains/preload defaults). `.env` SHA-256 was identical before/after,
and Git ignores it. No real email/API call, production migration, container restart,
Git commit, or push was performed.

References: [PostgreSQL official image](https://hub.docker.com/_/postgres),
[Gunicorn package](https://pypi.org/project/gunicorn/).
