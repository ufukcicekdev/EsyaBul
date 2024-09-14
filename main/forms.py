from django import forms
from .models import ContactUs

class ProductSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)



class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['full_name', 'email', 'phone', 'subject', 'message']