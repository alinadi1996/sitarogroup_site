from django.contrib import admin
from unfold.admin import ModelAdmin
from blog.models import Post


class PostAdmin(ModelAdmin):
    list_display = ('title', 'author', 'datetime_created', )
    search_fields = ('title', 'content', 'author__username')
    autocomplete_fields = ('author',)
    list_select_related = ('author',)
    list_filter = ('datetime_created',)
    list_per_page = 25
    show_full_result_count = False

admin.site.register(Post, PostAdmin)
