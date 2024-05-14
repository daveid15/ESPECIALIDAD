from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Product

class ProductForm(forms.ModelForm):
    product_image = forms.ImageField(required=False, label='Imagen del producto', 
                                     widget=forms.FileInput(attrs={'class': 'form-control-file'}))

   
class Meta:
    model = Product
    fields = ['supply_name', 'supply_code', 'supply_unit', 'supply_initial_stock','supply_input','supply_output']
    labels = {
        'supply_name': 'Nombre del producto',
        'supply_code': 'Codigo del producto',
        'supply_unit': 'Unidad del producto',
        'supply_initial_stock': 'Stock inicial del producto',
        'supply_input': 'Entrada del producto',
        'supply_output': 'Salida del producto',
        'supply_total': 'total del producto',
    }
    widgets = {
        'supply_name': forms.TextInput(attrs={'class': 'form-control'}),
        'supply_code': forms.NumberInput(attrs={'class': 'form-control'}),
        'supply_unit': forms.Select(attrs={'class': 'form-control'}),
        'supply_initial_stock': forms.NumberInput(attrs={'class': 'form-control'}),
        'supply_input': forms.NumberInput(attrs={'class': 'form-control'}),
        'supply_output': forms.NumberInput(attrs={'class': 'form-control'}),
        'supply_total': forms.NumberInput(attrs={'class': 'form-control'}),
        }