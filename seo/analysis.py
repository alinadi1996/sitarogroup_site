"""Editorial checklist, not a search-engine score or ranking prediction."""

import re

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from .services import get_meta_description, get_seo_title


def analyze_content(obj):
    title = get_seo_title(obj)
    description = get_meta_description(obj)
    keyword = (getattr(obj, "focus_keyword", "") or "").strip().casefold()
    raw_content = (getattr(obj, "content", "") or getattr(obj, "introduction", "") or "")
    plain_content = re.sub(r"\s+", " ", strip_tags(raw_content)).strip().casefold()
    canonical = getattr(obj, "canonical_url", "")
    valid_canonical = True
    if canonical:
        try:
            URLValidator(schemes=["http", "https"])(canonical)
        except ValidationError:
            valid_canonical = False
    cover = getattr(obj, "cover", None)
    has_cover = bool(cover)
    alt = getattr(obj, "cover_alt", None)
    if alt is None and has_cover:
        alt = f"تصویر شاخص {getattr(obj, 'title', '')}"  # Current blog template fallback.
    is_project = obj._meta.label == "portfolio.Project"
    # Blog text is currently rendered with linebreaks/escaping, not as rich HTML.
    has_h2 = is_project
    checks = [
        ("عنوان اختصاصی سئو", bool(obj.seo_title), "از عنوان محتوا استفاده می‌شود."),
        ("طول تقریبی عنوان", 30 <= len(title) <= 70, f"{len(title)} نویسه؛ بازهٔ پیشنهادی ۳۰ تا ۷۰ است."),
        ("توضیح متای اختصاصی", bool(obj.meta_description), "از خلاصهٔ محتوا استفاده می‌شود."),
        ("طول تقریبی توضیح", 70 <= len(description) <= 160, f"{len(description)} نویسه؛ بازهٔ پیشنهادی ۷۰ تا ۱۶۰ است."),
        ("عبارت کلیدی هدف", bool(keyword), "صرفاً برای بررسی داخلی است."),
        ("عبارت کلیدی در عنوان", bool(keyword) and keyword in title.casefold(), "وجود عبارت در عنوان بررسی می‌شود."),
        ("عبارت کلیدی در توضیح", bool(keyword) and keyword in description.casefold(), "وجود عبارت در توضیح بررسی می‌شود."),
        ("عبارت کلیدی در آغاز محتوا", bool(keyword) and keyword in plain_content[:250], "۲۵۰ نویسهٔ نخست بررسی می‌شود."),
        ("تیتر H2", has_h2, "قالب پروژه H2 دارد؛ قالب فعلی بلاگ از متن ساده H2 نمی‌سازد."),
        ("تصویر شاخص", has_cover, "تصویر محتوای اصلی بررسی می‌شود."),
        ("متن جایگزین تصویر", bool(alt), "در بلاگ از عنوان پست ساخته می‌شود؛ پروژه فیلد مستقل دارد."),
        ("canonical معتبر", valid_canonical, "در صورت خالی بودن، نشانی صفحه خودکار ساخته می‌شود."),
        ("اجازه ایندکس", obj.robots_index, "این صفحه noindex است."),
        ("اسکیما فعال", obj.schema_mode != "disabled", "اسکیمای این صفحه غیرفعال است."),
    ]
    return [{"label": label, "ok": ok, "detail": detail} for label, ok, detail in checks]
