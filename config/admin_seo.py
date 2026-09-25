"""Superuser-only SEO overview and read-only Search Console integration."""

from datetime import timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from blog.models import Post
from portfolio.models import Project


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def public_site_status():
    """Probe only the fixed, server-configured public URL; never follow redirects."""
    cached = cache.get("sitaro-public-site-status")
    if cached is not None:
        return cached
    request = Request(settings.SITARO_PUBLIC_SITE_URL, method="HEAD",
                      headers={"User-Agent": "SitaroAdminHealth/1.0"})
    try:
        with build_opener(_NoRedirect).open(request, timeout=4) as response:
            status = response.status
    except HTTPError as exc:
        status = exc.code
    except (URLError, TimeoutError, OSError):
        status = None
    result = {"reachable": status is not None and status < 400, "http_status": status}
    cache.set("sitaro-public-site-status", result, 300)
    return result


def search_console_status():
    """Fetch aggregate search performance for the last complete 28-day period."""
    site_url = settings.SITARO_GSC_SITE_URL
    credentials_file = settings.SITARO_GSC_CREDENTIALS_FILE
    if not site_url or not credentials_file:
        return {"state": "unconfigured"}
    if not Path(credentials_file).is_file():
        return {"state": "missing_credentials"}

    cache_key = f"sitaro-gsc-{site_url}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession

        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        # Search Console data may lag. Exclude the most recent three days.
        end_date = timezone.localdate() - timedelta(days=3)
        start_date = end_date - timedelta(days=27)
        endpoint = ("https://www.googleapis.com/webmasters/v3/sites/"
                    f"{quote(site_url, safe='')}/searchAnalytics/query")
        response = AuthorizedSession(credentials).post(
            endpoint,
            json={"startDate": start_date.isoformat(), "endDate": end_date.isoformat(),
                  "rowLimit": 1},
            timeout=8,
        )
        response.raise_for_status()
        rows = response.json().get("rows", [])
        row = rows[0] if rows else {}
        result = {
            "state": "connected",
            "clicks": int(row.get("clicks", 0)),
            "impressions": int(row.get("impressions", 0)),
            "ctr": round(float(row.get("ctr", 0)) * 100, 1),
            "position": round(float(row.get("position", 0)), 1),
            "start_date": start_date,
            "end_date": end_date,
        }
        cache.set(cache_key, result, 900)
        return result
    except (ImportError, ValueError, OSError):
        return {"state": "setup_error"}
    except Exception:
        # Do not expose Google response bodies or credential details in admin HTML.
        return {"state": "connection_error"}


class SEOOverviewView(TemplateView):
    admin_site = None  # Passed by Unfold's SITE_VIEWS loader.
    template_name = "admin/seo_overview.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            database_ok = cursor.fetchone()[0] == 1
        context.update(self.admin_site.each_context(self.request))
        context.update({
            "title": "بررسی سئو و وضعیت سایت",
            "post_count": Post.objects.count(),
            "project_count": Project.objects.filter(is_published=True).count(),
            "database_ok": database_ok,
            "public_site": public_site_status(),
            "search_console": search_console_status(),
            "search_console_property": settings.SITARO_GSC_SITE_URL,
            "robots_url": reverse("robots_txt"),
            "sitemap_url": reverse("sitemap_xml"),
        })
        return context
