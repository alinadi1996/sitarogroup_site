from django.contrib import admin
from unfold.admin import ModelAdmin
from blog.models import Post
from seo.admin import SEOAdminMixin, SEO_FIELDS


class PostAdmin(SEOAdminMixin, ModelAdmin):
    list_display = ('title', 'author', 'datetime_created', )
    search_fields = ('title', 'content', 'author__username')
    autocomplete_fields = ('author',)
    list_select_related = ('author',)
    list_filter = ('datetime_created',)
    list_per_page = 25
    show_full_result_count = False
    readonly_fields = ('datetime_created', 'datetime_updated', 'seo_updated_at', 'seo_analysis')
    fieldsets = (
        ('محتوا', {'fields': ('title', 'slug', 'author', 'content', 'cover', 'datetime_created', 'datetime_updated')}),
        ('بهینه‌سازی برای موتورهای جست‌وجو', {'fields': SEO_FIELDS}),
        ('بررسی داخلی SEO', {'fields': ('seo_analysis',)}),
    )

admin.site.register(Post, PostAdmin)
