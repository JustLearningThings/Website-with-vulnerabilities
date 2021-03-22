from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator

from blog.models import Post, Comment

# this is the regex validator that should be included
# passwordRegex = RegexValidator(r'^(?=[^a-z]*[a-z])(?=\D*\d)[^:&.~\s]{5,20}$', 'Password must contain at least one lowercase letter and at least one digit.')

class AuthForm(forms.Form):
    username = forms.CharField(label='username', max_length=64)
    password = forms.CharField(widget=forms.PasswordInput(), label='password', max_length=64)
    # password would be better to have a validator
    # password = forms.CharField(widget=forms.PasswordInput(), label='password', max_length=64, validators=[passwordRegex])

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']


# class CommentForm(forms.Form):
class CommentForm(forms.ModelForm):
    content = forms.CharField(max_length=256, widget=forms.Textarea, label='Leave a comment')
    class Meta:
        model = Comment
        fields = ['content']
