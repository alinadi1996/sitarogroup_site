from django.contrib import admin
from blog.models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'datetime_created', )

admin.site.register(Post, PostAdmin)