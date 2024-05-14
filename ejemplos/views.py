import json
import pandas as pd
import xlwt

#ejemplo pdf
from io import BytesIO
from django.template.loader import get_template
#from xhtml2pdf import pisa
#ejemplo pdf

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from registration.models import Profile


from django.db.models import Count, Avg, Q
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import (api_view, authentication_classes, permission_classes)
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from ejemplos.models import *

from django.conf import settings #importamos el archivo settings, para usar constantes declaradas en él
from django.core.mail import EmailMultiAlternatives #libreria para el envio de correos

@login_required
def ejemplos_main(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'ejemplos/ejemplos_main.html'
    return render(request,template_name,{'template_name':template_name,'profile':profile})

@login_required
def ejemplos_habilidad_add(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'ejemplos/ejemplos_add.html'
    return render(request,template_name,{'template_name':template_name,'profile':profile})

@login_required
def ejemplos_habilidad_save(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        nivel = request.POST.get('nivel')        
        if nombre == '' or nivel == '':
            messages.add_message(request, messages.INFO, 'Debes ingresar toda la información')
            return redirect('ejemplos_habilidad_add')
        habilidad_save = Habilidad(
            nombre = nombre,
            nivel = nivel,
            )
        habilidad_save.save()
        messages.add_message(request, messages.INFO, 'Habilidad ingresada con éxito')
        return redirect('ejemplos_list_habilidades')
    else:
        messages.add_message(request, messages.INFO, 'Error en el método de envío')
        return redirect('check_group_main')
@login_required
def ejemplos_habilidad_ver(request,habilidad_id):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    habildad_data = Habilidad.objects.get(pk=habilidad_id)
    template_name = 'ejemplos/ejemplos_habilidad_ver.html'
    return render(request,template_name,{'template_name':template_name,'profile':profile,'habildad_data':habildad_data})

@login_required
def ejemplos_list_habilidades(request,page=None,search=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    if page == None:
        page = request.GET.get('page')
    else:
        page = page
    if request.GET.get('page') == None:
        page = page
    else:
        page = request.GET.get('page') 
    #logica que permite recibir la cadena de búsqueda y propoga a través del paginador
    if search == None:
        search = request.GET.get('search')
    else:
        search = search
    if request.GET.get('search') == None:
        search = search
    else:
        search = request.GET.get('search') 
    if request.method == 'POST':
        search = request.POST.get('search') 
        page = None
    #fin logica que permite recibir la cadena de búsqueda y propoga a través del paginador
    h_list = [] #lista vacia para agrega la salida de la lista ya sea con la cadena de búsqueda o no
    if search == None or search == "None":# si la cadena de búsqueda viene vacia
        h_count = Habilidad.objects.filter(estado='Activo').count()
        h_list_array = Habilidad.objects.filter(estado='Activo').order_by('nivel')
        for h in h_list_array:
            h_list.append({'id':h.id,'nombre':h.nombre,'nivel':h.nivel})
    else:#si la cadena de búsqueda trae datos
        h_count = Habilidad.objects.filter(estado='Activo').filter(nombre__icontains=search).count()
        h_list_array = Habilidad.objects.filter(estado='Activo').filter(nombre__icontains=search).order_by('nombre')
        for h in h_list_array:
            h_list.append({'id':h.id,'nombre':h.nombre,'nivel':h.nivel})            
    paginator = Paginator(h_list, 10) 
    h_list_paginate= paginator.get_page(page)   
    template_name = 'ejemplos/ejemplos_list_habilidades.html'
    return render(request,template_name,{'template_name':template_name,'h_list_paginate':h_list_paginate,'paginator':paginator,'page':page})

#CARGA MASIVA
@login_required
def ejemplos_carga_masiva(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'ejemplos/ejemplos_carga_masiva.html'
    return render(request,template_name,{'template_name':template_name,'profiles':profiles})

@login_required
def import_file(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="archivo_importacion.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('carga_masiva')
    row_num = 0
    columns = ['Nombre Habilidad','Nivel']
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'dd/MM/yyyy'
    for row in range(1):
        row_num += 1
        for col_num in range(2):
            if col_num == 0:
                ws.write(row_num, col_num, 'ej: habilidad' , font_style)
            if col_num == 1:                           
                ws.write(row_num, col_num, '88' , font_style)
    wb.save(response)
    return response  

@login_required
def ejemplos_carga_masiva_save(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        print(request.FILES['myfile'])
        data = pd.read_excel(request.FILES['myfile'])
        df = pd.DataFrame(data)
        acc = 0
        for item in df.itertuples():
            #capturamos los datos desde excel
            nombre = str(item[1])            
            nivel = int(item[2])
            habilida_save = Habilidad(
                nombre = nombre,            
                nivel = nivel,
                )
            habilida_save.save()
        messages.add_message(request, messages.INFO, 'Carga masiva finalizada, se importaron '+str(acc)+' registros')
        return redirect('ejemplos_carga_masiva')    
#ejemplo reportes
@login_required
def reporte_todas_habilidades(request):
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
        if profiles.group_id != 1:
            messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
            return redirect('check_group_main')

        #establece los estilos de las celdas
        style_1 = xlwt.easyxf('font: name Times New Roman, color-index black, bold on',num_format_str='#,##0.00')
        style_2 = xlwt.easyxf('font: name Times New Roman, color-index black, bold on')
        style_date = xlwt.easyxf(num_format_str='dd/MM/YYYY')
        #fin establece los estilos de las celdas

        #establece las cabeceras para generar el reporte
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="ReporteHabilidades.xls"'#nombre del archivo
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Habilidades')#nombre de la hoja, genera la hoja
        #fin establece las cabeceras para generar el reporte

        #encabezados del reporte
        row_num = 0 #fija la primera fila
        columns = ['Nombre','Nivel','Creado']#nombre columnas del archivo
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style_2)#agrega las columnas a la primera fila
        #encabezados del reporte
        habilidades_array = Habilidad.objects.all().order_by('nombre') #consulta que trae la data a mostrar

        for row in habilidades_array: #recooremos el resultado de la consulta anterior
            row_num += 1 # avanzamos a la fila siguiente
            for col_num in range(3): #recorremos las columnas del reporte
                if col_num == 0:
                    ws.write(row_num, col_num, row.nombre, style_2)
                if col_num == 1:                           
                    ws.write(row_num, col_num, row.nivel, style_2)
                if col_num == 2:
                    ws.write(row_num, col_num, row.created.date(), style_date)#el date convierte el formato original a dd-mm-yyyy
        wb.save(response)#genera el libro excel
        return response #permite la descarga del informe
    except:
        messages.add_message(request, messages.INFO, 'Error al generar el reporte')
        return redirect('ejemplos_list_habilidades')   
@login_required
def reportes_main(request):
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
        if profiles.group_id != 1:
            messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
            return redirect('check_group_main')
        template_name = 'ejemplos/reportes_main.html'
        return render(request,template_name)
    except:
        messages.add_message(request, messages.INFO, 'Error al acceder al pagina de reportes')
        return redirect('ejemplos_list_habilidades')

@login_required
def reporte_habilidades_nombre(request):
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
        if profiles.group_id != 1:
            messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
            return redirect('check_group_main')

        #capturamos el metodo de envio
        if request.method == 'POST':
            habilidad = request.POST.get('habilidad')#captura la habilidad 
            #revisamos si la cadena viene vacia
            if len(habilidad) == 0:
                messages.add_message(request, messages.INFO, 'La habilidad no puede estar vacia')
                return redirect('reportes_main') 
            #fin revisamos si la cadena viene vacia
            #revisamos si la cadena pasada existe completa o parcial
            #icontains no distingue entre mayúsculas y minúsculas. 
            #contains distingue entre mayúsculas y minúsculas. 
            habilidad_count = Habilidad.objects.filter(estado='Activo').filter(nombre__icontains=habilidad).count()
            if habilidad_count < 1:
                messages.add_message(request, messages.INFO, 'No existe habilidades con la cadena buscada')
                return redirect('reportes_main')            
            #fin revisamos si la cadena pasada existe completa o parcial
            
            #establece los estilos de las celdas
            style_1 = xlwt.easyxf('font: name Times New Roman, color-index black, bold on',num_format_str='#,##0.00')
            style_2 = xlwt.easyxf('font: name Times New Roman, color-index black, bold on')
            style_date = xlwt.easyxf(num_format_str='dd/MM/YYYY')
            #fin establece los estilos de las celdas

            #establece las cabeceras para generar el reporte
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="ReporteHabilidades.xls"'#nombre del archivo
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Habilidades')#nombre de la hoja, genera la hoja
            #fin establece las cabeceras para generar el reporte

            #encabezados del reporte
            row_num = 0 #fija la primera fila
            columns = ['Nombre','Nivel','Creado']#nombre columnas del archivo
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], style_2)#agrega las columnas a la primera fila
            #encabezados del reporte
            
            habilidades_array = Habilidad.objects.filter(estado='Activo').filter(nombre__icontains=habilidad) #consulta que trae la data a mostrar

            for row in habilidades_array: #recooremos el resultado de la consulta anterior
                row_num += 1 # avanzamos a la fila siguiente
                for col_num in range(3): #recorremos las columnas del reporte
                    if col_num == 0:
                        ws.write(row_num, col_num, row.nombre, style_2)
                    if col_num == 1:                           
                        ws.write(row_num, col_num, row.nivel, style_2)
                    if col_num == 2:
                        ws.write(row_num, col_num, row.created.date(), style_date)#el date convierte el formato original a dd-mm-yyyy
            wb.save(response)#genera el libro excel
            return response #permite la descarga del informe
        else:
            messages.add_message(request, messages.INFO, 'Error')
            return redirect('check_group_main')   
    except:
        messages.add_message(request, messages.INFO, 'Error al generar el reporte')
        return redirect('ejemplos_list_habilidades')   
#fin ejemplo reportes

#ejemplos muchos a muchos
@login_required
def ejemplos_autor_list(request):
    autor_list = Autor.objects.all()
    template_name = 'ejemplos/ejemplos_autor_list.html'
    return render(request,template_name,{'autor_list':autor_list})

@login_required
def ejemplos_autor_new(request):
    template_name = 'ejemplos/ejemplos_autor_new.html'
    return render(request,template_name)

@login_required
def ejemplos_autor_save(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        autor_save = Autor(
            nombre = nombre,
            )
        autor_save.save()
        messages.add_message(request, messages.INFO, 'autor creado')   
        return redirect('ejemplos_autor_list')
    else:
        messages.add_message(request, messages.INFO, 'Error al crear el autor')   
        return redirect('ejemplos_autor_new')

@login_required
def ejemplos_proyect_list(request):
    proyect_list = Proyecto.objects.all()
    template_name = 'ejemplos/ejemplos_proyect_list.html'
    return render(request,template_name,{'proyect_list':proyect_list})

@login_required
def ejemplos_proyect_new(request):
    autor_list = Autor.objects.all()
    template_name = 'ejemplos/ejemplos_proyect_new.html'
    return render(request,template_name,{'autor_list':autor_list})

@login_required
def ejemplos_proyect_save(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        palabras_clave = request.POST.get('palabras_clave')
        autores = request.POST.getlist('autor')
        proyect_save = Proyecto(
            nombre = nombre,
            palabras_clave = palabras_clave
            )
        proyect_save.save()

        if autores: 
            for a in autores:
                proyect_save.autor.add(a) #guarda muchos a mucho
        messages.add_message(request, messages.INFO, 'proyecto creado')   
        return redirect('ejemplos_proyect_list')
    else:
        messages.add_message(request, messages.INFO, 'Error al crear el proyecto')   
        return redirect('ejemplos_proyect_list')

@login_required
def ejemplos_proyect_edit(request,proyecto_id):
    proyect_data = Proyecto.objects.get(pk=proyecto_id)
    autor_data = Autor.objects.filter(proyecto__id = proyect_data.id)
    autor_data_list = []
    for a in autor_data:
        autor_data_list.append(a.id)
    autor_list = Autor.objects.all()

    template_name = 'ejemplos/ejemplos_proyect_edit.html'
    return render(request,template_name,{'proyect_data':proyect_data,'autor_data_list':autor_data_list,'autor_list':autor_list})

@login_required
def ejemplos_proyect_edit_save(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        palabras_clave = request.POST.get('palabras_clave')
        autores = request.POST.getlist('autor')
        premio = request.POST.getlist('premio')
        Proyecto.objects.filter(pk=id).update(nombre = nombre)
        Proyecto.objects.filter(pk=id).update(palabras_clave = palabras_clave)
        
        proyecto = Proyecto.objects.get(pk=id)#carga el proyecto que usaremos para muchos a muchos
        #actualizmos autores
        autor_data = Autor.objects.filter(proyecto__id = id)
        for a in autor_data:
            proyecto.autor.remove(a) #elimina muchos a mucho
        if autores: 
            for a in autores:
                proyecto.autor.add(a) #guarda muchos a mucho        
        messages.add_message(request, messages.INFO, 'proyecto creado')   
        return redirect('ejemplos_proyect_list')
    else:
        messages.add_message(request, messages.INFO, 'Error al crear el proyecto')   
        return redirect('ejemplos_proyect_list')

#fin ejemplos muchos a muchos

#ejemplos correos
@login_required
def ejemplos_correo1(request):
    #llamos al metodo que envia el correo
    send_mail_ejemplo1(request,'rene@softiago.cl','dato por parametro ejemplo')
    messages.add_message(request, messages.INFO, 'correo enviado')
    return redirect('ejemplos_main')   

@login_required
def send_mail_ejemplo1(request,mail_to,data_1):
    #Ejemplo que permite enviar un correo solo con texto, el metodo, recibe por parametro la información para su ejecución    
    from_email = settings.DEFAULT_FROM_EMAIL #exporta desde el settings.py, el correo de envio por defecto
    subject = "Asunto del correo"    
    html_content = """
                    <html>
                        <head>
                            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                        </head>
                        <body>
                            <h3>Estimad@</h3>
                            <p>Es es el cuerpo que agrega el dato por parametro """+str(data_1)+""" mas texto .</p>
                            <p>otro párrafo</p>
                            <br/>
                            <p>Le saluda</p>
                            <p>Equipo de soluciones pyme.</p>
                            <br/>
                            <p><small>Correo generado automáticamente, por favor no responder.<small></p>
                        </body>
                    </html>            
                """
    msg = EmailMultiAlternatives(subject, html_content, from_email, [mail_to])
    msg.content_subtype = "html"
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@login_required
def ejemplos_correo2(request):
    #llamos al metodo que envia el correo
    send_mail_ejemplo2(request,'rene@softiago.cl','Ejemplo 2 con archivo')
    messages.add_message(request, messages.INFO, 'correo enviado')
    return redirect('ejemplos_main')   

@login_required
def send_mail_ejemplo2(request,mail_to,data_1):
    #Ejemplo que permite enviar un correo agregando un excel creado con info de la bd

    #archivo
    import os #debe ubicarlo en el inicio del archivo
    from email.mime.multipart import MIMEMultipart #debe ubicarlo en el inicio del archivo
    from email.mime.text import MIMEText #debe ubicarlo en el inicio del archivo
    from email.mime.base import MIMEBase #debe ubicarlo en el inicio del archivo
    from email import encoders #debe ubicarlo en el inicio del archivo

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#directorio base del proyecto en el servidor
    BASE_PATH = os.path.join(BASE_DIR,"core","static","core")#lugar donde se guarda el archivo
    file_name = "nombre_archivo.xls"#trate de que no se muy largo
    file_send = BASE_PATH+"/"+file_name
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Agenda')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True   
    columns = ['Habilidad','Tipo']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'dd/MM/yyyy'
    time_format = xlwt.XFStyle()
    time_format.num_format_str = 'hh:mm:ss'   
    rows = Habilidad.objects.all().order_by('nombre')         
    for row in rows:
        row_num += 1
        for col_num in range(len(columns)):
            if col_num == 0:
                ws.write(row_num, col_num, row.nombre, date_format)
            if col_num == 1:
                ws.write(row_num, col_num, row.nivel, font_style)                                               
    wb.save(file_send)  
    #fin archivo
    from_email = settings.DEFAULT_FROM_EMAIL #exporta desde el settings.py, el correo de envio por defecto
    subject = "Asunto del correo"    
    html_content = """
                    <html>
                        <head>
                            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                        </head>
                        <body>
                            <h3>Estimad@</h3>
                            <p>Es es el cuerpo que agrega el dato por parametro """+str(data_1)+""" mas texto .</p>
                            <p><small>Correo generado automáticamente, por favor no responder.<small></p>
                        </body>
                    </html>            
                """
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

#fin ejemplos correos

#ejemplo pdf
#este método nos permitirá crear pdf, como ven solo recive dos argumentos: 
#1- el HTML que renderizaremos 
#2- el diccionario donde pasaremos la información dinamica que deseamos mostrar 
'''
def crea_pdf(template_name,dic={}):
    template = get_template(template_name)#el metodo get_template, no permite cargar el html
    html = template.render(dic)#template rebder nos permite renderizar el html
    result = BytesIO() #permite almacenar en el buffer, el contenido como binarios
    pdf = pisa.pisaDocument(BytesIO(html.encode('ISO-8859-1')),result)
    return HttpResponse(result.getvalue(),content_type='application/pdf')
'''
@login_required
def lista_habilidades_pdf(request):
    habilidades = Habilidad.objects.all()
    diccionario = {
        'habilidades':habilidades
        }
    pdf = crea_pdf('ejemplos/ejemplos_list_habilidades_pdf.html',diccionario) 
    return HttpResponse(pdf,content_type='application/pdf')

#fin ejemplo pdf
#ejemplo dashboard
@login_required
def ejemplos_dashboard(request):
    #datos tarjeta 1
    habilidades_count = Habilidad.objects.all().count()
    #fin datos tarjeta 1
    #datos tarjeta 2
    heroes_count = Heroe.objects.all().count()
    #fin datos tarjeta 2
    #datos tarjeta 3
    rate_heroes_habilidad = heroes_count / habilidades_count
    #fin datos tarjeta 3
    #datos grafico 1
    #este gráfico nos trae la información de 3 niveles estáticos
    habilidades_total = habilidades_count
    habilidades_nivel1_count = Habilidad.objects.filter(nivel=1).count()
    habilidades_nivel2_count = Habilidad.objects.filter(nivel=2).count()
    habilidades_nivel3_count = Habilidad.objects.filter(nivel=3).count()
    suma_habilidades = habilidades_nivel1_count + habilidades_nivel2_count + habilidades_nivel3_count
    data_rate = round(float((suma_habilidades/habilidades_total)*100),1)
    data_set = [habilidades_nivel1_count,habilidades_nivel2_count,habilidades_nivel3_count]
    data_label = ['Nivel 1','Nivel 2','Nivel 3']
    data_color = ['#338AFF','#FA1A3C','#28B463']
    #fin datos grafico 1    
    #datos grafico 2    
    #este gráfico nos trae la información de todos los niveles
    habilidades_list = Habilidad.objects.all()#carga una array con todas las habilidades
    data_set_todos_niveles = []
    data_label_todos_niveles = []
    data_label_todos_niveles.append('Total')#agregamos estaticamente la etiqueta total para el gráfico
    data_set_todos_niveles.append(habilidades_total)#agregamos el total para que aparezca en el gráfico
    for i in habilidades_list:
        data_label_todos_niveles.append('Nivel'+str(i.nivel))
        data_set_todos_niveles.append(i.nivel) 
    #fin datos grafico 2  
    template_name = 'ejemplos/ejemplos_dashboard.html'
    return render(request,template_name,{'habilidades_count':habilidades_count,'heroes_count':heroes_count,'rate_heroes_habilidad':rate_heroes_habilidad,'data_rate':data_rate,'data_set':data_set,'data_label':data_label,'data_color':data_color,'data_set_todos_niveles':data_set_todos_niveles,'data_label_todos_niveles':data_label_todos_niveles})
#fin ejemplo dashboard

#ENDPOINT
#categorias
@api_view(['GET'])
def category_list_rest(request, format=None):
    if request.method == 'GET':
        category_list = Category.objects.all().order_by('category_name')
        category_json = []
        for h in category_list:
            category_json.append({
                'category_id':h.id,
                'category_name': h.category_name,
                'category_state': h.category_state,
                })
        return Response({'Listado Categorias':category_json})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def category_edit_rest(request, format=None):
    if request.method == 'POST':
        category_id = request.data['category_id']
        category_name = request.data['category_name']
        category_state = request.data['category_state']

        Category.objects.filter(pk=category_id).update(category_name=category_name)
        Category.objects.filter(pk=category_id).update(category_state=category_state)

        return Response({'MSJ':'Categoria editada'})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def category_add_rest(request, format=None):
    if request.method == 'POST':
        category_name = request.data['category_name']

        category_save = Category(
            category_name=category_name,
        )
        category_save.save()
        return Response({'MSJ':'Categoria creada'})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def category_del_rest(request, format=None):
    if request.method == 'POST':
        category_id = request.data['category_id']
        Category.objects.filter(pk=category_id).delete()
        return Response({'MSJ':'Categoria eliminado'})
    else:
        return Response({'Msj':"Error método no soportado"})


#Listar Proveedores Activos
@api_view(['GET'])
def provider_list_rest(request, format=None):
    if request.method == 'GET':
        provider_list = Provider.objects.all().order_by('provider_name')
        provider_json = []
        for h in provider_list:
            provider_json.append({
                'providerid':h.id,
                'provider_name':h.provider_name,
                'provider_last_name': h.provider_last_name,
                'provider_mail': h.provider_mail,
                'provider_state': h.provider_state,
                })
        return Response({'Proveedores Listado':provider_json})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def provider_edit_rest(request, format=None):
    if request.method == 'POST':
        provider_id = request.data['provider_id']
        provider_name = request.data['provider_name']
        provider_last_name = request.data['provider_last_name']
        provider_mail = request.data['provider_mail']
        provider_state = request.data['provider_state']

        Provider.objects.filter(pk=provider_id).update(provider_name=provider_name)
        Provider.objects.filter(pk=provider_id).update(provider_last_name=provider_last_name)
        Provider.objects.filter(pk=provider_id).update(provider_mail=provider_mail)
        Provider.objects.filter(pk=provider_id).update(provider_state=provider_state)

        return Response({'MSJ':'Proveedor editado'})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def provider_add_rest(request, format=None):
    if request.method == 'POST':
        provider_name = request.data['provider_name']
        provider_last_name = request.data['provider_last_name']
        provider_mail = request.data['provider_mail']

        provider_save = Provider(
            provider_name=provider_name,
            provider_last_name=provider_last_name,
            provider_mail=provider_mail,
        )
        provider_save.save()
        return Response({'MSJ':'Proveedor creado'})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def provider_del_rest(request, format=None):
    if request.method == 'POST':
        provider_id = request.data['provider_id']
        Provider.objects.filter(pk=provider_id).delete()
        return Response({'MSJ':'Proveedor eliminado'})
    else:
        return Response({'Msj':"Error método no soportado"})
#prodcutos
@api_view(['GET'])
def product_list_rest(request, format=None):
    if request.method == 'GET':
        product_list = Product.objects.all().order_by('product_name')
        product_json = []
        for h in product_list:
            product_json.append({
                'product_id':h.id,
                'product_name':h.product_name,
                'product_price': h.product_price,
                'product_image': h.product_image,
                'product_total': h.product_total,
                })
        return Response({'Listado':product_json})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def product_edit_rest(request, format=None):
    if request.method == 'POST':
        product_id = request.data['product_id']
        product_name = request.data['product_name']
        product_price = request.data['product_price']
        product_image = request.data['product_image']
        product_total = request.data['product_total']

        Product.objects.filter(pk=product_id).update(product_name=product_name)
        Product.objects.filter(pk=product_id).update(product_price=product_price)
        Product.objects.filter(pk=product_id).update(product_image=product_image)
        Product.objects.filter(pk=product_id).update(product_total=product_total)

        return Response({'MSJ':'editado'})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def product_add_rest(request, format=None):
    if request.method == 'POST':
        product_name = request.data['product_name']
        product_price = request.data['product_price']
        product_image = request.data['product_image']

        product_save = Product(
            product_name=product_name,
            product_price=product_price,
            product_image=product_image,
            product_total=product_price-product_image,
        )
        product_save.save()
        return Response({'MSJ':'creado'})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def product_del_rest(request, format=None):
    if request.method == 'POST':
        product_id = request.data['product_id']
        Product.objects.filter(pk=product_id).delete()
        return Response({'MSJ':'eliminado'})
    else:
        return Response({'Msj':"Error método no soportado"})

@api_view(['POST'])
def ejemplos_habilidad_add_rest(request, format=None):    
    if request.method == 'POST':
        nombre = request.data['nombre'] 
        nivel = request.data['nivel'] 
        if nombre == '' or nivel == '':
            return Response({'Msj': "Error los datos no pueder estar en blanco"})                         
        habilidad_save = Habilidad(
            nombre = nombre,
            nivel = nivel,
            )
        habilidad_save.save()
        return Response({'Msj': "Habilidad creada"})
    else:
        return Response({'Msj': "Error método no soportado"})

@api_view(['GET'])
def ejemplos_habilidad_list_rest(request, format=None):    
    if request.method == 'GET':
        habilidad_list =  Habilidad.objects.all().order_by('nombre')
        habilidad_json = []
        for h in habilidad_list:
            habilidad_json.append({'habilidad':h.nombre,'nivel':h.nivel,'estado':h.estado})
        return Response({'Listado': habilidad_json})
    else:
        return Response({'Msj': "Error método no soportado"})

@api_view(['POST'])
def ejemplos_habilidad_get_element_rest(request, format=None):    
    if request.method == 'POST':
        habilidad_json = []
        habilidad_id = request.data['habilidad_id']
        habilidad_array =  Habilidad.objects.get(pk=habilidad_id)
        habilidad_json.append(
            {'id':habilidad_array.id,
             'nombre':habilidad_array.nombre,
             'nivel':habilidad_array.nivel,
             'estado':habilidad_array.estado})
        return Response({habilidad_array.nombre:habilidad_json})
    else:
        return Response({'Msj': "Error método no soportado"})

@api_view(['POST'])
def ejemplos_habilidad_update_element_rest(request, format=None):    
    if request.method == 'POST':
        habilidad_id = request.data['habilidad_id']
        nombre = request.data['nombre']
        nivel = request.data['nivel']
        estado = request.data['estado']
        Habilidad.objects.filter(pk=habilidad_id).update(nombre=nombre)
        Habilidad.objects.filter(pk=habilidad_id).update(nivel=nivel)
        Habilidad.objects.filter(pk=habilidad_id).update(estado=estado)
        return Response({'Msj':'Habilidad editada con éxito'})
    else:
        return Response({'Msj': 'Error método no soportado'})

@api_view(['POST'])
def ejemplos_habilidad_del_element_rest(request, format=None):    
    if request.method == 'POST':
        habilidad_id = request.data['habilidad_id']
        Habilidad.objects.filter(pk=habilidad_id).delete()
        return Response({'Msj':'Habilidad eliminada con éxito'})
    else:
        return Response({'Msj': 'Error método no soportado'})

@api_view(['POST'])
def ejemplos_habilidad_list_date_rest(request, format=None):    
    if request.method == 'POST':
        created = request.data['created']
        habilidad_list_count = Habilidad.objects.filter(created=created).count()
        if habilidad_list_count > 0:
            habilidad_list =  Habilidad.objects.filter(created=created).order_by('nombre')
            habilidad_json = []
            for h in habilidad_list:
                habilidad_json.append({'habilidad':h.nombre,'nivel':h.nivel,'estado':h.estado})
            return Response({'Listado': habilidad_json})
        else:
            return Response({'Msj': 'No existen habilidades creadas el '+str(created)})
    else:
        return Response({'Msj': 'Error método no soportado'})

@api_view(['POST'])
def ejemplos_habilidad_list_range_date_rest(request, format=None):    
    if request.method == 'POST':
        initial = request.data['initial']
        final = request.data['final']
        habilidad_list_count = Habilidad.objects.filter(created__range=(initial,final)).count()
        if habilidad_list_count > 0:
            habilidad_list =  Habilidad.objects.filter(created__range=(initial,final)).order_by('nombre')
            habilidad_json = []
            for h in habilidad_list:
                habilidad_json.append({'habilidad':h.nombre,'nivel':h.nivel,'estado':h.estado})
            return Response({'Listado': habilidad_json})
        else:
            return Response({'Msj': 'No existen habilidades creadas entre el '+str(initial)+' al '+str(final)})
    else:
        return Response({'Msj': 'Error método no soportado'})


@api_view(['POST'])
def ejemplos_habilidad_list_contains(request, format=None):    
    if request.method == 'POST':
        search = request.data['search']
        habilidad_list_count = Habilidad.objects.filter(Q(nombre__icontains=search)|Q(estado__icontains=search)).count()
        if habilidad_list_count > 0:
            habilidad_list =  Habilidad.objects.filter(Q(nombre__icontains=search)|Q(estado__icontains=search)).order_by('nombre')
            habilidad_json = []
            for h in habilidad_list:
                habilidad_json.append({'habilidad':h.nombre,'nivel':h.nivel,'estado':h.estado})
            return Response({'Listado': habilidad_json})
        else:
            return Response({'Msj': 'No existen habilidades que concuerden en estado o nombre con la cadena '+str(search)})    
    else:
        return Response({'Msj': 'Error método no soportado'})