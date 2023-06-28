from django import forms
from .models import Listing, Comment

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ["user", "active", "winner"]
        

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ["user", "listing"]
