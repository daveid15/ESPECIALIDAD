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
from .forms import ProductForm
from django.urls import reverse
from registration.models import Profile
from inventario.models import Product 
import json
import pandas as pd
import xlwt
import traceback
from openpyxl import Workbook
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import os 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 


# Create your views here.
@login_required
def inventario_main(request, page=None, search=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')

    page = request.GET.get('page', page)
    search = request.GET.get('search', search)

    if request.method == 'POST':
        search = request.POST.get('search')
        page = None

    if search is None or search == "None":
        p_list_array = Product.objects.all().order_by('supply_name')
    else:
        p_list_array = Product.objects.filter(supply_name__icontains=search).order_by('supply_name')

    # Filtrar los productos con bajo stock
    low_stock_products = []
    for p in p_list_array:
        if p.supply_total < 5:  # Ajusta este valor según tu criterio para "bajo stock"
            low_stock_products.append({
                'id': p.id,
                'supply_name': p.supply_name,
                'supply_code': p.supply_code,
                'supply_unit': p.supply_unit,
                'supply_initial_stock': p.supply_initial_stock,
                'supply_input': p.supply_input,
                'supply_output': p.supply_output,
                'supply_total': p.supply_total,
                'low_stock': True,
            })
            

    paginator = Paginator(low_stock_products, 10)  # Ajusta el número de elementos por página según sea necesario
    p_list_paginate = paginator.get_page(page)

    template_name = 'inventario/inventario_main.html'
    return render(request, template_name, {
        'template_name': template_name,
        'p_list_paginate': p_list_paginate,
        'paginator': paginator,
        'page': page
    })

@login_required
def crear_producto(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    #category_list = Category.objects.all().order_by('category_name')
    template_name = 'inventario/crear_producto.html'
    return render(request,template_name,{'profile':profile})#,'category_list':category_list})
#CREAR PRODUCTO TAL VEZ


@login_required
def producto_save(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')
    if request.method == 'POST':
        supply_name = request.POST.get('supply_name')
        supply_code = request.POST.get('supply_code')  
        supply_unit = request.POST.get('supply_unit')
        supply_initial_stock = request.POST.get('supply_initial_stock')
        supply_input = request.POST.get('supply_input')
        supply_output = request.POST.get('supply_output')
        
   
        #product_category_id = request.POST.get('category_name') 
        if supply_name == '' or supply_code == '' or supply_unit == '' or supply_input == ''or supply_output == '':
            messages.add_message(request, messages.INFO, 'Debes ingresar toda la información')
            return redirect('crear_producto')
        #category =Category.objects.get(id=product_category_id)
        producto_save = Product(
            supply_name=supply_name,
            supply_code=supply_code,
            supply_unit=supply_unit,
            supply_initial_stock=supply_initial_stock,
            supply_input=int("0"),
            supply_output=int("0"),
            supply_total=supply_initial_stock,
        )
        producto_save.save()
        messages.add_message(request, messages.INFO, 'Producto ingresado con éxito')
        return redirect('inventario_main')
    else:
        messages.add_message(request, messages.INFO, 'Error en el método de envío')
        return redirect('check_group_main')


   #VER PRODUCTO Y se usa pa editar
@login_required
def producto_ver(request, product_id):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    product_data = Product.objects.get(pk=product_id)
    #category_list = Category.objects.all()
    #selected_category = product_data.product_category
    template_name = 'inventario/producto_ver.html'
    return render(request, template_name, {'profile': profile, 'product_data': product_data}) #'category_list': category_list, 'selected_category': selected_category})



@login_required
def producto_list(request, page=None, search=None):
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
        p_count = Product.objects.filter(supply_name='a').count()
        p_list_array = Product.objects.all().order_by('supply_name')
    else:
        p_count = Product.objects.filter(supply_name='a').filter(supply_name__icontains=search).count()
        p_list_array = Product.objects.all().filter(supply_name__icontains=search).order_by('supply_name')

    p_list = []
    for p in p_list_array:
        p_list.append({
            'id': p.id,
            'supply_name': p.supply_name,
            'supply_code': p.supply_code,
            'supply_unit': p.supply_unit,
            'supply_initial_stock': p.supply_initial_stock,
            'supply_input': p.supply_input,
            'supply_output': p.supply_output,
            'supply_total': p.supply_total,
            #'category_name': p.product_category.category_name, # aquí se obtiene el category_name asociado al producto
        })

    paginator = Paginator(p_list, 1)
    p_list_paginate = paginator.get_page(page)

    template_name = 'inventario/producto_list.html'
    return render(request, template_name, {'template_name': template_name, 'p_list_paginate': p_list_paginate, 'paginator': paginator, 'page': page})


@login_required
def producto_edit(request, product_id):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':

        supply_name = request.POST.get('supply_name')
        supply_code = request.POST.get('supply_code')
        supply_unit = request.POST.get('supply_unit')
        supply_initial_stock = request.POST.get('supply_initial_stock')
        supply_input = request.POST.get('supply_input')
        supply_output = request.POST.get('supply_output')
        
        
        product.supply_name = supply_name
        product.supply_code = supply_code
        product.supply_unit = supply_unit
        product.supply_initial_stock = supply_initial_stock
        product.supply_input = supply_input
        product.supply_output = supply_output
        if supply_input=="0" and supply_output=="0":
            product.supply_total = supply_initial_stock
        else:
            if supply_input=="0":
                product.supply_total= (int(supply_initial_stock))-(int(supply_output))
            else:
                if supply_output=="0":
                    product.supply_total= (int(supply_initial_stock))+(int(supply_input))
                else:
                    product.supply_total= (int(supply_initial_stock))+(int(supply_input))-(int(supply_output))

        product.save()
        messages.success(request, 'Producto editado correctamente')
        
        return redirect('producto_ver', product_id=product.id)
    else:
        product_data = Product.objects.get(pk=product_id)
        #categories = Category.objects.all()
        
        template_name= 'inventario/producto_ver.html'
        
        return render(request, template_name, {'product_data': product_data})#, 'categories': categories})

    
#ELIMINAR PRODUCTO
def producto_delete(request, product_id):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Producto eliminado correctamente')
    return redirect(reverse('producto_list'))


#CARGA MASIVA   
@login_required
def carga_masiva_producto(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'inventario/carga_masiva_producto.html'
    return render(request, template_name, {'profiles': profile})

@login_required
def import_file_producto(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="archivo_importacion_productos.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = 'carga_masiva'

    columns = ['supply_name', 'supply_code', 'supply_unit', 'supply_stock_initial']
    ws.append(columns)

    example_data = ['ej: Nombre producto', 'SK1111', 'Kg', 10]
    ws.append(example_data)

    wb.save(response)
    return response  

@login_required
def carga_masiva_producto_save(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        try:
            data = pd.read_excel(request.FILES['myfile'], engine='openpyxl',skiprows=1)
            df = pd.DataFrame(data)
            acc = 0
            for item in df.itertuples():
                supply_name = str(item[1])
                supply_code = str(item[2])
                supply_unit = str(item[3])
                supply_initial_stock = int(item[4])

                #Valida que supply_name solo sean letras
                if not supply_name.replace('','').isalpha():
                    raise ValueError('El nombre del insumo solo puede contener letras')
                
                #Valida que supply_unit solo sean las opciones kg o LATA (330 ml)
                if supply_unit not in ['kg','LATA (330 ml)']:
                    raise ValueError('La unidad del suministro solo puede ser "kg" o "LATA (330 ml)"')
                
                #Valida que supply_initial_stock solo sean numeros
                if not isinstance(supply_initial_stock, int):
                    raise ValueError('El stock inicial debe ser un valor numérico')
             
                producto_save = Product(
                    supply_name=supply_name,
                    supply_code=supply_code,
                    supply_unit=supply_unit,
                    supply_initial_stock=supply_initial_stock,
                  
                )
                producto_save.save()
                acc += 1

            messages.add_message(request, messages.INFO, 'Carga masiva finalizada, se importaron ' + str(acc) + ' registros')
            return redirect('carga_masiva_producto')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Error al procesar el archivo: {str(e)}')
            return redirect('carga_masiva_producto')
    
@login_required
def descarga_reporte_producto(request):
    try:    
        profiles = Profile.objects.get(user_id = request.user.id)
        if profiles.group_id != 1:
         messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
         return redirect('check_group_main')
    
        style_2 = xlwt.easyxf('font: name Time New Roman, color-index black; font: bold on')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        response=HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="ListaProductos.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Productos')

        row_num = 0
        columns = ['Nombre', 'Precio', 'Estado','Categoria']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num] ,font_style)

        productos = Product.objects.all().order_by('supply_name')

        for row in productos:
            row_num += 1
            for col_num in range(4):
                if col_num == 0:
                    ws.write(row_num, col_num, row.supply_name, style_2)
                if col_num == 1:
                    ws.write(row_num, col_num, row.supply_code, style_2)   
                if col_num == 2:
                    ws.write(row_num, col_num, row.supply_unit, style_2)
             #  if col_num == 3:
            #       ws.write(row_num, col_num, str(row.product_category), style_2)

        
        wb.save(response)
        return response
    except Exception:
            traceback.print_exc()
            messages.add_message(request, messages.ERROR, 'Se produjo un error al generar el archivo Excel. Por favor, inténtelo de nuevo más tarde.')
            return redirect('producto_list')

@login_required
def reportes_main_productos(request):
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
        if profiles.group_id != 1:
            messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
            return redirect('check_group_main')
        
        template_name = 'inventario/reportes_main_productos.html'
        return render(request,template_name)
    except:
        messages.add_message(request, messages.INFO, 'Error al acceder al pagina de reportes')
        return redirect('producto_list')


@login_required
def reporte_producto_filtro(request):
    try:
        profiles = Profile.objects.get(user_id=request.user.id)
        if profiles.group_id != 1:
            messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
            return redirect('check_group_main')

        if request.method == 'POST':
            producto = request.POST.get('supply_name')
            if len(producto) == 0:
                messages.add_message(request, messages.INFO, 'El producto no puede estar vacío')
                return redirect('reportes_main_productos')
            producto_count = Product.objects.filter(estado='Activo').filter(supply_name__icontains=producto).count()
            if producto_count < 1:
                messages.add_message(request, messages.INFO, 'No existe producto con la cadena buscada')
                return redirect('reportes_main')

            style_1 = xlwt.easyxf('font: name Times New Roman, color-index black, bold on', num_format_str='#,##0.00')
            style_2 = xlwt.easyxf('font: name Times New Roman, color-index black, bold on')
            

            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="ReporteProductos.xls"'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Productos')

            row_num = 0
            columns = ['Nombre', 'Precio', 'Estado'] #le borre categoria
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], style_2)

            productos_array = Product.objects.filter(estado='Activo').filter(supply_name__icontains=producto)
            for row in productos_array:
                row_num += 1
                for col_num in range(4):
                    if col_num == 0:
                        ws.write(row_num, col_num, row.supply_name, style_2)
                    if col_num == 1:
                        ws.write(row_num, col_num, row.supply_code, style_2)
                    if col_num == 2:
                        ws.write(row_num, col_num, row.supply_unit, style_2)
                    #if col_num == 3:
                    #   ws.write(row_num, col_num, str(row.product_category), style_2)

            wb.save(response)
            return response
        else:
            messages.add_message(request, messages.INFO, 'Error')
            return redirect('check_group_main')
    except:
        messages.add_message(request, messages.INFO, 'Error al generar el reporte')
        return redirect('reportes_main_productos')
"""
    ########################## email #######################################
@login_required
def correo1(request):
    #llamos al metodo que envia el correo
    send_mail_ejemplo2(request,'correo.mypyme@gmail.com','')
    messages.add_message(request, messages.INFO, 'correo enviado')
    return redirect('inventario_main')   
@login_required
def send_mail_ejemplo2(request,mail_to,data_1):
    #Ejemplo que permite enviar un correo agregando un excel creado con info de la bd


    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#directorio base del proyecto en el servidor
    BASE_PATH = os.path.join(BASE_DIR,"core","static","core")#lugar donde se guarda el archivo
    file_name = "Estado_Ventas.xls"#trate de que no se muy largo
    file_send = BASE_PATH+"/"+file_name
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('diosito salvame')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True   
    columns = ['Nombre','Precio','estado','categoria']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
        style_2 = xlwt.easyxf('font: name Times New Roman, color-index black, bold on')
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'dd/MM/yyyy'
    time_format = xlwt.XFStyle()
    time_format.num_format_str = 'hh:mm:ss'   
    #insumos = Insumos.objects.all().order_by('insumos_name')
    
    for row in insumos:
        row_num += 1
        for col_num in range(4):
            if col_num == 0:
                ws.write(row_num, col_num, row.insumos_name, style_2)
            if col_num == 1:
                ws.write(row_num, col_num, row.insumos_price, style_2)   
            if col_num == 2:
                ws.write(row_num, col_num, row.insumos_state, style_2)
            if col_num == 3:
                ws.write(row_num, col_num, str(row.insumos_categorys), style_2)                                         
    wb.save(file_send)  
    #fin archivo
    from_email = settings.DEFAULT_FROM_EMAIL #exporta desde el settings.py, el correo de envio por defecto
    subject = "Ventas Mypyme"    
    HTRML
    msg = EmailMultiAlternatives(subject, html_content, from_email, [mail_to])
    msg.content_subtype = "html"
    msg.attach_alternative(html_content, "text/html")

    msg = EmailMultiAlternatives(subject, html_content, from_email, [mail_to])
    msg.content_subtype = "html"
    archivo_adjunto = open(file_send,'rb')
    # Creamos un objeto MIME base
    adjunto_MIME = MIMEBase('application', 'octet-stream')
    # Y le cargamos el archivo adjunto
    adjunto_MIME.set_payload((archivo_adjunto).read())
    # Codificamos el objeto en BASE64
    encoders.encode_base64(adjunto_MIME)
    # Agregamos una cabecera al objeto    
    adjunto_MIME.add_header('Content-Disposition',"attachment; filename= %s" % file_name)
    # Y finalmente lo agregamos al mensaje
    msg.attach(adjunto_MIME)


    msg.send()


"""