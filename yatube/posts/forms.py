from django import forms

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group',)
        help_text = {
            'text': 'Текст поста',
            'group': 'Группа',
        }

    def clean_text(self):
        data = self.cleaned_data['text']

        if not data:
            raise forms.ValidationError('Заполните поле текст!')

        return data
