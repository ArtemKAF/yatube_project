from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ("text", "group", "image")
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "cols": 40,
                    "rows": 10,
                },
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = ("text",)
        widget = {
            "text": forms.Textarea(
                attrs={
                    "colls": 40,
                    "rows": 5,
                }
            )
        }
