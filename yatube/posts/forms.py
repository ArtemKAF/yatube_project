from django import forms

from .models import Group, Post


class PostForm(forms.ModelForm):

    text = forms.CharField(
        label="Текст поста",
        help_text="Текст нового поста",
        widget=forms.Textarea(),
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Группа",
        help_text="Группа, к которой будет относиться пост",
        required=False,
    )

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
