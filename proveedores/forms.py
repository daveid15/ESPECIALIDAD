from django import forms
from .models import Proveedor  # Importa el modelo correcto

class ProveedorForm(forms.ModelForm):  # Cambia el nombre de la clase a ProveedorForm
    class Meta:
        model = Proveedor  # Usa el modelo Proveedor
        fields = ['proveedor_name', 'proveedor_last_name', 'proveedor_rut', 'proveedor_mail', 'proveedor_address', 'proveedor_region', 'proveedor_comuna', 'proveedor_phone', 'activo']  # Lista de campos del modelo Proveedor que quieres incluir en el formulario


        


