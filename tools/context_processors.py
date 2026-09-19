from .models import Tool


def header_tools(request):
    tools = (
        Tool.objects.public()
        .select_related("category")
        .only("title", "slug", "status", "is_featured", "category__title")
        .order_by("-is_featured", "order", "title")[:5]
    )
    return {"header_tools": tools}
