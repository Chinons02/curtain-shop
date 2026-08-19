from django import forms
from django.forms import ModelChoiceField
from typing import cast
from .models import CurtainCustomization, FabricType, FabricColor, CurtainDesign

class CustomizationForm(forms.ModelForm):
    class Meta:
        model = CurtainCustomization
        fields = [
            'width', 'height', 'fabric_type', 'fabric_color',
            'include_inner_curtain', 'inner_fabric',
            'design', 'style', 'heading_type', 'quantity',
            'special_instructions'
        ]
        widgets = {
            'width': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '12', 
                'max': '240',
                'placeholder': 'Width in inches'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '12',
                'max': '240',
                'placeholder': 'Height in inches'
            }),
            'fabric_type': forms.Select(attrs={'class': 'form-select'}),
            'fabric_color': forms.Select(attrs={'class': 'form-select'}),
            'include_inner_curtain': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'inner_fabric': forms.Select(attrs={'class': 'form-select'}),
            'design': forms.Select(attrs={'class': 'form-select'}),
            'style': forms.Select(attrs={'class': 'form-select'}),
            'heading_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Any special requirements?'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cast(ModelChoiceField, self.fields['inner_fabric']).queryset = FabricType.objects.filter(
            is_light_fabric=True, available=True
        )
        self.fields['inner_fabric'].required = False
        self.fields['design'].required = False
        self.fields['special_instructions'].required = False