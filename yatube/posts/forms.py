from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ["text", "group"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "cols": 40,
                    "rows": 10,
                },
            ),
        }
