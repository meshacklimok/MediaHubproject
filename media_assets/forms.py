from django import forms 
from .models import MediaAsset

class MediaAssetForm(forms.ModelForm):
    class Meta:
        model = MediaAsset
        fields = ('title','description','category','media_file','is_public')
        
        widgets = {
             'title' : forms.TextInput(attrs={
                'class' : 'form-control'
            }),
            'description' : forms.Textarea(attrs={
                'class' : 'form-control',
                'rows' : 3
            }),
            'category' : forms.Select(attrs={
                'class' : 'form-control'
            }), 
            'is_public' : forms.CheckboxInput(attrs={
                'class' : 'form-check-input'
            })
            
        }