from django.conf import settings
from django.db import models
from django.urls import reverse
from seo.models import SEOFieldsMixin


class Post(SEOFieldsMixin):
    status_choices = (
        ('drf', 'Draft'),
        ('pub', 'Published'),
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    cover = models.ImageField(upload_to='blog/%Y/%m', null=True, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'وبلاگ'
        verbose_name_plural = 'نوشته ها'



    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse('blog:blog_detail', kwargs={'pk': self.pk})



