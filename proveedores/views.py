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
from django.db.models import Sum, Q
import re

from registration.models import Profile
from proveedores.models import Proveedor, Orden_compra, Producto_Orden, Prov_prod
from inventario.models import Product
from administrator.views import validar_email,validar_rut,validar_string,validar_numero,validar_int
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
    
    productos = Product.objects.all()

    if request.method == 'POST':
        proveedor_form = ProveedorForm(request.POST)
        if proveedor_form.is_valid():
            proveedor = proveedor_form.save(commit=False)
            proveedor.activo = True  # Establecer el proveedor como activo
            proveedor.save()
            
            messages.success(request, 'Proveedor y productos asociados creados exitosamente.')
            return redirect('proveedores/proveedores_crear.html')  # Redirige a la vista deseada
    else:
        proveedor_form = ProveedorForm()
    
    return render(request, 'proveedores/proveedores_crear.html', {'proveedor_form': proveedor_form, 'productos': productos})

#GUARDAR UN PROVEEDOR
@login_required
def proveedor_save(request):
    #Comprobar que el usuario es administrador
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')
    
    #Se extraen y guardan los datos ingresados por el usuario mediante POST
    if request.method == 'POST':
        errores = []
        proveedor_name = request.POST.get('proveedor_name')
        proveedor_last_name = request.POST.get('proveedor_last_name')
        proveedor_rut = request.POST.get('proveedor_rut')
        proveedor_mail = request.POST.get('proveedor_mail')
        proveedor_address = request.POST.get('proveedor_address')
        proveedor_region = request.POST.get('region')
        proveedor_comuna = request.POST.get('comuna')
        proveedor_phone = request.POST.get('proveedor_phone')
        template_name = 'proveedores/proveedores_crear.html'
        producto = request.POST.getlist('producto_orden[]')
        producto_nuevo = request.POST.getlist('producto_nuevo[]')
        codigo_nuevo = request.POST.getlist('codigo_nuevo[]')
        unidad_nuevo = request.POST.getlist('unidad_nuevo[]')

        # Validaciones
        if not validar_string(proveedor_name, request):
            errores.append('Nombre inválido')
        if not validar_string(proveedor_last_name, request):
            errores.append('Apellido inválido')
        if not validar_numero(proveedor_phone, request):
            errores.append('Número de teléfono inválido')
        if not validar_email(proveedor_mail, request):
            errores.append('Correo electrónico inválido')
        if not validar_rut(proveedor_rut, request):
            errores.append('RUT inválido')
        
        #Validación para el ingreso de los datos en el formato solicitado al usuario
        if errores:
            messages.add_message(request, messages.INFO, 'Hubo algunos errores al crear el proveedor: ' + ', '.join(errores))
            return render(request, template_name)
        
        #Validación para evitar campos vacíos
        if any(field == '' for field in [proveedor_name, proveedor_last_name, proveedor_rut, proveedor_mail, proveedor_address, proveedor_region, proveedor_comuna, proveedor_phone]):
            messages.add_message(request, messages.INFO, 'Debes ingresar toda la información')
            return redirect('proveedores_main')
        
        #Validaciones para crear proveedores con ruts y emails únicos
        rut_exist = Proveedor.objects.filter(proveedor_rut=proveedor_rut).exists()
        mail_exist = Proveedor.objects.filter(proveedor_mail=proveedor_mail).exists()
        
        if not rut_exist:
            if not mail_exist:
                
                try:
                    # función atomic para ir paso a paso con el procedimiento. Si resulta algún error, se cancelará todo el proceso
                    with transaction.atomic():
                        #Se crea el proveedor nuevo con los datos guardados anteriormente
                        proveedor_save = Proveedor(
                            proveedor_name=proveedor_name,
                            proveedor_last_name=proveedor_last_name,
                            proveedor_rut=proveedor_rut,
                            proveedor_mail=proveedor_mail,
                            proveedor_address=proveedor_address,
                            proveedor_region=proveedor_region,
                            proveedor_comuna=proveedor_comuna,
                            proveedor_phone=proveedor_phone,
                        )
                        proveedor_save.save()
                        
                        print(codigo_nuevo)
                        
                        for prod_id in producto: #-> Se recorre el listado de productos ingresados por el usuario para asociarlos al proveedor a crear
                            try:
                                prod_id = int(prod_id)  # Convertir prod_id a entero
                                producto_instance = Product.objects.get(id=prod_id) #Instanciación del producto
                            #Validación de que el producto (existente) ingresado exista en la base de datos 
                            except Product.DoesNotExist:
                                messages.add_message(request, messages.ERROR, f'Producto con ID {prod_id} no encontrado')
                                return render(request, template_name)
                            except ValueError:
                                messages.add_message(request, messages.ERROR, 'Error en los datos de los productos.')
                                return render(request, template_name)
                            
                            Prov_prod.objects.create(
                                proveedor=proveedor_save,
                                producto=producto_instance,
                            )
                            messages.add_message(request, messages.INFO, 'Productos guardados con éxito')

                    # Verificar si la lista de productos nuevos no está vacía
                    if producto_nuevo and all(producto_nuevo) and codigo_nuevo and all(codigo_nuevo) and unidad_nuevo and all(unidad_nuevo):
                        print("xddddlol")
                        for producto, codigo, unidad in zip(producto_nuevo, codigo_nuevo, unidad_nuevo):
                            # Formatear y validar el código del nuevo producto
                            codigo_formateado = f'SKU{codigo}'
                            #Validación del código en formato solicitado
                            if not re.match(r'^SKU\d{4}$', codigo_formateado):
                                messages.add_message(request, messages.ERROR, f'El código del producto {codigo} debe tener el formato SKU seguido de 4 dígitos')
                                return render(request, template_name)

                            # Creación del nuevo producto
                            nuevo_producto = Product.objects.create(
                                supply_name=producto,
                                supply_code=codigo_formateado,
                                supply_unit=unidad,
                                supply_initial_stock=0,
                                supply_input=0,
                                supply_output=0,
                                supply_total=0
                            )

                            # Obtener la instancia del producto recién creado
                            producto_instance_nuevo = Product.objects.get(id=nuevo_producto.id)

                            # Crear la relación en Prov_prod
                            Prov_prod.objects.create(
                                proveedor=proveedor_save,
                                producto=producto_instance_nuevo,
                            )
                        messages.add_message(request, messages.INFO, 'Productos creados y guardados con éxito')
                    else:
                        print("No hay productos nuevos para agregar.") #Validación e caso de error al crear el producto nuevo
                except Exception as e:
                    messages.add_message(request, messages.ERROR, f'Error al guardar productos: {str(e)}') #Validación en caso de no guardar los productos
                        
                        
                messages.add_message(request, messages.INFO, 'Proveedor ingresado con éxito')
                return redirect('proveedores_activos')
            else:
                #Validación en caso de un email existente
                messages.add_message(request, messages.INFO, 'El correo que está tratando de ingresar, ya existe en nuestros registros')
                return redirect('proveedores_activos')
        else:
            #Valdació en caso de un rut existente
            messages.add_message(request, messages.INFO, 'El RUT que está tratando de ingresar, ya existe en nuestros registros')
            return redirect('proveedores_activos')
    else:
        #Validación de POST
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
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor_productos = proveedor.prov_prod_set.all()
    template_name = 'proveedores/proveedor_ver.html'
    return render(request, template_name, {'profile': profile, 'proveedor_data': proveedor_data, 'proveedor':proveedor, 'proveedor_productos':proveedor_productos})

#EDITAR PROVEEDOR
@login_required
def proveedor_edit(request, proveedor_id):
    #Validación de Permisos de administrador
    profile = Profile.objects.get(user_id=request.user.id)
    productos = Product.objects.all()
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    proveedor = get_object_or_404(Proveedor, id=proveedor_id)

    #Recolección de los datos mediante POST
    if request.method == 'POST':
        proveedor_name = request.POST.get('proveedor_name')
        proveedor_last_name = request.POST.get('proveedor_last_name')
        proveedor_mail = request.POST.get('proveedor_mail')
        proveedor_phone = request.POST.get('proveedor_phone')
        proveedor_address = request.POST.get('proveedor_address')
        proveedor_region = request.POST.get('region')
        proveedor_comuna = request.POST.get('comuna')
        producto = request.POST.getlist('producto_orden[]')
        producto_nuevo = request.POST.getlist('producto_nuevo[]')
        codigo_nuevo = request.POST.getlist('codigo_nuevo[]')
        unidad_nuevo = request.POST.getlist('unidad_nuevo[]')

        #Validación de email existente, exceptuando al email propio del proveedor a editar
        mail_exist = Proveedor.objects.filter(proveedor_mail=proveedor_mail).exclude(id=proveedor_id).exists()
        if not mail_exist:
            try:
                # función atomic para ir paso a paso con el procedimiento. Si resulta algún error, se cancelará todo el proceso
                with transaction.atomic():
                    proveedor.proveedor_name = proveedor_name
                    proveedor.proveedor_last_name = proveedor_last_name
                    proveedor.proveedor_mail = proveedor_mail
                    proveedor.proveedor_phone = proveedor_phone
                    proveedor.proveedor_address = proveedor_address
                    proveedor.proveedor_region = proveedor_region
                    proveedor.proveedor_comuna = proveedor_comuna
                    proveedor.save()

                    # Limpiar productos actuales y volver a asignarlos
                    Prov_prod.objects.filter(proveedor=proveedor).delete()

                    # Agregar productos existentes
                    for prod_id in producto:
                        try:
                            prod_id = int(prod_id)  # Convertir prod_id a entero
                            producto_instance = Product.objects.get(id=prod_id)
                        except Product.DoesNotExist:
                            messages.add_message(request, messages.ERROR, f'Producto con ID {prod_id} no encontrado')
                            return render(request, 'proveedores/proveedor_edit.html', {'proveedor_data': proveedor, 'productos': productos})
                        except ValueError:
                            messages.add_message(request, messages.ERROR, 'Error en los datos de los productos.')
                            return render(request, 'proveedores/proveedor_edit.html', {'proveedor_data': proveedor, 'productos': productos})

                        #Asociación de proveedor al producto asginado
                        Prov_prod.objects.create(
                            proveedor=proveedor,
                            producto=producto_instance,
                        )

                    # Crear y agregar productos nuevos solo si no están vacíos
                    for producto, codigo, unidad in zip(producto_nuevo, codigo_nuevo, unidad_nuevo):
                        if producto.strip() and codigo.strip() and unidad.strip():  # Validar campos no vacíos
                            nuevo_producto = Product.objects.create(
                                supply_name=producto,
                                supply_code=codigo,
                                supply_unit=unidad,
                                supply_initial_stock=0,
                                supply_input=0,
                                supply_output=0,
                                supply_total=0
                            )
                            #Creación del producto nuevo
                            Prov_prod.objects.create(
                                proveedor=proveedor,
                                producto=nuevo_producto,
                            )

                messages.add_message(request, messages.INFO, 'Proveedor editado con éxito')
            except Exception as e:
                messages.add_message(request, messages.ERROR, f'Error al guardar productos: {str(e)}')
                return render(request, 'proveedores/proveedor_edit.html', {'proveedor_data': proveedor, 'productos': productos})

            return redirect('proveedores_activos')
        else:
            messages.add_message(request, messages.INFO, 'El correo que está tratando de ingresar, ya existe en nuestros registros')
            return render(request, 'proveedores/proveedor_edit.html', {'proveedor_data': proveedor, 'productos': productos})

    else:
        return render(request, 'proveedores/proveedor_edit.html', {'proveedor_data': proveedor, 'productos': productos})


#ELIMINAR PROVEEDOR
def proveedor_delete(request, proveedor_id):
    #Validación de permisoss de administrador
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    #Identifica el proveedor seleccionado
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    #Eliminación del Proveedor
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

#ARCHIVO DE EJEMPLO PARA CARGA MASIVA
@login_required
def import_file_proveedor(request):
    #Validación permisos de administrador
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    
    #Identifiación del response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="archivo_importacion_proveedor.xlsx"'

    #Nombre de columnas para el archivo
    
    wb = Workbook()
    ws = wb.active
    ws.title = 'carga_masiva'

    columns = ['Rut', 'Nombre', 'Apellido', 'Correo', 'Teléfono', 'Dirección', 'Región', 'Comuna', 'Insumo']
    ws.append(columns)


    #Información de ejemplo
    example_data = [
        'ej: 17605812-2',
        'ej: Nombre proveedor',
        'ej: Apellido proveedor',
        'ej: bc@gmail.com',
        'ej: 955642334',
        'ej: Av. central 123',
        'ej: Tarapacá',
        'ej: Iquique',
        'ej: Palta'
    ]
    ws.append(example_data)
 
    wb.save(response)
    return response

#CARGA MASIVA
@login_required
def carga_masiva_proveedor_save(request):
    #Validación de permisos de administrador
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        try:
            # Leer el archivo Excel
            data = pd.read_excel(request.FILES['myfile'], engine='openpyxl', skiprows=1)
            df = pd.DataFrame(data)
            print("Contenido del DataFrame:")
            print(df)  # Mostrar el contenido del DataFrame para verificar los datos

            acc = 0

            # Obtener los proveedores activos una vez antes de iterar
            proveedores_activos = Proveedor.objects.filter(activo=True).values_list('proveedor_rut', 'proveedor_mail')
            ruts_activos = {proveedor[0] for proveedor in proveedores_activos}
            correos_activos = {proveedor[1] for proveedor in proveedores_activos}

            for item in df.itertuples(index=False):
                proveedor_rut = str(item[0])
                proveedor_name = str(item[1])
                proveedor_last_name = str(item[2])
                proveedor_mail = str(item[3])
                proveedor_phone = str(item[4])
                proveedor_address = str(item[5])
                proveedor_region = str(item[6])
                proveedor_comuna = str(item[7])
                proveedor_insumo = str(item[8])  # Asegúrate de que este campo exista en tu modelo
                
                # Mensaje de depuración para cada registro
                print(f"Procesando RUT: {proveedor_rut}, Correo: {proveedor_mail}")

                # Validación de RUT y correo
                if proveedor_rut in ruts_activos:
                    messages.add_message(request, messages.INFO, f'El RUT "{proveedor_rut}" ya existe en nuestros registros.')
                    print(f'El RUT "{proveedor_rut}" ya existe en nuestros registros.')
                    continue

                if proveedor_mail in correos_activos:
                    messages.add_message(request, messages.INFO, f'El correo electrónico "{proveedor_mail}" ya existe en nuestros registros.')
                    print(f'El correo electrónico "{proveedor_mail}" ya existe en nuestros registros.')
                    continue

                # Guardar proveedor si pasa todas las validaciones
                proveedor_save = Proveedor(
                    proveedor_rut=proveedor_rut,
                    proveedor_name=proveedor_name,
                    proveedor_last_name=proveedor_last_name,
                    proveedor_mail=proveedor_mail,
                    proveedor_phone=proveedor_phone,
                    proveedor_address=proveedor_address,
                    proveedor_region=proveedor_region,
                    proveedor_comuna=proveedor_comuna,
                    proveedor_insumo=proveedor_insumo,
                    activo=True
                )
                proveedor_save.save()
                acc += 1
                print(f'Registro guardado: RUT {proveedor_rut}, Correo {proveedor_mail}')

            messages.add_message(request, messages.INFO, f'Carga masiva finalizada, se importaron {acc} registros')
            print(f'Carga masiva finalizada, se importaron {acc} registros')
            return redirect('carga_masiva_proveedor')

        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Error al procesar el archivo: {str(e)}')
            print(f'Error al procesar el archivo: {str(e)}')
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
        proveedores_activos = proveedores_activos.filter(Q(proveedor_name__icontains=search) | 
            Q(proveedor_last_name__icontains=search))

    # Paginar los resultados
    paginator = Paginator(proveedores_activos, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Renderizar la plantilla con los datos de los proveedores activos
    return render(request, 'proveedores_activos.html', {'p_list_paginate': page_obj, 'paginator': paginator, 'search': search})


@login_required
def proveedores_eliminados(request):
    # Verificar si el usuario tiene permisos
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')
    
    search = request.GET.get('search')
    proveedores_list = Proveedor.objects.filter(activo=False)
    
    if search:
        proveedores_list = proveedores_list.filter(
            Q(proveedor_name__icontains=search) | 
            Q(proveedor_last_name__icontains=search)
        )

    # Obtener el paginador y los resultados paginados
    page_obj, paginator = get_paginated_results(request, proveedores_list)

    return render(request, 'proveedores_eliminados.html', {
        'proveedores_eliminados': page_obj,
        'paginator': paginator,
        'search': search
    })
def get_paginated_results(request, queryset):
    # Paginar los resultados
    paginator = Paginator(queryset, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj, paginator

#RESTAURAR PROVEEDOR
@login_required
def restaurar_proveedor(request, proveedor_id):
    #Validación de permisos de admnistrador
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

#ELIMINACIÓN LÓGICA DEL PROVEEDOR
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

#ELIMINACIÓN FÍSICA DEL PROVEEDOR
def proveedor_delete(request, proveedor_id):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.delete()
    messages.success(request, 'Proveedor eliminado correctamente')
    return redirect(reverse('proveedores_activos'))
 

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
def orden_list_enviada(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')
    
    search = request.GET.get('search')
    ordenes = Orden_compra.objects.filter(estado='enviado').order_by('id')
    
    if search:
        ordenes = ordenes.filter(
            Q(proveedor_orden__proveedor_name__icontains=search) | 
            Q(proveedor_orden__proveedor_last_name__icontains=search)
        )
    paginator = Paginator(ordenes, 4)
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
        ordenes = ordenes.filter(
            Q(proveedor_orden__proveedor_name__icontains=search) | 
            Q(proveedor_orden__proveedor_last_name__icontains=search)
        )
    paginator = Paginator(ordenes, 4)
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
        ordenes = ordenes.filter(
            Q(proveedor_orden__proveedor_name__icontains=search) | 
            Q(proveedor_orden__proveedor_last_name__icontains=search)
        )
    paginator = Paginator(ordenes, 4)
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
        ordenes = ordenes.filter(
            Q(proveedor_orden__proveedor_name__icontains=search) | 
            Q(proveedor_orden__proveedor_last_name__icontains=search)
        )
    paginator = Paginator(ordenes, 4)
    pagina_numero = request.GET.get('pagina')
    
    try:
        ordenes = paginator.page(pagina_numero)
    except PageNotAnInteger:
        ordenes = paginator.page(1)
    except EmptyPage:
        ordenes = paginator.page(paginator.num_pages)
    
    return render(request, 'proveedores/orden_list_anulada.html', {'ordenes': ordenes, 'search': search, 'pagina_obj': ordenes})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Proveedor, Orden_compra, Producto_Orden
from inventario.models import Product

@login_required
def orden_save(request):
    #Validación Permisos de administrador
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')

    #Proveedores y Productos guardados para después recorrerlos
    proveedores = Proveedor.objects.all()
    productos = Product.objects.all()

    #Recolección de los datos mediante POST
    if request.method == 'POST':
        proveedor_orden = request.POST.get('proveedor_orden')
        producto_orden = request.POST.getlist('producto_orden[]')
        cantidad_orden = request.POST.getlist('cantidad_orden[]')
        monto_orden = request.POST.get('monto_orden')

        # Validar que el proveedor existe
        try:
            proveedor_instance = Proveedor.objects.get(id=proveedor_orden)
        except Proveedor.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'Proveedor no encontrado')
            return render(request, 'proveedores/orden_crear.html', {'profiles': profile, 'proveedores': proveedores, 'productos': productos})

        # Validar que los productos y cantidades han sido proporcionados
        if not producto_orden or not cantidad_orden:
            messages.add_message(request, messages.INFO, 'Debes ingresar toda la información de los productos y sus cantidades')
            return render(request, 'proveedores/orden_crear.html', {'profiles': profile, 'proveedores': proveedores, 'productos': productos})

        # Validar cantidades y monto
        try:
            cantidades_validas = [int(cant) if cant else 0 for cant in cantidad_orden]
            monto_valido = int(monto_orden)
        except ValueError:
            messages.add_message(request, messages.ERROR, 'Las cantidades y el monto deben ser números enteros válidos')
            return render(request, 'proveedores/orden_crear.html', {'profiles': profile, 'proveedores': proveedores, 'productos': productos})

        # Validar que al menos un producto tenga una cantidad mayor a 0
        if all(cant == 0 for cant in cantidades_validas):
            messages.add_message(request, messages.ERROR, 'Debe haber al menos un producto con una cantidad mayor a 0')
            return render(request, 'proveedores/orden_crear.html', {'profiles': profile, 'proveedores': proveedores, 'productos': productos})

        try:
            #Función atomic para ir paso a paso en el procedimiento y cancelar todo en caso de error
            with transaction.atomic():
                orden = Orden_compra(proveedor_orden=proveedor_instance, monto=monto_valido) #Instancia de la nueva orden
                orden.save()

                #Recorrido de todos los productos y cantidades ingresadas por el usuario
                for prod, cant in zip(producto_orden, cantidades_validas):
                    try:
                        producto_instance = Product.objects.get(id=prod)
                        #Validación
                    except Product.DoesNotExist:
                        messages.add_message(request, messages.ERROR, f'Producto con ID {prod} no encontrado')
                        return render(request, 'proveedores/orden_crear.html', {'profiles': profile, 'proveedores': proveedores, 'productos': productos})

                    #Relación de la órden de compra y sus productos respectivos
                    Producto_Orden.objects.create(
                        orden_id=orden,
                        producto=producto_instance,
                        cantidad_orden=cant,
                    )
                #Mensaje de éxito
                messages.add_message(request, messages.SUCCESS, f'Orden de compra #{orden.id} creada con éxito')
                return redirect('orden_crear')
        #Mensaje de error
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Error al crear la orden: {str(e)}')
            return redirect('orden_crear')
    #Mensaje de error
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
    #Recolección de datos mediante POST
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        
        #Cambio de estado solicitado por ususario
        if nuevo_estado in ['aceptado', 'rechazado', 'anulado']:
            orden = get_object_or_404(Orden_compra, id=orden_id)#Instanciación de la orden
            orden.estado = nuevo_estado #Cambio de estado
            orden.save()
            #Mensaje de éxito
            messages.add_message(request, messages.INFO, 'Se ha cambiado el estado de la orden')
            return redirect('orden_list_enviada')
        else:
            "Mensaje de error"
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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Proveedor, Orden_compra, Producto_Orden
from inventario.models import Product
@login_required
def editar_orden(request, orden_id):
    #Validación de permisos de administrador
    profile = get_object_or_404(Profile, user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')

    #Proveedores y Productos guardados para después recorrerlos
    proveedores = Proveedor.objects.all()
    productos = Product.objects.all()
    
    #Identidicación de orden a editar y sus productos correspondientes
    orden = get_object_or_404(Orden_compra, pk=orden_id)
    productos_orden = Producto_Orden.objects.filter(orden_id=orden)

    #Recolección de Datos mediante POST
    if request.method == 'POST':
        producto_orden = request.POST.getlist('producto_orden[]')
        cantidad_orden = request.POST.getlist('cantidad_orden[]')
        monto_orden = request.POST.get("monto_orden")

        #Validación de campos vacíos
        if not producto_orden or not cantidad_orden:
            messages.add_message(request, messages.INFO, 'Debes ingresar toda la información')
            return render(request, 'editar_orden.html', {
                'profiles': profile, 'proveedores': proveedores, 'productos': productos, 
                'orden': orden, 'productos_orden': productos_orden,
                'form_data': zip(producto_orden, cantidad_orden)
            })

        try:
            #Validación de cantidades positivas y distintas de 0
            cantidades_validas = [int(cant) if cant else 0 for cant in cantidad_orden]
            monto_valido = int(monto_orden)
        except ValueError:
            #Mensaje de error por números inválidos
            messages.add_message(request, messages.ERROR, 'Las cantidades y el monto deben ser números enteros válidos')
            return render(request, 'editar_orden.html', {
                'profiles': profile, 'proveedores': proveedores, 'productos': productos, 
                'orden': orden, 'productos_orden': productos_orden,
                'form_data': zip(producto_orden, cantidad_orden)
            })
        #Validación de cantidades vacías
        if all(cant == 0 for cant in cantidades_validas):
            messages.add_message(request, messages.ERROR, 'Debe haber al menos un producto con una cantidad mayor a 0')
            return render(request, 'editar_orden.html', {
                'profiles': profile, 'proveedores': proveedores, 'productos': productos, 
                'orden': orden, 'productos_orden': productos_orden,
                'form_data': zip(producto_orden, cantidad_orden)
            })

        try:
            #Función atomic, para procesar paso a paso y en caso de error, cancelar todo
            with transaction.atomic():
                orden.monto = monto_valido #Cambio de monto
                orden.save()

                #Eliminación de relación anterior entre orden de compra y sus productos
                Producto_Orden.objects.filter(orden_id=orden).delete()
                for prod, cant in zip(producto_orden, cantidades_validas):
                    try:
                        producto = Product.objects.get(id=prod) #Instanciación de producto
                    except Product.DoesNotExist:
                        #Mensaje de error
                        messages.add_message(request, messages.ERROR, f'Producto con ID {prod} no encontrado')
                        return render(request, 'editar_orden.html', {
                            'profiles': profile, 'proveedores': proveedores, 'productos': productos, 
                            'orden': orden, 'productos_orden': productos_orden,
                            'form_data': zip(producto_orden, cantidad_orden)
                        })

                    #Creación de nueva relación orden de compra y producto
                    Producto_Orden.objects.create(
                        orden_id=orden,
                        producto=producto,
                        cantidad_orden=cant,
                    )
                #Mensaje de Éxito
                messages.add_message(request, messages.SUCCESS, 'Orden actualizada con éxito')
                return redirect('editar_orden', orden_id=orden.id)
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Error al actualizar la orden: {str(e)}')
            return render(request, 'editar_orden.html', {
                'profiles': profile, 'proveedores': proveedores, 'productos': productos, 
                'orden': orden, 'productos_orden': productos_orden,
                'form_data': zip(producto_orden, cantidad_orden)
            })
    else:
        return render(request, 'editar_orden.html', {
            'profiles': profile, 'proveedores': proveedores, 'productos': productos, 
            'orden': orden, 'productos_orden': productos_orden,
            'form_data': zip([p.producto.id for p in productos_orden], [p.cantidad_orden for p in productos_orden])
        })



        
#DASHBOARDS

@login_required
def get_chart_oc_1(request):

    ordenes = Orden_compra.objects.all()
    

    Enviadas = int(ordenes.values("estado").filter(estado="enviado").count())
    Rechazadas = int(ordenes.values("estado").filter(estado="rechazado").count())
    Aceptadas = int(ordenes.values("estado").filter(estado="aceptado").count())
    Anuladas = int(ordenes.values("estado").filter(estado="anulado").count())

    chart_data = {
        "title": {
            "text": 'Cantidad de órdenes'
        },   
        'tooltip': {
            'show': True,
            'trigger': "axis",
            'triggerOn': "mousemove|click"
        },
        'xAxis': {
            'type': 'category',
            'data': ['Enviadas',"Rechazadas","Aceptadas","Anuladas"],
        },
        'yAxis': {
            'type': 'value'
        },
        'series': [
            {
                'data': [Enviadas,Rechazadas,Aceptadas,Anuladas],
                'type': 'bar',

            }
        ]
    }

    return JsonResponse(chart_data)

def cargar_productos(request):
    proveedor_id = request.GET.get('proveedor')
    productos = Product.objects.filter(prov_prod__proveedor_id=proveedor_id).distinct()
    productos_list = list(productos.values('id', 'supply_name', 'supply_unit'))

    return JsonResponse(productos_list, safe=False)
