from django.shortcuts import render
from django.shortcuts import render
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, GroupManager, User
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.urls import reverse
import json
import pandas as pd
import xlwt
from datetime import datetime
from django.http import HttpResponse
import traceback
import os
from django.db import transaction
from django.views.decorators.csrf import csrf_protect


from registration.models import Profile
from ventas.models import Prod_venta, Orden_venta, Venta_producto
from administrator.views import validar_email,validar_rut,validar_string,validar_numero
from inventario.models import Product

# Create your views here.

@login_required
def ventas_main(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'ventas/ventas_main.html'
    return render(request,template_name,{'profiles':profiles})

@login_required
def venta_save(request):
    if request.method == 'POST':
        cliente_name = request.POST.get('cliente_name')
        cliente_last_name = request.POST.get('cliente_last_name')
        producto_venta = ['Completo Italiano', 'Completo Personalizado', 'Bebida']  #request.POST.getlist('producto_venta')
        cantidad_venta = request.POST.getlist('cantidad_venta')
        cliente_venta = f"{cliente_name} {cliente_last_name}"
        print(producto_venta)
        print(cantidad_venta)
        if not all([cliente_name, cliente_last_name, producto_venta, cantidad_venta]):
            messages.error(request, 'Debes ingresar toda la información')
            return redirect('venta_crear')

        try:
            with transaction.atomic():
                orden_venta = Orden_venta.objects.create(cliente_venta=cliente_venta)
                total_venta = 0

                for prod, cant in zip(producto_venta, cantidad_venta):
                    producto_instancia = Prod_venta.objects.get(nombre_producto=prod)
                    venta_producto = Venta_producto.objects.create(producto=producto_instancia, cantidad=cant, id_orden=orden_venta, precio_producto=producto_instancia.precio)
                    venta_producto.save()
                    total_venta += producto_instancia.precio * int(cant)

                orden_venta.total_venta = total_venta
                orden_venta.save()

                messages.success(request, 'Orden de Venta creada con éxito')
                return redirect('venta_crear')
        except Exception as e:
            messages.error(request, f'Error al crear la orden: {str(e)}')
            return redirect('venta_crear')
    else:
        messages.error(request, 'Error en el método de envío')
        return redirect('venta_crear')



@login_required
def venta_list(request, page=None, search=None,grupo_id=1):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    template_name = 'ventas/venta_list.html'
    return render(request, template_name,{'profiles': profile})

@login_required
def venta_crear(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id not in [1, 2]:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')
    
    #clientes = Cliente.objects.all()
    productos= Prod_venta.objects.all()
    template_name = 'ventas/venta_crear.html'
    '''
    if request.method == 'POST':
        numero_orden = request.POST.get('numero_orden')
        cliente_name = request.POST.get('cliente_name')
        producto_orden = request.POST.get('producto_orden')
        cantidad_orden = request.POST.get('cantidad_orden')
        monto_orden = request.POST.get('monto_orden')
        producto_orden = request.POST.get('producto_orden')
        agregados_orden = request.POST.get('agregados_orden')
        
        # Mostrar los datos recibidos del formulario
        print("Datos recibidos del formulario:")
        print(f"Orden: {numero_orden}")
        print(f"Cliente: {cliente_name}")
        print(f"Producto: {producto_orden}")
        print(f"Cantidad: {cantidad_orden}")
        print(f"Monto: {monto_orden}")
        print(f"Agregados: {agregados_orden}")

        # Intentar crear la nueva orden de compra
        try:
            nueva_orden = Orden_venta.objects.create(
                numero_orden=numero_orden,
                cliente_name=cliente_name,
                producto_orden=producto_orden,
                cantidad_orden=cantidad_orden,
                monto_orden=monto_orden,
                agregados_orden=agregados_orden,
                # Puedes agregar más campos aquí según sea necesario
            )
            # Guardar el ID de la nueva orden en la sesión
            request.session['nueva_orden_id'] = nueva_orden.id
            print("¡Venta creada con éxito!")
        except Exception as e:
            print(f"Error al crear la venta: {e}")

        # Redirigir al usuario al listado de órdenes
        return redirect('venta_list')
        '''
    
    return render(request, template_name, {'profiles': profiles, 'productos':productos})

@login_required
def detalle_orden_de_venta(request, orden_id):
    orden = get_object_or_404(Orden_venta, id=orden_id)
    return render(request, 'detalle_orden_de_venta.html', {'orden': orden})