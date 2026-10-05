from django import forms

from .models import Post
from .rich_text import sanitize_rich_text


class RichTextWidget(forms.Textarea):
    class Media:
        css = {"all": ("css/admin-rich-text.css",)}
        js = ("js/admin-rich-text.js",)

    def __init__(self, attrs=None):
        super().__init__({"class": "sitaro-rich-text-source", "rows": 18, **(attrs or {})})

    def format_value(self, value):
        # The editor inserts this value into a contenteditable element.
        return sanitize_rich_text(super().format_value(value))


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        widgets = {"content": RichTextWidget()}

    def clean_content(self):
        return sanitize_rich_text(self.cleaned_data["content"])
