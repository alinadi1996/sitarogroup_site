"""Allowed formatting for editorial content, both in admin and on public pages."""

import bleach


ALLOWED_TAGS = (
    "p", "br", "strong", "b", "em", "i", "u", "h2", "h3", "h4",
    "ul", "ol", "li", "blockquote", "a", "pre", "code", "hr",
)


def sanitize_rich_text(value):
    return bleach.clean(
        value or "",
        tags=ALLOWED_TAGS,
        attributes={"a": ("href", "title")},
        protocols=("http", "https", "mailto"),
        strip=True,
        strip_comments=True,
    )
