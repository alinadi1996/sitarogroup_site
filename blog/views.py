from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic

from blog.models import Post
from portfolio.models import Project
from seo.services import build_seo
from seo.models import StaticPageSEO


def index(request):
    """SEO-friendly, server-rendered agency portfolio landing page."""
    projects = [
        {
            "title": "فروشگاه آنلاین آتریسا",
            "category": "طراحی سایت",
            "filter": "web",
            "result": "افزایش ۲.۴ برابری نرخ تبدیل",
            "description": "بازطراحی تجربه خرید، معماری محتوای محصول و بهینه‌سازی مسیر پرداخت.",
            "number": "01",
            "tone": "cobalt",
        },
        {
            "title": "رشد ارگانیک ویدا",
            "category": "سئو",
            "filter": "seo",
            "result": "رشد ۱۸۰٪ ورودی گوگل",
            "description": "استراتژی کلمات کلیدی، سئوی تکنیکال و طراحی هاب‌های محتوایی.",
            "number": "02",
            "tone": "lime",
        },
        {
            "title": "دستیار تلگرام کارما",
            "category": "ربات تلگرام",
            "filter": "bot",
            "result": "خودکارسازی ۷۰٪ پشتیبانی",
            "description": "ربات فروش و پشتیبانی متصل به پنل مدیریت و درگاه پرداخت.",
            "number": "03",
            "tone": "violet",
        },
        {
            "title": "پلتفرم رزرو سپهر",
            "category": "طراحی سایت + سئو",
            "filter": "web seo",
            "result": "Core Web Vitals سبز",
            "description": "طراحی محصول، توسعه Django و زیرساخت محتوایی مقیاس‌پذیر.",
            "number": "04",
            "tone": "ember",
        },
    ]
    return render(request, "home.html", {"projects": projects})


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    hidden_pages = set(StaticPageSEO.objects.filter(robots_index=False).values_list("page_key", flat=True))
    return render(
        request,
        "sitemap.xml",
        {"portfolio_projects": Project.objects.published().filter(robots_index=True).only("slug", "updated_at"),
         "blog_posts": Post.objects.filter(robots_index=True).only("id", "datetime_updated"),
         "hidden_pages": hidden_pages},
        content_type="application/xml",
    )


class BlogListView(generic.ListView):
    model = Post
    template_name = "blog/blog_list.html"
    context_object_name = "blog_list"


class BlogDetailView(generic.DetailView):
    model = Post
    template_name = "blog/blog_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seo"] = build_seo(self.object, self.request)
        return context
