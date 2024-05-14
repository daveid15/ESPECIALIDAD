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


from registration.models import Profile
from proveedores.models import Proveedor, Orden_compra
from inventario.models import Product
from administrator.views import validar_email,validar_rut,validar_string,validar_numero
# Create your views here.
@login_required
def proveedores_main(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'proveedores/proveedores_main.html'
    return render(request,template_name,{'profiles':profiles})


@login_required
def proveedores_crear(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'proveedores/proveedores_crear.html'
    return render(request,template_name,{'profiles':profiles})

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

        proveedor_save = Proveedor(
            proveedor_name=proveedor_name,
            proveedor_last_name=proveedor_last_name,
            proveedor_rut=proveedor_rut,
            proveedor_mail=proveedor_mail,
            proveedor_address=proveedor_address,
            proveedor_region=proveedor_region,
            proveedor_comuna=proveedor_comuna,
            proveedor_phone=proveedor_phone
        )
        proveedor_save.save()
        messages.add_message(request, messages.INFO, 'Proveedor ingresado con éxito')
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

    if page is None:
        page = request.GET.get('page')
    else:
        page = page

    if request.GET.get('page') is None:
        page = page
    else:
        page = request.GET.get('page')

    if search is None:
        search = request.GET.get('search')
    else:
        search = search

    if request.GET.get('search') is None:
        search = search
    else:
        search = request.GET.get('search')

    if request.method == 'POST':
        search = request.POST.get('search')
        page = None

    if search is None or search == "None":
        p_count = Proveedor.objects.filter(proveedor_name='a').count()
        p_list_array = Proveedor.objects.all().order_by('proveedor_name')
    else:
        p_count = Proveedor.objects.filter(proveedor_name='a').filter(proveedor_name__icontains=search).count()
        p_list_array = Proveedor.objects.all().filter(proveedor_name__icontains=search).order_by('proveedor_name')

    p_list = []
    for p in p_list_array:
        p_list.append({
            'id': p.id,
            'proveedor_name': p.proveedor_name,
            'proveedor_mail': p.proveedor_mail,
            'proveedor_phone': p.proveedor_phone,
        })

    paginator = Paginator(p_list, 4)
    p_list_paginate = paginator.get_page(page)

    template_name = 'proveedores/proveedor_list.html'
    return render(request, template_name, {'template_name': template_name, 'p_list_paginate': p_list_paginate, 'paginator': paginator, 'page': page})


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

        proveedor.proveedor_name = proveedor_name
        proveedor.proveedor_last_name = proveedor_last_name
        proveedor.proveedor_mail = proveedor_mail
        proveedor.proveedor_phone = proveedor_phone
        proveedor.proveedor_address = proveedor_address
        proveedor.proveedor_region = proveedor_region
        proveedor.proveedor_comuna = proveedor_comuna
        
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
    return render(request,template_name,{'profiles':profile})

@login_required
def import_file_proveedor(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="archivo_importacion_proveedors.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('carga_masiva')
    row_num = 0
    columns = ['proveedor_name','proveedor_mail','proveedor_phone']
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'dd/MM/yyyy'
    for row in range(1):
        row_num += 1
        for col_num in range(3):
            if col_num == 0:
                ws.write(row_num, col_num, 'ej: Nombre proveedor' , font_style)
            if col_num == 1:                           
                ws.write(row_num, col_num, 'abc@gmail.com' , font_style)
            if col_num == 2:                           
                ws.write(row_num, col_num, '55642334' , font_style)
    wb.save(response)
    return response  

@login_required
def carga_masiva_proveedor_save(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        #try:
        print(request.FILES['myfile'])
        data = pd.read_excel(request.FILES['myfile'])
        df = pd.DataFrame(data)
        acc = 0
        for item in df.itertuples():    
            proveedor_name = str(item[1])            
            proveedor_mail = str(item[2])
            proveedor_phone = str(item[3])
            proveedor_save = Proveedor(
                proveedor_name = proveedor_name,            
                proveedor_mail = proveedor_mail,
                proveedor_phone = proveedor_phone,
  
                )
            proveedor_save.save()
        messages.add_message(request, messages.INFO, 'Carga masiva finalizada, se importaron '+str(acc)+' registros')
        return redirect('carga_masiva_proveedor')
    
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

#Órden de Compraa
'''
@login_required
def orden_crear(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    #Consulta en la base de Datos para llamar los datos de Proveedores y colocarlos en el select
    proveedores = Proveedor.objects.all()
    #Consulta en la base de Datos para llamar los datos de Productos y colocarlos en el select
    productos = Product.objects.all()
    template_name = 'proveedores/orden_crear.html'
    print(productos)
    return render(request, template_name, {'profiles': profiles, 'proveedores': proveedores, 'productos': productos})
    '''

@login_required
def orden_save(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')
    
    
    if request.method == 'POST':
        proveedor_orden = request.POST.get('proveedor_orden')
        producto_orden = request.POST.get('producto_orden')
        unidad_orden = request.POST.get('unidad_orden')
        cantidad_orden = request.POST.get('cantidad_orden')
        

        if proveedor_orden == '' or producto_orden == '' or unidad_orden == '' or cantidad_orden == '':
            messages.add_message(request, messages.INFO, 'Debes ingresar toda la información')
            return render(request, template_name, {'profiles': profile})

        orden_save = Orden_compra(
            proveedor_orden=proveedor_orden,
            producto_orden=producto_orden,
            unidad_orden=unidad_orden,
            cantidad_orden=cantidad_orden
        )

        orden_save.save()
        template_name = 'proveedores/orden_crear.html'
        return render(request, template_name, {'profiles': profile})

    
    else:
        messages.add_message(request, messages.INFO, 'Error en el método de envío')


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
def orden_list_enviada(request, page=None, search=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    search = request.GET.get('search')
    ordenes = Orden_compra.objects.filter(estado='enviado')
    if search:
        ordenes = ordenes.filter(Q(proveedor_orden__icontains=search) |
                                 Q(producto_orden__icontains=search) |
                                 Q(unidad_orden__icontains=search) |
                                 Q(cantidad_orden__icontains=search))

    paginator = Paginator(ordenes, 10)
    page_number = request.GET.get('page')
    ordenes = paginator.get_page(page_number)

    return render(request, 'proveedores/orden_list_enviada.html', {'ordenes': ordenes, 'search': search})


@login_required
def orden_list_aceptada(request, page=None, search=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    search = request.GET.get('search')
    ordenes = Orden_compra.objects.filter(estado='aceptado')
    if search:
        ordenes = ordenes.filter(Q(proveedor_orden__icontains=search) |
                                 Q(producto_orden__icontains=search) |
                                 Q(unidad_orden__icontains=search) |
                                 Q(cantidad_orden__icontains=search))

    paginator = Paginator(ordenes, 10)
    page_number = request.GET.get('page')
    ordenes = paginator.get_page(page_number)

    return render(request, 'proveedores/orden_list_aceptada.html', {'ordenes': ordenes, 'search': search})


@login_required
def orden_list_rechazada(request, page=None, search=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    search = request.GET.get('search')
    ordenes = Orden_compra.objects.filter(estado='rechazado')
    if search:
        ordenes = ordenes.filter(Q(proveedor_orden__icontains=search) |
                                 Q(producto_orden__icontains=search) |
                                 Q(unidad_orden__icontains=search) |
                                 Q(cantidad_orden__icontains=search))

    paginator = Paginator(ordenes, 10)
    page_number = request.GET.get('page')
    ordenes = paginator.get_page(page_number)

    return render(request, 'proveedores/orden_list_rechazada.html', {'ordenes': ordenes, 'search': search})


@login_required
def orden_list_anulada(request, page=None, search=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    search = request.GET.get('search')
    ordenes = Orden_compra.objects.filter(estado='anulado')
    if search:
        ordenes = ordenes.filter(Q(proveedor_orden__icontains=search) |
                                 Q(producto_orden__icontains=search) |
                                 Q(unidad_orden__icontains=search) |
                                 Q(cantidad_orden__icontains=search))

    paginator = Paginator(ordenes, 10)
    page_number = request.GET.get('page')
    ordenes = paginator.get_page(page_number)

    return render(request, 'proveedores/orden_list_anulada.html', {'ordenes': ordenes, 'search': search})

@login_required
def orden_crear(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id not in [1, 2]:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')
    
    proveedores = Proveedor.objects.all()
    productos = Product.objects.all()
    template_name = 'proveedores/orden_crear.html'

    if request.method == 'POST':
        proveedor_orden = request.POST.get('proveedor_orden')
        producto_orden = request.POST.get('producto_orden')
        unidad_orden = request.POST.get('unidad_orden')
        cantidad_orden = request.POST.get('cantidad_orden')

        # Mostrar los datos recibidos del formulario
        print("Datos recibidos del formulario:")
        print(f"Proveedor: {proveedor_orden}")
        print(f"Producto: {producto_orden}")
        print(f"Unidad: {unidad_orden}")
        print(f"Cantidad: {cantidad_orden}")

        # Intentar crear la nueva orden de compra
        try:
            nueva_orden = Orden_compra.objects.create(
                proveedor_orden=proveedor_orden,
                producto_orden=producto_orden,
                unidad_orden=unidad_orden,
                cantidad_orden=cantidad_orden,
                # Puedes agregar más campos aquí según sea necesario
            )
            # Guardar el ID de la nueva orden en la sesión
            request.session['nueva_orden_id'] = nueva_orden.id
            print("¡Orden de compra creada con éxito!")
        except Exception as e:
            print(f"Error al crear la orden de compra: {e}")

        # Redirigir al usuario al listado de órdenes
        return redirect('lista_orden')
    
    return render(request, template_name, {'profiles': profiles, 'proveedores': proveedores, 'productos': productos})

def cambiar_estado_orden_enviada(request, orden_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado == 'aceptado' or 'anulado' or 'rechazado':
            orden = Orden_compra.objects.get(id=orden_id)
            orden.estado = nuevo_estado
            orden.save()
            messages.add_message(request, messages.INFO, 'Se ha cambiado el estado de la orden')
            return redirect('orden_list_enviada')
        else:
            messages.error(request, 'El valor enviado para el nuevo estado no es válido.')
        return redirect('orden_list_enviada')  # Redirigir a la página principal de órdenes o donde desees

        
    # Si el método de solicitud no es POST, simplemente redirigir de nuevo a la lista de órdenes
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
            messages.success(request, f'La orden {orden.id} ha sido eliminada correctamente.')
        else:
            messages.error(request, 'El valor enviado para el nuevo estado no es válido.')
        return redirect('orden_list_anulada')  # Redirigir a la página principal de órdenes o donde desees

    # Si la solicitud no es POST, renderizar un mensaje de error
    messages.error(request, 'Se requiere una solicitud POST para eliminar la orden.')
    return redirect('orden_list_anulada')

@login_required
def detalle_orden_de_compra_enviada(request, orden_id):
    orden = get_object_or_404(Orden_compra, id=orden_id)
    return render(request, 'detalle_orden_de_compra_enviada.html', {'orden': orden})

@login_required
def detalle_orden_de_compra_aceptada(request, orden_id):
    orden = get_object_or_404(Orden_compra, id=orden_id)
    return render(request, 'detalle_orden_de_compra_aceptada.html', {'orden': orden})

@login_required
def detalle_orden_de_compra_rechazada(request, orden_id):
    orden = get_object_or_404(Orden_compra, id=orden_id)
    return render(request, 'detalle_orden_de_compra_rechazada.html', {'orden': orden})

@login_required
def detalle_orden_de_compra_anulada(request, orden_id):
    orden = get_object_or_404(Orden_compra, id=orden_id)
    return render(request, 'detalle_orden_de_compra_anulada.html', {'orden': orden})

@login_required
def editar_orden(request, orden_id):
    orden = get_object_or_404(Orden_compra, pk=orden_id)
    if request.method == 'POST':
        # Obtener los datos del formulario POST
        proveedor = request.POST.get('proveedor_orden')
        producto = request.POST.get('producto_orden')
        unidad = request.POST.get('unidad_orden')
        cantidad = request.POST.get('cantidad_orden')
        
        # Actualizar los campos de la orden de compra
        orden.proveedor_orden = proveedor
        orden.producto_orden = producto
        orden.unidad_orden = unidad
        orden.cantidad_orden = cantidad

        # Guardar los cambios en la base de datos
        orden.save()

        # Agregar un mensaje de éxito
        messages.success(request, '¡Los cambios se guardaron correctamente!')

        # Redirigir a la página de detalles de la orden de compra
        return redirect('orden_list_enviada')

    # Si la solicitud es GET, renderizar el formulario de edición
    return render(request, 'editar_orden.html', {'orden': orden})
