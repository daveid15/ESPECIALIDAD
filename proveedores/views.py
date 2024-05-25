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
from openpyxl import Workbook
import xlwt
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
import traceback
import os
from django.db import transaction
from django.views.decorators.csrf import csrf_protect
import matplotlib.pyplot as plt
import pandas as pd
from django.http.response import JsonResponse

from registration.models import Profile
from proveedores.models import Proveedor, Orden_compra, Producto_Orden
from inventario.models import Product
from administrator.views import validar_email,validar_rut,validar_string,validar_numero
from .forms import ProveedorForm
from datetime import datetime

# Create your views here.
@login_required
def proveedores_main(request):
    current_month = datetime.now().month

    proveedores_activos_count = Proveedor.objects.filter(activo=True).count()
    proveedores_eliminados_count = Proveedor.objects.filter(activo=False).count()
    total_proveedores_count = Proveedor.objects.count()

    # Filtrar por los proveedores creados en el mes actual
    proveedores_nuevos_count = Proveedor.objects.filter(created_at__month=current_month).count()

    return render(request, 'proveedores/proveedores_main.html', {
        'proveedores_activos_count': proveedores_activos_count,
        'proveedores_eliminados_count': proveedores_eliminados_count,
        'total_proveedores_count': total_proveedores_count,
        'proveedores_nuevos_count': proveedores_nuevos_count,
    })


@login_required
def proveedores_crear(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        # Procesar el formulario de creación del proveedor
        proveedor_form = ProveedorForm(request.POST)
        if proveedor_form.is_valid():
            proveedor = proveedor_form.save(commit=False)
            proveedor.activo = True  # Establecer el proveedor como activo
            proveedor.save()
            messages.success(request, 'Proveedor creado correctamente')
            return redirect('proveedores_activos')  # Redirigir a la lista de proveedores activos

    else:
        # Renderizar el formulario de creación del proveedor
        proveedor_form = ProveedorForm()

    template_name = 'proveedores/proveedores_crear.html'
    return render(request, template_name, {'profiles': profiles, 'proveedor_form': proveedor_form})


@login_required
def proveedor_save(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')
    
    if request.method == 'POST':
        errores=[]
        proveedor_name = request.POST.get('proveedor_name')
        proveedor_last_name = request.POST.get('proveedor_last_name')
        proveedor_rut = request.POST.get('proveedor_rut')
        proveedor_mail = request.POST.get('proveedor_mail')
        proveedor_address = request.POST.get('proveedor_address')
        proveedor_region = request.POST.get('proveedor_region')
        proveedor_comuna = request.POST.get('proveedor_comuna')
        proveedor_phone = request.POST.get('proveedor_phone')
        proveedor_insumo = request.POST.getlist('proveedor_insumo')
        template_name = 'proveedores/proveedores_main.html'
        if not validar_string(proveedor_name,request):
            errores.append('Nombre inválido')
        if not validar_string(proveedor_last_name,request):
            errores.append('Apellido inválido')
        if not validar_numero(proveedor_phone,request):
            errores.append('Número de teléfono inválido')
        if not validar_email(proveedor_mail,request):
            errores.append('Correo electrónico inválido')
        if not validar_rut(proveedor_rut,request):
            errores.append('RUT inválido')
        if errores:
            messages.add_message(request, messages.INFO, 'Hubo algunos errores al crear el proveedor: ' + ', '.join(errores))
            return render(request,template_name)
        if proveedor_name == '' or proveedor_last_name == '' or proveedor_rut == '' or proveedor_mail == '' or proveedor_address == '' or proveedor_region == '' or proveedor_comuna == '' or proveedor_phone ==  '':
            messages.add_message(request, messages.INFO, 'Debes ingresar toda la información')
            return redirect('proveedores_main')
        rut_exist = Proveedor.objects.filter(proveedor_rut=proveedor_rut).count() 
        mail_exist = Proveedor.objects.filter(proveedor_mail=proveedor_mail).count()
        if rut_exist == 0:
            if mail_exist == 0:
                proveedor_save = Proveedor(
                    proveedor_name=proveedor_name,
                    proveedor_last_name=proveedor_last_name,
                    proveedor_rut=proveedor_rut,
                    proveedor_mail=proveedor_mail,
                    proveedor_address=proveedor_address,
                    proveedor_region=proveedor_region,
                    proveedor_comuna=proveedor_comuna,
                    proveedor_phone=proveedor_phone,
                    proveedor_insumo=proveedor_insumo
              )

                proveedor_save.save()
                messages.add_message(request, messages.INFO, 'Proveedor ingresado con éxito')
                return redirect('proveedores_main')
            else:
                messages.add_message(request, messages.INFO, 'El correo que esta tratando de ingresar, ya existe en nuestros registros')
                return redirect('proveedores_main') 
        else:
            messages.add_message(request, messages.INFO, 'El rut que esta tratando de ingresar, ya existe en nuestros registros')  
            return redirect('proveedores_main')
    else:
        messages.add_message(request, messages.INFO, 'Error en el método de envío')
        return redirect('check_group_main')


    
@login_required
def proveedor_list(request, page=None, search=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')

    ordenes = Proveedor.objects.all()
    search = request.GET.get('search')
    
    
    if search:
        ordenes = ordenes.filter(Q(proveedor_name__icontains=search))

    paginator = Paginator(ordenes, 1)
    pagina_numero = request.GET.get('pagina')
    
    try:
        ordenes = paginator.page(pagina_numero)
    except PageNotAnInteger:
        ordenes = paginator.page(1)
    except EmptyPage:
        ordenes = paginator.page(paginator.num_pages)

    template_name = 'proveedores/proveedor_list.html'
    return render(request, template_name, {'template_name': template_name, 'ordenes': ordenes, 'page': page})


@login_required
def proveedor_ver(request, proveedor_id):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    proveedor_data = Proveedor.objects.get(pk=proveedor_id)
    template_name = 'proveedores/proveedor_ver.html'
    return render(request, template_name, {'profile': profile, 'proveedor_data': proveedor_data,})

@login_required
def proveedor_edit(request, proveedor_id):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':

        proveedor_name = request.POST.get('proveedor_name')
        proveedor_last_name = request.POST.get('proveedor_last_name')
        proveedor_mail = request.POST.get('proveedor_mail')
        proveedor_phone = request.POST.get('proveedor_phone')
        proveedor_address = request.POST.get('proveedor_address')
        proveedor_region = request.POST.get('proveedor_region') 
        proveedor_comuna = request.POST.get('proveedor_comuna')
        proveedor_insumo = request.POST.getlist('proveedor_insumo')

        proveedor.proveedor_name = proveedor_name
        proveedor.proveedor_last_name = proveedor_last_name
        proveedor.proveedor_mail = proveedor_mail
        proveedor.proveedor_phone = proveedor_phone
        proveedor.proveedor_address = proveedor_address
        proveedor.proveedor_region = proveedor_region
        proveedor.proveedor_comuna = proveedor_comuna
        proveedor.proveedor_insumo = proveedor_insumo
        
        proveedor.save()
        
        return redirect('proveedor_edit', proveedor_id=proveedor.id)
    else:
        proveedor_data = Proveedor.objects.get(pk=proveedor_id)
        
        template_name= 'proveedores/proveedor_edit.html'
        
        return render(request, template_name, {'proveedor_data': proveedor_data})

def proveedor_delete(request, proveedor_id):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.delete()
    messages.success(request, 'Proveedor eliminado correctamente')
    return redirect(reverse('proveedor_list'))
 
@login_required
def carga_masiva_proveedor(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'proveedores/carga_masiva_proveedor.html'
    return render(request, template_name, {'profiles': profile})

@login_required
def import_file_proveedor(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="archivo_importacion_proveedors.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = 'carga_masiva'

    columns = ['proveedor_rut', 'proveedor_name', 'proveedor_last_name', 'proveedor_mail', 'proveedor_phone', 'proveedor_address', 'proveedor_region', 'proveedor_comuna', 'proveedor_insumo']
    ws.append(columns)


    example_data = [
        'ej: Rut',
        'ej: Nombre proveedor',
        'ej: Apellido proveedor',
        'abc@gmail.com',
        '55642334',
        'ej: Direccion',
        'ej: Region',
        'ej: Comuna',
        'ej: Insumo'
    ]
    ws.append(example_data)

    wb.save(response)
    return response

@login_required
def carga_masiva_proveedor_save(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        try:
            data = pd.read_excel(request.FILES['myfile'], engine='openpyxl', skiprows=1)
            df = pd.DataFrame(data)
            acc = 0
            for item in df.itertuples():
                proveedor_rut = str(item[1])
                proveedor_name = str(item[2])
                proveedor_last_name = str(item[3])
                proveedor_mail = str(item[4])
                proveedor_phone = str(item[5])
                proveedor_address = str(item[6])
                proveedor_region = str(item[7])
                proveedor_comuna = str(item[8])
                proveedor_insumo = str(item[9])
                
                # Validación de rut
                if not validar_rut(proveedor_rut, request):
                    messages.add_message(request, messages.INFO, f'El RUT "{proveedor_rut}" no es válido.')
                    continue

                # Validación de correp
                if not validar_email(proveedor_mail, request):
                    messages.add_message(request, messages.INFO, f'El correo electrónico "{proveedor_mail}" no es válido.')
                    continue

                # Validación de nombre
                if not validar_string(proveedor_name, request) or not validar_string(proveedor_last_name, request):
                    messages.add_message(request, messages.INFO, 'El nombre y/o apellido no son válidos.')
                    continue
                
                # Validación de direccion
                if not validar_string(proveedor_region, request) or not validar_string(proveedor_comuna, request):
                    messages.add_message(request, messages.INFO, 'La comuna y/o región no son válidos.')
                    continue

                # Validación de insumo
                if not validar_string(proveedor_insumo, request):
                    messages.add_message(request, messages.INFO, 'El insumo ingresado no es válido.')
                    continue

                # Validaci+on de telefono
                if not validar_numero(proveedor_phone, request):
                    messages.add_message(request, messages.INFO, f'El número de teléfono "{proveedor_phone}" no es válido.')
                    continue

                rut_exist = Proveedor.objects.filter(proveedor_rut=proveedor_rut).count() 
                if rut_exist== 0:
                    proveedor_save = Proveedor(
                        proveedor_rut=proveedor_rut,
                        proveedor_name=proveedor_name,
                        proveedor_last_name=proveedor_last_name,
                        proveedor_mail=proveedor_mail,
                        proveedor_phone=proveedor_phone,
                        proveedor_address=proveedor_address,
                        proveedor_region=proveedor_region,
                        proveedor_comuna=proveedor_comuna,
                        proveedor_insumo=proveedor_insumo
                    )
                    proveedor_save.save()
                    acc += 1
                    messages.add_message(request, messages.INFO, 'Carga masiva finalizada, se importaron ' + str(acc) + ' registros')
                    return redirect('carga_masiva_proveedor')
                else:
                    messages.add_message(request, messages.INFO, 'El rut que esta tratando de ingresar, ya existe en nuestros registros')   
                    return redirect('carga_masiva_user')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Error al procesar el archivo: {str(e)}')
            return redirect('carga_masiva_proveedor')
    return HttpResponseRedirect(reverse('carga_masiva_proveedor'))

@login_required
def descarga_reporte(request):
    try:    
        profiles = Profile.objects.get(user_id = request.user.id)
        if profiles.group_id != 1:
         messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
         return redirect('check_group_main')
    
        style_2 = xlwt.easyxf('font: name Time New Roman, color-index black; font: bold on')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        response=HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="ListaProveedores.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Proveedores')

        row_num = 0
        columns = ['Nombre', 'Mail', 'Telefono']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num] ,font_style)

        proveedores = Proveedor.objects.all().order_by('proveedor_name')

        for row in proveedores:
            row_num += 1
            for col_num in range(3):
                if col_num == 0:
                    ws.write(row_num, col_num, row.proveedor_name, style_2)
                if col_num == 1:
                    ws.write(row_num, col_num, row.proveedor_mail, style_2)   
                if col_num == 2:
                    ws.write(row_num, col_num, row.proveedor_phone, style_2)

        
        wb.save(response)
        return response
    except Exception:
            traceback.print_exc()
            messages.add_message(request, messages.ERROR, 'Se produjo un error al generar el archivo Excel. Por favor, inténtelo de nuevo más tarde.')
            return redirect('proveedor_list')
    
@login_required   
def seleccion_proveedores(request):
    return render(request, 'seleccion_proveedores.html')

from django.core.paginator import Paginator
from .models import Proveedor

@login_required
def proveedores_activos(request):
    # Obtener los proveedores activos
    proveedores_activos = Proveedor.objects.filter(activo=True)

    # Aplicar búsqueda si se proporciona un término de búsqueda
    search = request.GET.get('search')
    if search:
        proveedores_activos = proveedores_activos.filter(proveedor_name__icontains=search)

    # Paginar los resultados
    paginator = Paginator(proveedores_activos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Renderizar la plantilla con los datos de los proveedores activos
    return render(request, 'proveedores_activos.html', {'p_list_paginate': page_obj, 'paginator': paginator, 'search': search})

@login_required
def proveedores_eliminados(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')

    proveedores_list = Proveedor.objects.filter(activo=False)
    paginator = Paginator(proveedores_list, 10)  # Cambia 10 por el número de proveedores que deseas mostrar por página

    page = request.GET.get('page')
    proveedores_paginate = paginator.get_page(page)
    
    return render(request, 'proveedores_eliminados.html', {
        'proveedores_eliminados': proveedores_paginate,
        'paginator': paginator,
        'search': request.GET.get('search', '')
    })

@login_required
def restaurar_proveedor(request, proveedor_id):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')

    try:
        proveedor = Proveedor.objects.get(pk=proveedor_id)
        proveedor.activo = True
        proveedor.save()
        messages.add_message(request, messages.INFO, f'Proveedor {proveedor.proveedor_name} restaurado con éxito')
    except Proveedor.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Proveedor no encontrado')

    return redirect('proveedores_eliminados')

@login_required
def eliminar_proveedor(request, proveedor_id):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')

    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    
    proveedor.activo = False
    proveedor.save()
    messages.add_message(request, messages.INFO, 'Proveedor ' + proveedor.proveedor_name + ' eliminado con éxito')
    return redirect('proveedores_activos')



#Órden de Compraa


@login_required
def orden_main(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'proveedores/orden_main.html'
    return render(request,template_name,{'profiles':profiles})
    
    
@login_required
def lista_orden(request, grupo_id):
    ordenes = Orden_compra.objects.filter(proveedor_orden=grupo_id)
    return render(request, 'proveedores/lista_orden.html', {'ordenes': ordenes})


@login_required
def orden_list_enviada(request, page=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    
    search = request.GET.get('search')
    ordenes = Orden_compra.objects.filter(estado='enviado').order_by('id')
    
    if search:
        ordenes = ordenes.filter(Q(proveedor_orden__proveedor_name__icontains=search))

    paginator = Paginator(ordenes, 5)
    pagina_numero = request.GET.get('pagina')
    
    try:
        ordenes = paginator.page(pagina_numero)
    except PageNotAnInteger:
        ordenes = paginator.page(1)
    except EmptyPage:
        ordenes = paginator.page(paginator.num_pages)
    
    return render(request, 'proveedores/orden_list_enviada.html', {'ordenes': ordenes, 'search': search, 'pagina_obj': ordenes})



@login_required
def orden_list_aceptada(request, page=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    
    search = request.GET.get('search')
    ordenes = Orden_compra.objects.filter(estado='aceptado').order_by('id')
    
    if search:
        ordenes = ordenes.filter(Q(proveedor_orden__proveedor_name__icontains=search))

    paginator = Paginator(ordenes, 5)
    pagina_numero = request.GET.get('pagina')
    
    try:
        ordenes = paginator.page(pagina_numero)
    except PageNotAnInteger:
        ordenes = paginator.page(1)
    except EmptyPage:
        ordenes = paginator.page(paginator.num_pages)
    
    return render(request, 'proveedores/orden_list_aceptada.html', {'ordenes': ordenes, 'search': search, 'pagina_obj': ordenes})



@login_required
def orden_list_rechazada(request, page=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    
    search = request.GET.get('search')
    ordenes = Orden_compra.objects.filter(estado='rechazado').order_by('id')
    
    if search:
        ordenes = ordenes.filter(Q(proveedor_orden__proveedor_name__icontains=search))

    paginator = Paginator(ordenes, 5)
    pagina_numero = request.GET.get('pagina')
    
    try:
        ordenes = paginator.page(pagina_numero)
    except PageNotAnInteger:
        ordenes = paginator.page(1)
    except EmptyPage:
        ordenes = paginator.page(paginator.num_pages)
    
    return render(request, 'proveedores/orden_list_rechazada.html', {'ordenes': ordenes, 'search': search, 'pagina_obj': ordenes})


@login_required
def orden_list_anulada(request, page=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    
    search = request.GET.get('search')
    ordenes = Orden_compra.objects.filter(estado='anulado').order_by('id')
    
    if search:
        ordenes = ordenes.filter(Q(proveedor_orden__proveedor_name__icontains=search))

    paginator = Paginator(ordenes, 5)
    pagina_numero = request.GET.get('pagina')
    
    try:
        ordenes = paginator.page(pagina_numero)
    except PageNotAnInteger:
        ordenes = paginator.page(1)
    except EmptyPage:
        ordenes = paginator.page(paginator.num_pages)
    
    return render(request, 'proveedores/orden_list_anulada.html', {'ordenes': ordenes, 'search': search, 'pagina_obj': ordenes})

@login_required
def orden_save(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    proveedores = Proveedor.objects.all()
    productos = Product.objects.all()

    if request.method == 'POST':
        proveedor_orden = request.POST.get('proveedor_orden')
        producto_orden = request.POST.getlist('producto_orden[]')
        cantidad_orden = request.POST.getlist('cantidad_orden[]')
        monto_orden = request.POST.get('monto_orden')

        try:
            proveedor_instance = Proveedor.objects.get(proveedor_name=proveedor_orden)
        except Proveedor.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'Proveedor no encontrado')
            return render(request, 'proveedores/orden_crear.html', {'profiles': profile, 'proveedores': proveedores, 'productos': productos})

        if not producto_orden or not cantidad_orden:
            messages.add_message(request, messages.INFO, 'Debes ingresar toda la información')
            return render(request, 'proveedores/orden_crear.html', {'profiles': profile, 'proveedores': proveedores, 'productos': productos})

        try:
            with transaction.atomic():
                orden = Orden_compra(proveedor_orden=proveedor_instance, monto = monto_orden)
                orden.save()

                for prod, cant in zip(producto_orden, cantidad_orden):
                    producto = Product.objects.get(supply_name=prod)
                    detalle = Producto_Orden(
                        orden_id=orden,
                        producto=producto,
                        cantidad_orden=cant,
                    )
                    detalle.save()
                messages.add_message(request, messages.SUCCESS, 'Orden creada con éxito')
                return redirect('orden_crear')  # Redirige a la página de creación para limpiar el formulario
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Error al crear la orden: {str(e)}')
            return render(request, 'proveedores/orden_crear.html', {'profiles': profile, 'proveedores': proveedores, 'productos': productos})
    else:
        messages.add_message(request, messages.ERROR, 'Error en el método de envío')
        return redirect('orden_crear')


@login_required
def orden_crear(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id not in [1, 2]:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')
    
    proveedores = Proveedor.objects.all()
    productos = Product.objects.all()
    template_name = 'proveedores/orden_crear.html'
    
    return render(request, template_name, {'profiles': profiles, 'proveedores': proveedores, 'productos': productos})

def cambiar_estado_orden_enviada(request, orden_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        
        if nuevo_estado in ['aceptado', 'rechazado', 'anulado']:
            orden = get_object_or_404(Orden_compra, id=orden_id)
            orden.estado = nuevo_estado
            orden.save()
            messages.add_message(request, messages.INFO, 'Se ha cambiado el estado de la orden')
            return redirect('orden_list_enviada')
        else:
            messages.add_message(request, messages.INFO, 'Debe seleccionar un estado nuevo para la orden')
            return redirect('orden_list_enviada')

    return redirect('orden_main')

def cambiar_estado_orden_rechazada(request, orden_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado == 'anulado':
            orden = Orden_compra.objects.get(id=orden_id)
            orden.estado = nuevo_estado
            orden.save()
            messages.add_message(request, messages.INFO, 'Se ha cambiado el estado de la orden')
            return redirect('orden_list_rechazada')
        else:
            messages.error(request, 'El valor enviado para el nuevo estado no es válido.')
        return redirect('orden_list_rechazada')  # Redirigir a la página principal de órdenes o donde desees


    # Si el método de solicitud no es POST, simplemente redirigir de nuevo a la lista de órdenes
    return redirect('orden_main')

def cambiar_estado_orden_aceptada(request, orden_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado == 'anulado':
            orden = Orden_compra.objects.get(id=orden_id)
            orden.estado = nuevo_estado
            orden.save()
            messages.add_message(request, messages.INFO, 'Se ha cambiado el estado de la orden')
            return redirect('orden_list_aceptada')
        else:
            messages.error(request, 'El valor enviado para el nuevo estado no es válido.')
        return redirect('orden_list_aceptada')  # Redirigir a la página principal de órdenes o donde desees

    # Si el método de solicitud no es POST, simplemente redirigir de nuevo a la lista de órdenes
    return redirect('orden_main')

@login_required
def eliminar_orden(request, orden_id):
    # Obtener la orden a eliminar
    orden = get_object_or_404(Orden_compra, id=orden_id)

    # Verificar si se ha enviado una solicitud POST
    if request.method == 'POST':
        # Verificar si el usuario tiene permisos para eliminar la orden
        if request.user.profile.group_id != 1:
            messages.error(request, 'No tienes permisos para eliminar órdenes.')
            return redirect('check_group_main')

        # Verificar si el valor enviado es "eliminar"
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado == "eliminar":
            # Eliminar la orden
            orden.delete()
            messages.success(request, f'La orden ha sido eliminada correctamente.')
        else:
            messages.error(request, 'El valor enviado para el nuevo estado no es válido.')
        return redirect('orden_list_anulada')  # Redirigir a la página principal de órdenes o donde desees

    # Si la solicitud no es POST, renderizar un mensaje de error
    messages.error(request, 'Se requiere una solicitud POST para eliminar la orden.')
    return redirect('orden_list_anulada')

@login_required
def detalle_orden_de_compra_enviada(request, orden_id):
    orden = get_object_or_404(Orden_compra, id=orden_id)
    orden_productos = orden.producto_orden_set.all()
    return render(request, 'detalle_orden_de_compra_enviada.html', {'orden': orden, 'orden_productos': orden_productos})

@login_required
def detalle_orden_de_compra_aceptada(request, orden_id):
    orden = get_object_or_404(Orden_compra, id=orden_id)
    orden_productos = orden.producto_orden_set.all()
    return render(request, 'detalle_orden_de_compra_aceptada.html', {'orden': orden, 'orden_productos': orden_productos})

@login_required
def detalle_orden_de_compra_rechazada(request, orden_id):
    orden = get_object_or_404(Orden_compra, id=orden_id)
    orden_productos = orden.producto_orden_set.all()
    return render(request, 'detalle_orden_de_compra_rechazada.html', {'orden': orden, 'orden_productos': orden_productos})

@login_required
def detalle_orden_de_compra_anulada(request, orden_id):
    orden = get_object_or_404(Orden_compra, id=orden_id)
    orden_productos = orden.producto_orden_set.all()
    return render(request, 'detalle_orden_de_compra_anulada.html', {'orden': orden, 'orden_productos': orden_productos})

@login_required
def editar_orden(request, orden_id):
    profile = get_object_or_404(Profile, user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    proveedores = Proveedor.objects.all()
    productos = Product.objects.all()
    orden = get_object_or_404(Orden_compra, pk=orden_id)
    productos_orden = Producto_Orden.objects.filter(orden_id=orden)

    if request.method == 'POST':
        # Proveedor_orden is not fetched from POST anymore
        producto_orden = request.POST.getlist('producto_orden[]')
        cantidad_orden = request.POST.getlist('cantidad_orden[]')
        monto_orden = request.POST.get("monto_orden")
        
        if not producto_orden or not cantidad_orden:
            messages.add_message(request, messages.INFO, 'Debes ingresar toda la información')
            return render(request, 'editar_orden.html', {
                'profiles': profile, 'proveedores': proveedores, 'productos': productos, 
                'orden': orden, 'productos_orden': productos_orden
            })

        try:
            with transaction.atomic():
                # Update the amount only
                orden.monto = monto_orden
                orden.save()

                # Delete old products and add the new ones
                Producto_Orden.objects.filter(orden_id=orden).delete()
                for prod, cant in zip(producto_orden, cantidad_orden):
                    producto = Product.objects.get(supply_name=prod)
                    detalle = Producto_Orden(
                        orden_id=orden,
                        producto=producto,
                        cantidad_orden=cant,
                    )
                    detalle.save()
                
                messages.add_message(request, messages.SUCCESS, 'Orden actualizada con éxito')
                return redirect('editar_orden', orden_id=orden.id)
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Error al actualizar la orden: {str(e)}')
            return render(request, 'editar_orden.html', {
                'profiles': profile, 'proveedores': proveedores, 'productos': productos, 
                'orden': orden, 'productos_orden': productos_orden
            })
    else:
        return render(request, 'editar_orden.html', {
            'profiles': profile, 'proveedores': proveedores, 'productos': productos, 
            'orden': orden, 'productos_orden': productos_orden
        })
        
#DASHBOARDS

@login_required
def get_chart_oc_1(request):

    proveedores = Proveedor.objects.all()
    
    # Lista para almacenar los nombres completos de los proveedores y montos acumulados
    nombres_proveedor = []
    montos = []
    
    for proveedor in proveedores:
        nombre_completo = proveedor.get_nombre_completo()
        nombres_proveedor.append(nombre_completo)
        ordenes_proveedor = Orden_compra.objects.filter(proveedor_orden=proveedor)
        monto_acumulado = sum(orden.monto for orden in ordenes_proveedor)
        montos.append(monto_acumulado)
    
    chart_data = {
        'xAxis': {
            'type': 'category',
            'data': nombres_proveedor
        },
        'yAxis': {
            'type': 'value'
        },
        'series': [
            {
                'data': montos,
                'type': 'bar'
            }
        ]
    }

    return JsonResponse(chart_data)
