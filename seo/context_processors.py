from django.urls import reverse

from .services import TOOL_DEFAULTS, TOOL_ROUTES, build_seo, get_page_seo


PAGE_ROUTES = {
    "home": "home", "leads:contact": "contact", "tools:index": "tools",
    "portfolio:project_list": "portfolio_index", "blog:blog_list": "blog_index",
}
ACCOUNT_DEFAULTS = {
    "account_login": ("ورود به حساب | گروه سیتارو", "ورود امن به فضای همکاری مشتریان گروه سیتارو."),
    "account_signup": ("ساخت حساب | گروه سیتارو", "ساخت حساب کاربری برای ورود به فضای همکاری گروه سیتارو."),
    "account_change_password": ("تغییر رمز عبور | گروه سیتارو", "تغییر امن رمز عبور حساب کاربری گروه سیتارو."),
    "account_reset_password": ("بازیابی رمز عبور | گروه سیتارو", "دریافت لینک امن بازیابی رمز عبور حساب گروه سیتارو."),
    "account_reset_password_done": ("ایمیل بازیابی ارسال شد | گروه سیتارو", "راهنمای بازیابی رمز عبور برای شما ارسال شد."),
    "account_reset_password_from_key": ("انتخاب رمز جدید | گروه سیتارو", "انتخاب رمز عبور جدید برای حساب گروه سیتارو."),
    "account_reset_password_from_key_done": ("بازیابی رمز کامل شد | گروه سیتارو", "رمز عبور جدید با موفقیت ثبت شد."),
    "accounts:profile": ("پنل کاربری | گروه سیتارو", "مدیریت حساب و تنظیمات امنیتی کاربر در گروه سیتارو."),
}


def seo_context(request):
    match = request.resolver_match
    if not match:
        return {}
    route = match.view_name
    if route in PAGE_ROUTES:
        return {"seo": get_page_seo(PAGE_ROUTES[route], request)}
    if route.startswith("tools:") and route.split(":")[-1] in TOOL_ROUTES:
        from tools.models import Tool
        tool_name = route.split(":")[-1]
        tool = Tool.objects.filter(slug=TOOL_ROUTES[tool_name], status=Tool.Status.ACTIVE).first()
        title, description = TOOL_DEFAULTS[tool_name]
        return {"seo": build_seo(tool, request, title=title, description=description,
                                 canonical_path=reverse(route))}
    if route.startswith(("account_", "accounts:")):
        title, description = ACCOUNT_DEFAULTS.get(route, (None, None))
        return {"seo": build_seo(None, request, title=title, description=description, noindex=True)}
    return {"seo": build_seo(None, request)}
