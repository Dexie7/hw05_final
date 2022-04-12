from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        text = forms.CharField(required=True)
        group = forms.CharField(required=False)
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        text = forms.CharField(required=True)
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) > 1:
            return text
        raise forms.ValidationError("Не заполнен текст комментария!")
