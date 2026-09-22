from io import BytesIO
import ipaddress
import json
import os
from pathlib import Path
import socket
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from PIL import Image, UnidentifiedImageError

from .models import Tool


OUTPUT_FORMATS = {
    "webp": ("WEBP", "image/webp", "webp"),
    "png": ("PNG", "image/png", "png"),
    "jpeg": ("JPEG", "image/jpeg", "jpg"),
}
IMAGE_EXTENSIONS = {".avif", ".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
MAX_UPLOAD_SIZE = 25 * 1024 * 1024
MAX_ARCHIVE_FILES = 50
MAX_ARCHIVE_SIZE = 100 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
MAX_WEBSITE_RESPONSE_SIZE = 2 * 1024 * 1024
PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


class WebsiteMetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = []
        self.description = ""
        self.h1_count = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta" and attributes.get("name", "").lower() == "description":
            self.description = attributes.get("content", "").strip()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title.append(data.strip())


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def validate_public_url(value):
    url = value.strip()
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
        raise ValueError("یک آدرس معتبر با http:// یا https:// وارد کنید.")
    try:
        port = parts.port
    except ValueError as error:
        raise ValueError("شماره پورت آدرس معتبر نیست.") from error
    if port not in {None, 80, 443}:
        raise ValueError("فقط وب‌سایت‌های HTTP و HTTPS معمولی قابل بررسی هستند.")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parts.hostname, None)}
    except socket.gaierror as error:
        raise ValueError("دامنه پیدا نشد. آدرس را دوباره بررسی کنید.") from error
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise ValueError("آدرس‌های محلی یا خصوصی قابل بررسی نیستند.")
    return url


def inspect_website(url):
    opener = build_opener(NoRedirectHandler())
    current_url = validate_public_url(url)
    for _ in range(6):
        request = Request(current_url, headers={"User-Agent": "SitaroWebsiteAnalyzer/1.0"})
        try:
            response = opener.open(request, timeout=10)
        except HTTPError as error:
            if error.code in {301, 302, 303, 307, 308} and error.headers.get("Location"):
                current_url = validate_public_url(urljoin(current_url, error.headers["Location"]))
                continue
            raise ValueError(f"وب‌سایت با خطای HTTP {error.code} پاسخ داد.") from error
        except (URLError, TimeoutError, OSError) as error:
            raise ValueError("اتصال به وب‌سایت ممکن نشد.") from error

        with response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "application/xhtml+xml"}:
                raise ValueError("این آدرس یک صفحه HTML قابل بررسی نیست.")
            content = response.read(MAX_WEBSITE_RESPONSE_SIZE + 1)
            if len(content) > MAX_WEBSITE_RESPONSE_SIZE:
                raise ValueError("حجم صفحه برای بررسی بیش از حد مجاز است.")
            charset = response.headers.get_content_charset() or "utf-8"
            html = content.decode(charset, errors="replace")

        parser = WebsiteMetadataParser()
        parser.feed(html)
        return {
            "final_url": current_url,
            "status_code": response.status,
            "title": " ".join(part for part in parser.title if part),
            "description": parser.description,
            "h1_count": parser.h1_count,
        }
    raise ValueError("تعداد تغییرمسیرهای وب‌سایت بیش از حد مجاز است.")


def fetch_page_speed(url):
    parameters = {"url": url, "strategy": "mobile", "category": "PERFORMANCE"}
    api_key = os.environ.get("GOOGLE_PAGESPEED_API_KEY")
    if not api_key:
        return None, "کلید Google PageSpeed تنظیم نشده است. مقدار GOOGLE_PAGESPEED_API_KEY را برای سرویس وب تنظیم کنید."
    parameters["key"] = api_key
    try:
        with urlopen(f"{PAGESPEED_API_URL}?{urlencode(parameters)}", timeout=60) as response:
            data = json.load(response)
    except HTTPError as error:
        if error.code == 403:
            return None, "Google PageSpeed کلید API را نپذیرفت. API را در Google Cloud فعال کنید و محدودیت‌های کلید را بررسی کنید."
        if error.code == 429:
            return None, "سهمیه درخواست‌های Google PageSpeed فعلاً پر شده است. چند دقیقه دیگر دوباره تلاش کنید."
        return None, f"Google PageSpeed با خطای {error.code} پاسخ داد."
    except (URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None, "دریافت گزارش Google PageSpeed در حال حاضر ممکن نیست. دوباره تلاش کنید."

    lighthouse = data.get("lighthouseResult", {})
    audits = lighthouse.get("audits", {})
    performance = lighthouse.get("categories", {}).get("performance", {}).get("score")
    if performance is None:
        return None, "Google PageSpeed برای این آدرس امتیازی برنگرداند."
    return {
        "score": round(performance * 100),
        "first_contentful_paint": audits.get("first-contentful-paint", {}).get("displayValue", "-"),
        "largest_contentful_paint": audits.get("largest-contentful-paint", {}).get("displayValue", "-"),
        "total_blocking_time": audits.get("total-blocking-time", {}).get("displayValue", "-"),
        "cumulative_layout_shift": audits.get("cumulative-layout-shift", {}).get("displayValue", "-"),
    }, None


def convert_image(source, output_format):
    """Convert a validated image while keeping uploads out of persistent storage."""
    pil_format, _, extension = OUTPUT_FORMATS[output_format]
    with Image.open(source) as image:
        if image.width * image.height > MAX_IMAGE_PIXELS:
            raise ValueError("ابعاد تصویر بیش از حد مجاز است.")
        image.load()

        if pil_format == "JPEG":
            if image.mode in ("RGBA", "LA"):
                background = Image.new("RGB", image.size, "white")
                background.paste(image, mask=image.getchannel("A"))
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

        output = BytesIO()
        save_options = {"quality": 90} if pil_format in {"JPEG", "WEBP"} else {}
        image.save(output, format=pil_format, **save_options)
    return output.getvalue(), extension


class ImageConvertView(View):
    template_name = "tools/image_converter.html"

    def get(self, request):
        return self.render_form(request)

    def post(self, request):
        uploaded_file = request.FILES.get("image")
        output_format = request.POST.get("output_format")
        if uploaded_file is None or output_format not in OUTPUT_FORMATS:
            return HttpResponseBadRequest("فایل و فرمت خروجی معتبر نیست.")
        if uploaded_file.size > MAX_UPLOAD_SIZE:
            return HttpResponseBadRequest("حجم فایل نباید از ۲۵ مگابایت بیشتر باشد.")

        try:
            if Path(uploaded_file.name).suffix.lower() == ".zip":
                return self.convert_archive(uploaded_file, output_format)
            converted, extension = convert_image(uploaded_file, output_format)
        except (BadZipFile, UnidentifiedImageError, OSError, ValueError) as error:
            message = str(error) if isinstance(error, ValueError) else "فایل تصویر معتبر نیست."
            return self.render_form(request, message, status=400)

        filename = f"{Path(uploaded_file.name).stem}.{extension}"
        return self.download_response(converted, OUTPUT_FORMATS[output_format][1], filename)

    def convert_archive(self, uploaded_file, output_format):
        with ZipFile(uploaded_file) as source_archive:
            files = [
                item for item in source_archive.infolist()
                if not item.is_dir() and Path(item.filename).suffix.lower() in IMAGE_EXTENSIONS
            ]
            total_size = sum(item.file_size for item in files)
            if not files:
                raise ValueError("فایل ZIP هیچ تصویر قابل تبدیلی ندارد.")
            if len(files) > MAX_ARCHIVE_FILES or total_size > MAX_ARCHIVE_SIZE:
                raise ValueError("ZIP حداکثر می‌تواند ۵۰ تصویر با مجموع ۱۰۰ مگابایت داشته باشد.")
            if any(item.flag_bits & 0x1 for item in files):
                raise ValueError("تصاویر رمزدار ZIP پشتیبانی نمی‌شوند.")

            result = BytesIO()
            with ZipFile(result, "w", ZIP_DEFLATED) as result_archive:
                for index, item in enumerate(files, start=1):
                    converted, extension = convert_image(BytesIO(source_archive.read(item)), output_format)
                    filename = f"{index:02d}-{Path(item.filename).stem}.{extension}"
                    result_archive.writestr(filename, converted)

        return self.download_response(result.getvalue(), "application/zip", f"sitaro-images-{output_format}.zip")

    def render_form(self, request, error=None, status=200):
        return self.render_to_response(request, {"error": error}, status)

    def render_to_response(self, request, context, status=200):
        return render(request, self.template_name, context, status=status)

    @staticmethod
    def download_response(content, content_type, filename):
        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class WebsiteAnalyzerView(View):
    template_name = "tools/website_analyzer.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            url = validate_public_url(request.POST.get("url", ""))
            analysis = inspect_website(url)
        except ValueError as error:
            return render(request, self.template_name, {"error": str(error), "url": request.POST.get("url", "")}, status=400)

        page_speed, page_speed_error = fetch_page_speed(url)
        return render(
            request,
            self.template_name,
            {"url": url, "analysis": analysis, "page_speed": page_speed, "page_speed_error": page_speed_error},
        )


class ToolIndexView(ListView):
    model = Tool
    template_name = "tools/index.html"
    context_object_name = "tools"

    def get_queryset(self):
        return Tool.objects.public().select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visible_tools = list(context["tools"])
        featured_tool = next((tool for tool in visible_tools if tool.is_featured), None)
        context["featured_tool"] = featured_tool
        context["tools"] = [tool for tool in visible_tools if tool != featured_tool]
        context["visible_tool_count"] = len(visible_tools)
        return context


class ToolLaunchView(View):
    """Routes active tools to their implementation while preserving stable tool URLs."""

    def get(self, request, slug):
        tool = Tool.objects.public().filter(slug=slug, status=Tool.Status.ACTIVE).first()
        if tool is None:
            raise Http404("این ابزار در دسترس نیست.")
        if tool.slug == "image-optimizer":
            return HttpResponseRedirect(reverse("tools:image_converter"))
        if tool.slug == "website-analyzer":
            return HttpResponseRedirect(reverse("tools:website_analyzer"))
        return HttpResponseRedirect(f"{reverse('tools:index')}#tool-{tool.slug}")
