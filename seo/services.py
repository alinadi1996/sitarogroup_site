"""Single source of truth for public SEO metadata and structured data."""

import re
from urllib.parse import urljoin, urlsplit

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import strip_tags

from .models import SchemaMode, SiteSEOSettings, StaticPageSEO, validate_schema


STATIC_ROUTES = {
    "home": "home", "contact": "leads:contact", "tools": "tools:index",
    "portfolio_index": "portfolio:project_list", "blog_index": "blog:blog_list",
}
STATIC_DEFAULTS = {
    "home": ("گروه سیتارو | طراحی سایت اختصاصی، جنگو، وردپرس و سئو",
             "طراحی و توسعه وب‌سایت‌های اختصاصی با Django و WordPress، سئو تکنیکال و بهینه‌سازی سرعت توسط گروه سیتارو."),
    "contact": ("تماس با ما و شروع همکاری | گروه سیتارو",
                "برای طراحی سایت، توسعه اختصاصی، سئو، بهینه‌سازی عملکرد یا اتوماسیون، درخواست همکاری خود را برای گروه سیتارو ارسال کنید."),
    "tools": ("ابزارهای رایگان سئو و بررسی سایت | Sitaro",
              "ابزارهای رایگان Sitaro برای بررسی سئو، سرعت، ساختار فنی، محتوا و بهینه‌سازی وب‌سایت."),
    "portfolio_index": ("نمونه‌کارهای طراحی سایت و توسعه وب | گروه سیتارو",
                        "مطالعه نمونه‌کارهای طراحی و توسعه وب، جنگو، وردپرس، سئو و بهینه‌سازی عملکرد در گروه سیتارو."),
    "blog_index": ("مجله سیتارو | طراحی سایت، جنگو و سئو",
                   "مقاله‌ها و تجربه‌های گروه سیتارو درباره طراحی محصول، توسعه جنگو، وردپرس، سئو و بهینه‌سازی عملکرد وب."),
}
TOOL_ROUTES = {
    "website_analyzer": "website-analyzer", "serp_preview": "serp-preview",
    "image_converter": "image-optimizer", "schema_generator": "schema-generator",
    "sitemap_robots_generator": "sitemap-robots-generator",
}
TOOL_DEFAULTS = {
    "website_analyzer": ("تحلیل سایت و تست سرعت Google PageSpeed | Sitaro", "اطلاعات پایه سایت و گزارش سرعت موبایل Google PageSpeed را بررسی کنید."),
    "serp_preview": ("پیش‌نمایش نتیجه گوگل و بررسی متا تگ | Sitaro", "با ابزار رایگان Sitaro ظاهر تقریبی عنوان، آدرس و توضیحات صفحه را در نتایج گوگل برای موبایل و دسکتاپ بررسی کنید."),
    "image_converter": ("تبدیل تصویر به WebP، PNG و JPEG | Sitaro", "تصاویر تکی یا ZIP را به WebP، PNG و JPEG تبدیل کنید."),
    "schema_generator": ("ساخت اسکیما JSON-LD آنلاین و رایگان | Sitaro", "با ابزار رایگان Sitaro کد اسکیما برای سازمان، کسب‌وکار محلی، مقاله، محصول و Breadcrumb بسازید و JSON-LD آماده دریافت کنید."),
    "sitemap_robots_generator": ("ساخت Sitemap XML و Robots.txt آنلاین | Sitaro", "با ابزار رایگان Sitaro فایل sitemap.xml و robots.txt آماده برای وب‌سایت خود بسازید و دانلود کنید."),
}


def site_settings():
    return SiteSEOSettings.objects.filter(pk=1).first()


def _plain(value, limit=160):
    return re.sub(r"\s+", " ", strip_tags(str(value or ""))).strip()[:limit]


def _site_base(settings_obj=None):
    value = (settings_obj.site_url if settings_obj else "https://sitarogroup.ir/").strip()
    return value.rstrip("/") + "/"


def _absolute(value, request=None, settings_obj=None):
    if not value:
        return ""
    if urlsplit(str(value)).scheme in ("http", "https"):
        return str(value)
    return urljoin(_site_base(settings_obj), str(value).lstrip("/"))


def get_seo_title(obj, request=None):
    settings_obj = site_settings()
    return (getattr(obj, "seo_title", "") or getattr(obj, "meta_title", "") or
            getattr(obj, "title", "") or getattr(obj, "name", "") or
            (settings_obj.default_seo_title if settings_obj else STATIC_DEFAULTS["home"][0]))


def get_meta_description(obj):
    settings_obj = site_settings()
    return (_plain(getattr(obj, "meta_description", ""), 300) or
            _plain(getattr(obj, "summary", "") or getattr(obj, "short_description", ""), 300) or
            _plain(getattr(obj, "content", "") or getattr(obj, "introduction", ""), 160) or
            (settings_obj.default_meta_description if settings_obj else STATIC_DEFAULTS["home"][1]))


def get_canonical_url(obj, request):
    custom = getattr(obj, "canonical_url", "")
    if custom and urlsplit(custom).scheme in ("http", "https"):
        return custom
    path = obj.get_absolute_url() if obj and hasattr(obj, "get_absolute_url") else request.path
    return _absolute(path or request.path, request, site_settings())


def get_robots_directive(obj):
    return ("index" if getattr(obj, "robots_index", True) else "noindex") + ", " + (
        "follow" if getattr(obj, "robots_follow", True) else "nofollow")


def _image_url(image, request, settings_obj=None):
    try:
        return _absolute(image.url, request, settings_obj) if image else ""
    except (AttributeError, ValueError):
        return ""


def get_og_data(obj, request):
    settings_obj = site_settings()
    image = (_image_url(getattr(obj, "og_image", None), request, settings_obj) or
             _image_url(getattr(obj, "cover", None), request, settings_obj) or
             _image_url(settings_obj.default_og_image, request, settings_obj) if settings_obj else
             _image_url(getattr(obj, "og_image", None), request) or _image_url(getattr(obj, "cover", None), request))
    return {
        "title": getattr(obj, "og_title", "") or get_seo_title(obj, request),
        "description": getattr(obj, "og_description", "") or get_meta_description(obj),
        "image": image,
        "type": "article" if getattr(obj, "_meta", None) and obj._meta.label == "blog.Post" else
                (settings_obj.default_og_type if settings_obj else "website"),
        "site_name": settings_obj.site_name if settings_obj else "گروه سیتارو",
    }


def _breadcrumb(label, parent_label, parent_path, current_url, request):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": parent_label,
                 "item": _absolute(parent_path, request, site_settings())},
                {"@type": "ListItem", "position": 2, "name": label, "item": current_url},
            ]}


def _site_schema(settings_obj):
    if not settings_obj:
        return []
    base = _site_base(settings_obj)
    organization = {"@context": "https://schema.org", "@type": "Organization",
                    "@id": base + "#organization", "name": settings_obj.organization_name,
                    "url": base}
    if settings_obj.legal_name:
        organization["legalName"] = settings_obj.legal_name
    if settings_obj.organization_description:
        organization["description"] = settings_obj.organization_description
    if settings_obj.contact_email:
        organization["email"] = settings_obj.contact_email
    if settings_obj.contact_phone:
        organization["telephone"] = settings_obj.contact_phone
    if logo := _image_url(settings_obj.organization_logo, settings_obj=settings_obj, request=None):
        organization["logo"] = logo
    if settings_obj.social_links:
        organization["sameAs"] = [link for link in settings_obj.social_links if isinstance(link, str) and link.startswith("https://")]
    website = {"@context": "https://schema.org", "@type": "WebSite",
               "@id": base + "#website", "name": settings_obj.site_name, "url": base,
               "publisher": {"@id": organization["@id"]}}
    return [organization, website]


def get_schema_data(obj, request):
    if getattr(obj, "robots_index", True) is False:
        return []
    mode = getattr(obj, "schema_mode", SchemaMode.AUTO)
    if mode == SchemaMode.DISABLED:
        return []
    if mode == SchemaMode.CUSTOM:
        data = getattr(obj, "custom_schema", None)
        try:
            validate_schema(data)
        except ValidationError:
            return []
        return data if isinstance(data, list) else [data] if data else []

    from blog.models import Post
    from portfolio.models import Project
    from tools.models import Tool

    current_url = get_canonical_url(obj, request)
    settings_obj = site_settings()
    if isinstance(obj, Post):
        article = {"@context": "https://schema.org", "@type": "BlogPosting",
                   "headline": obj.title, "description": get_meta_description(obj),
                   "datePublished": obj.datetime_created.isoformat(),
                   "dateModified": obj.datetime_updated.isoformat(),
                   "author": {"@type": "Person", "name": str(obj.author)},
                   "mainEntityOfPage": current_url}
        if image := get_og_data(obj, request)["image"]:
            article["image"] = image
        if settings_obj:
            article["publisher"] = {"@id": _site_base(settings_obj) + "#organization"}
        return [article]
    if isinstance(obj, Project):
        result = [_breadcrumb(obj.title, "نمونه‌کارها", reverse("portfolio:project_list"), current_url, request)]
        if obj.title and obj.summary and obj.cover:
            result.append({"@context": "https://schema.org", "@type": "CreativeWork",
                           "name": obj.title, "description": obj.summary, "url": current_url,
                           "image": _image_url(obj.cover, request, settings_obj)})
        return result
    if isinstance(obj, Tool) and obj.is_available and obj.slug in TOOL_ROUTES.values() and obj.get_absolute_url():
        result = []
        if obj.slug in {"serp-preview", "schema-generator", "sitemap-robots-generator"}:
            result.append(_breadcrumb(obj.title, "ابزارها", reverse("tools:index"), current_url, request))
        result.append({"@context": "https://schema.org", "@type": "WebApplication",
                       "name": obj.title, "description": obj.short_description, "url": current_url})
        return result
    if isinstance(obj, StaticPageSEO) and obj.page_key == "home":
        return _site_schema(settings_obj)
    return []


def build_seo(obj, request, *, title=None, description=None, canonical_path=None, noindex=False):
    settings_obj = site_settings()
    title = getattr(obj, "seo_title", "") or title or get_seo_title(obj, request)
    description = getattr(obj, "meta_description", "") or description or get_meta_description(obj)
    canonical = getattr(obj, "canonical_url", "") or (
        _absolute(canonical_path, request, settings_obj) if canonical_path else get_canonical_url(obj, request))
    og = get_og_data(obj, request)
    og["title"] = getattr(obj, "og_title", "") or title
    og["description"] = getattr(obj, "og_description", "") or description
    robots = "noindex, nofollow" if noindex else get_robots_directive(obj)
    schema = [] if robots.startswith("noindex") else get_schema_data(obj, request)
    return {"title": title, "description": description, "canonical": canonical,
            "robots": robots, "og": og, "schema": schema}


def get_page_seo(page_key, request):
    obj = StaticPageSEO.objects.filter(page_key=page_key).first() or StaticPageSEO(page_key=page_key)
    title, description = STATIC_DEFAULTS[page_key]
    if page_key == "home" and (settings_obj := site_settings()):
        title, description = settings_obj.default_seo_title, settings_obj.default_meta_description
    return build_seo(obj, request, title=title, description=description,
                     canonical_path=reverse(STATIC_ROUTES[page_key]))
