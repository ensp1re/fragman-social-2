from django import forms
from .models import Comment
#
#
# class PostForm(forms.ModelForm):
#     caption = forms.CharField(widget=forms.Textarea(attrs={
#         'placeholder': 'What is happening?!', 'oninput': 'autoResize(this)',
#         "id" : "form-post-id",
#     }))
#     image = forms.ImageField(widget=forms.FileInput(attrs={
#         'accept': '.jpg, .jpeg, .png', 'style': 'display: none',
#         'id' : 'imagePost',
#     }))
#
#     class Meta:
#         model = Post
#         fields = ("caption", "image")


#      don't work idk why

# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['text']
#         widgets = {
#             'text': forms.Textarea(
#                 attrs={'class': 'com', 'placeholder': 'Enter your comment...', 'oninput' : 'autoResize(this)'}),
#         }