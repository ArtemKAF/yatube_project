from django import forms

from .models import Group, Post


class PostForm(forms.ModelForm):

    text = forms.CharField(
        label=Post._meta.get_field("text").verbose_name,
        help_text=Post._meta.get_field("text").help_text,
        widget=forms.Textarea(),
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label=Post._meta.get_field("group").verbose_name,
        help_text=Post._meta.get_field("group").help_text,
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
