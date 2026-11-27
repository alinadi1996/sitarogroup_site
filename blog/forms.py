from django import forms

from .models import Post
from .rich_text import sanitize_rich_text
from jodit.widgets import JoditWidget


# class RichTextWidget(forms.Textarea):
#     class Media:
#         css = {"all": ("dist/css/admin-rich-text.min.css",)}
#         js = ("dist/js/admin-rich-text.min.js",)

#     def __init__(self, attrs=None):
#         super().__init__({"class": "sitaro-rich-text-source", "rows": 18, **(attrs or {})})

#     def format_value(self, value):
#         # The editor inserts this value into a contenteditable element.
#         return sanitize_rich_text(super().format_value(value))



# class JoditWidget(forms.Textarea):

#     def __init__(self, attrs=None):
#         default_attrs = {
#             "class": "sitaro-jodit",
#             "rows": 20,
#             "dir": "rtl",
#         }

#         if attrs:
#             default_attrs.update(attrs)

#         super().__init__(attrs=default_attrs)

# class PostAdminForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = "__all__"
#         widgets = {"content": JoditWidget()}


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=JoditWidget(config_name='default'))

    class Meta:
        model = Post
        fields = ["content"]
