from django import forms

class ShippingForm(forms.Form):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Full Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': '3',
        'placeholder': 'Street Address'
    }))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'City'
    }))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'State'
    }))
    zip_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'ZIP Code (Optional)'
    }))
    delivery_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': '2',
        'placeholder': 'Special delivery instructions'
    }))