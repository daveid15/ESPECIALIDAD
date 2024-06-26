# Importaciones de Python estándar
import calendar
import json
import random
from datetime import datetime, time, timedelta
import re
from itertools import cycle
# Importaciones de Django
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.core.files.storage import FileSystemStorage
# Importaciones de tus aplicaciones locales
from registration.models import Profile
from django.contrib.auth.models import Group, User
from .models import Usuario
from inventario.models import Product

"""
    validar_numero Valida si el número proporcionado tiene exactamente 9 dígitos.
    Solo realiza la validación si la solicitud es de tipo POST.
"""
def validar_numero(numero,request):

    if request.method == 'POST':
        if re.fullmatch(r'\d{9}', numero):
            return True
        else:
            return False
"""
    validar_string Valida si la cadena contiene solo letras (mayúsculas y minúsculas),
    incluyendo caracteres como Ñ, ñ y vocales acentuadas.
    Solo realiza la validación si la solicitud es de tipo POST.
"""
def validar_string(cadena, request):
    if request.method == 'POST':
        if re.fullmatch(r'[A-Za-zÑñÁÉÍÓÚáéíóú]+', cadena):
            return True
        else:
            return False
"""
    validar_nombre Valida si la cadena contiene solo letras y espacios,
    permitiendo caracteres especiales como Ñ y vocales acentuadas.
    Solo realiza la validación si la solicitud es de tipo POST.
"""
def validar_nombre(cadena, request):
    if request.method == 'POST':
        if re.fullmatch(r'[A-Za-zÑñÁÉÍÓÚáéíóú\s]+', cadena):
            return True
        else:
            return False

"""
    validar_email Valida si el correo electrónico proporcionado tiene un formato válido.
    Utiliza una expresión regular y solo realiza la validación si la solicitud es de tipo POST.
"""       
def validar_email(email,request):
    if request.method == 'POST':
        # Expresión regular para validar un correo electrónico
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, email):
            return True
        else:
            return False
        
"""
    validar_rut Valida un RUT asegurando que esté en mayúsculas,
    sin guiones y con un dígito verificador correcto. Solo realiza la validación si la solicitud es de tipo POST.
"""
def validar_rut(rut,request):
    if request.method == 'POST':
        rut = rut.upper()
        rut = rut.replace("-", "")
        aux = rut[:-1]
        dv = rut[-1:]

        revertido = map(int, reversed(str(aux)))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(revertido, factors))
        res = (-s) % 11

        if str(res) == dv:
            return True
        elif dv == "K" and res == 10:
            return True
        else:
            return False
"""
    validar_int Valida si el valor proporcionado es un número entero.
"""   
def validar_int(num):
    if isinstance(num, int):
        return True
    else:
        return False
# ---------------------------------------------------FUNCIONES YA DE LOS TEMPLATES
@login_required
def perfil_main(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'administrator/perfil_main.html'
    return render(request,template_name,{'profiles':profiles})

"""
    admin_main Función que gestiona la vista principal del administrador.

    1. Verifica que el usuario tenga permisos de acceso a esta sección.
    2. Filtra los productos según el término de búsqueda proporcionado.
    3. Identifica y lista los productos con bajo stock.
    4. Pagina los resultados y los renderiza en la plantilla correspondiente.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.
    - page (int, opcional): Número de página para la paginación.
    - search (str, opcional): Término de búsqueda para filtrar productos.

    Retorno:
    - HttpResponse: Renderiza la plantilla 'admin_main.html' con los productos paginados y el perfil del usuario.
"""
@login_required
def admin_main(request, page=None, search=None):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'administrator/admin_main.html'
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
        if p.supply_total is not None and str(p.supply_total).isdigit():
            if int(p.supply_total) < 5:  # Ajusta este valor según tu criterio para "bajo stock"
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
    paginator = Paginator(low_stock_products, 4)  # Ajusta el número de elementos por página según sea necesario
    p_list_paginate = paginator.get_page(page)   
    return render(request,template_name,{'profiles':profiles, 'p_list_paginate':p_list_paginate})

#Flujo usuarios
@login_required
def users_main(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    groups = Group.objects.all().exclude(pk=0).order_by('id')
    user_id = request.user.id  # Aquí se obtiene la ID actual del Usuario
    template_name = 'administrator/users_main.html'
    return render(request,template_name,{'groups':groups,'profiles':profiles, 'user_id': user_id})


# Generar la contraseña basada en los primeros 6 caracteres del correo electrónico
def generate_password(email):
    
    password = email[:6]
    return password

"""
   new_user Función para crear un nuevo usuario.

    1. Verifica que el usuario tenga permisos de administrador.
    2. Valida los datos proporcionados para crear un nuevo usuario.
    3. Crea el usuario y su perfil si las validaciones son exitosas.
    4. Maneja errores y mensajes informativos.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.

    Retorno:
    - HttpResponse: Renderiza la plantilla 'new_user.html' con la lista de grupos y mensajes informativos.
"""
@login_required
def new_user(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        errores = []
        grupo = request.POST.get('grupo')
        rut = request.POST.get('rut')
        first_name = request.POST.get('name')
        last_name = request.POST.get('last_name1')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        comuna = request.POST.get('comuna')
        generated_password = generate_password(email)
        address = request.POST.get('address')
        region = request.POST.get('region')
        profile_image = request.FILES.get('profile_image')

        # VALIDACIONES CREAR CUENTA
        if not validar_string(first_name, request):
            errores.append('Nombre inválido')
        if not validar_string(last_name, request):
            errores.append('Apellido inválido')
        if not validar_numero(mobile, request):
            errores.append('Número de teléfono inválido')
        if not validar_email(email, request):
            errores.append('Correo electrónico inválido')
        if not validar_rut(rut, request):
            errores.append('RUT inválido')
        if errores:
            messages.add_message(request, messages.INFO, 'Hubo algunos errores al crear el usuario: ' + ', '.join(errores))
            return render(request, 'administrator/new_user.html', {'groups': Group.objects.all().exclude(pk=0).order_by('id')})

        rut_exist = User.objects.filter(username=rut).count()
        mail_exist = User.objects.filter(email=email).count()
        if rut_exist == 0:
            if mail_exist == 0:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=generated_password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True  
                )
                user.save()
                profile_save = Profile(
                    user=user,
                    group_id=grupo,
                    username=email,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    mobile=mobile,
                    region=region,
                    comuna=comuna,
                    rut=rut,
                    first_session='No',
                    token_app_session='No',
                    profile_image=profile_image 
                )
                profile_save.save()
                messages.add_message(request, messages.INFO, 'Usuario creado con éxito')
            else:
                messages.add_message(request, messages.INFO, 'El correo que está tratando de ingresar, ya existe en nuestros registros')
        else:
            messages.add_message(request, messages.INFO, 'El rut que está tratando de ingresar, ya existe en nuestros registros')

    groups = Group.objects.all().exclude(pk=0).order_by('id')
    return render(request, 'administrator/new_user.html', {'groups': groups})


"""
   list_main  Muestra la vista principal de la lista de usuarios basada en el grupo.

    1. Verifica que el usuario tenga permisos adecuados para acceder a esta sección.
    2. Obtiene el grupo especificado por el `group_id`.
    3. Renderiza la plantilla con la información del grupo y el perfil del usuario.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.
    - group_id (int): El ID del grupo para filtrar los usuarios.

    Retorno:
    - HttpResponse: Renderiza la plantilla 'list_main.html' con la información del grupo y el perfil del usuario.
"""
@login_required
def list_main(request,group_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    group = Group.objects.get(pk=group_id)
    template_name = 'administrator/list_main.html'
    return render(request,template_name,{'group':group,'profiles':profiles})
"""
    user_detail_view Muestra los detalles del usuario específico y su perfil.

    1. Obtiene el objeto de usuario y su perfil asociado usando el `user_id`.
    2. Renderiza la plantilla con la información del usuario y el perfil.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.
    - user_id (int): El ID del usuario para obtener los detalles.

    Retorno:
    - HttpResponse: Renderiza la plantilla 'user_detail.html' con la información del usuario y el perfil.
"""
@login_required
def user_detail_view(request, user_id):
    # Obtener el objeto de usuario y su perfil
    user_data = get_object_or_404(User, pk=user_id)
    profile_data = get_object_or_404(Profile, user_id=user_id)
    
    # Renderizar el template y pasar el contexto
    template_name = 'user_detail.html'
    context = {
        'user_data': user_data,
        'profile_data': profile_data
    }
    return render(request, template_name, context)
"""
   list_users  Lista todos los usuarios registrados en el sistema.

    1. Obtiene todos los usuarios del sistema.
    2. Renderiza la plantilla con la lista de usuarios.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.

    Retorno:
    - HttpResponse: Renderiza la plantilla con la lista de usuarios.
"""
@login_required
def list_users(request):
    users = User.objects.all()
    return render(request, 'ruta_a_tu_template.html', {'users': users})    
    
"""
    edit_perfil Permite a un usuario editar su propio perfil.

    Se asegura de que el usuario tenga permisos adecuados (grupo_id == 1).
    Permite la edición de nombre, apellido, teléfono, dirección, región, comuna y foto de perfil.
    Maneja la validación de datos de entrada y muestra mensajes de error si hay problemas.
    Actualiza tanto el modelo User como el modelo Profile correspondiente.

    Returns:
        HttpResponseRedirect o HttpResponse: Redirige al usuario a la página de listado de usuarios activos o 
        renderiza la plantilla 'edit_perfil.html' con los datos del usuario.

    Template:
        'administrator/edit_perfil.html': Plantilla utilizada para mostrar el formulario de edición de perfil.

    Contexto de la plantilla:
        user_data (User): Instancia del modelo User del usuario actual.
        profile_data (Profile): Instancia del modelo Profile del usuario actual.
        groups (Group): Instancia del grupo al que pertenece el usuario.
        profile_list (QuerySet): Lista de todos los grupos disponibles para selección en el formulario.

"""
@login_required
def edit_perfil(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        errores = []
        grupo = request.POST.get('grupo')
        user_id = request.POST.get('user_id')
        first_name = request.POST.get('name')
        last_name = request.POST.get('last_name1')
        mobile = request.POST.get('phone')
        address = request.POST.get('address')
        region = request.POST.get('region')
        comuna = request.POST.get('comuna')
        profile_image = request.FILES.get('profile_image')
        template_name = 'administrator/edit_perfil.html'
        user_data_count = User.objects.filter(pk=request.user.id).count()
        user_data = User.objects.get(pk=request.user.id)
        profile_data = Profile.objects.get(user_id=request.user.id)

        # Validar strings y números
        if not validar_string(first_name, request):
            errores.append('Nombre inválido')
        if not validar_string(last_name, request):
            errores.append('Apellido inválido')
        if not validar_numero(mobile, request):
            errores.append('Número de teléfono inválido')
        if errores:
            messages.add_message(request, messages.INFO, 'Hubo algunos errores al editar el perfil: ' + ', '.join(errores))
            return render(request, template_name, {'user_data': user_data, 'profile_data': profile_data, 'groups': groups, 'profile_list': profile_list, 'region': region, 'comuna': comuna})

        if user_data_count == 1:
            User.objects.filter(pk=request.user.id).update(first_name=first_name, last_name=last_name)
            profile_data.first_name = first_name
            profile_data.last_name = last_name
            profile_data.mobile = mobile
            profile_data.address = address
            profile_data.region = region
            profile_data.comuna = comuna

            # Manejar la foto de perfil
            if profile_image:
                fs = FileSystemStorage()
                filename = fs.save(profile_image.name, profile_image)
                profile_data.profile_image = filename  # Solo almacena el nombre del archivo

            profile_data.save()

            messages.add_message(request, messages.INFO, f'Usuario {user_data.first_name} {user_data.last_name} editado con éxito')
            return redirect('list_user_active', grupo)
        else:
            messages.add_message(request, messages.INFO, f'Hubo un error al editar el Usuario {user_data.first_name} {user_data.last_name}')
            return redirect('list_user_active', profile_data.group_id)

    user_data = User.objects.get(pk=request.user.id)
    profile_data = Profile.objects.get(user_id=request.user.id)
    groups = Group.objects.get(pk=profile_data.group_id)
    profile_list = Group.objects.all().exclude(pk=0).order_by('name')

    template_name = 'administrator/edit_perfil.html'
    return render(request, template_name, {'user_data': user_data, 'profile_data': profile_data, 'groups': groups, 'profile_list': profile_list})
"""
    edit_user Permite a los administradores editar usuarios

    1. Verifica que el usuario tenga permisos adecuados para acceder a esta sección.
    2. Valida los datos proporcionados en el formulario de edición.
    3. Actualiza el perfil del usuario con los datos proporcionados.
    4. Maneja la subida de la imagen de perfil.
    5. Renderiza la plantilla con los datos actuales del usuario y posibles errores.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.

    Retorno:
    - HttpResponse: Renderiza la plantilla 'edit_perfil.html' con la información del usuario y el perfil.
"""
    
@login_required
def edit_user(request, user_id):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        errores = []
        user_id = request.POST.get('user_id')
        first_name = request.POST.get('name')
        last_name = request.POST.get('last_name1')
        email = request.POST.get('email')
        group = request.POST.get('grupo')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        region = request.POST.get('region')
        comuna = request.POST.get('comuna')
        profile_image = request.FILES.get('profile_image')  # Obtén la imagen de perfil del formulario

        template_name = 'administrator/edit_user.html'
        profile_data = Profile.objects.get(user_id=user_id)
        groups = Group.objects.get(pk=profile_data.group_id)
        user_data = User.objects.filter(pk=user_id).first()

        # Validar campos
        if not validar_string(first_name, request):
            errores.append('Nombre inválido')
        if not validar_string(last_name, request):
            errores.append('Apellido inválido')
        if not validar_numero(mobile, request):
            errores.append('Número de teléfono inválido')
        if errores:
            messages.add_message(request, messages.INFO, 'Hubo algunos errores al editar el usuario: ' + ', '.join(errores))
            return render(request, template_name, {'user_data': user_data, 'profile_data': profile_data, 'groups': groups, 'profile_list': Group.objects.all().exclude(pk=0).order_by('name')})

        if user_data is None:
            messages.add_message(request, messages.INFO, 'El usuario no existe.')
            return redirect('list_user_active')

        if user_data.email != email and User.objects.filter(email=email).exists():
            messages.add_message(request, messages.INFO, f'El correo {email} ya existe en nuestros registros asociado a otro usuario. Por favor, utilice otro.')
            return redirect('list_user_active', group)

        # Actualizar datos de usuario
        User.objects.filter(pk=user_id).update(first_name=first_name, last_name=last_name)

        # Actualizar datos de perfil
        profile_data.first_name = first_name
        profile_data.last_name = last_name
        profile_data.mobile = mobile
        profile_data.address = address
        profile_data.region = region
        profile_data.comuna = comuna
        profile_data.group_id = group

        if profile_image:
            profile_data.profile_image = profile_image  # Actualiza la imagen de perfil si se proporcionó una nueva

        profile_data.save()

        messages.add_message(request, messages.INFO, f'Usuario {user_data.first_name} {user_data.last_name} editado con éxito.')
        return redirect('list_user_active', group)

    user_data = User.objects.get(pk=user_id)
    profile_data = Profile.objects.get(user_id=user_id)
    groups = Group.objects.get(pk=profile_data.group_id)
    profile_list = Group.objects.all().exclude(pk=0).order_by('name')
    template_name = 'administrator/edit_user.html'
    return render(request, template_name, {
        'user_data': user_data,
        'profile_data': profile_data,
        'groups': groups,
        'profile_list': profile_list,
        'profile_image_url': profile_data.profile_image.url if profile_data.profile_image else None
    })



"""
    list_user_active Muestra una lista de usuarios activos de un grupo específico con opción de búsqueda y paginación.

    1. Verifica que el usuario tenga permisos adecuados para acceder a esta sección.
    2. Obtiene los usuarios activos del grupo especificado.
    3. Filtra la lista de usuarios basada en una búsqueda opcional.
    4. Pagina los resultados y renderiza la plantilla con la lista de usuarios.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.
    - group_id (int): El ID del grupo para filtrar los usuarios.
    - page (int, opcional): El número de página para la paginación.

    Retorno:
    - HttpResponse: Renderiza la plantilla 'list_user_active.html' con la lista de usuarios activos.
    """
@login_required
def list_user_active(request, group_id, page=None):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id not in [1, 2]:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    search = request.GET.get('search','')
    
    if page is None:
        page = request.GET.get('page')
    
    group = Group.objects.get(pk=group_id)
    user_array = User.objects.filter(is_active=True, profile__group_id=group_id)
    
    if search:
        user_array = user_array.filter(first_name__icontains=search)

    user_all = []
    for us in user_array:
        profile_data = Profile.objects.get(user_id=us.id)
        name = us.first_name + ' ' + us.last_name
        user_all.append({'id': us.id, 'user_name': us.username, 'name': name, 'mail': us.email})

    paginator = Paginator(user_all, 5)
    user_list = paginator.get_page(page)
    template_name = 'administrator/list_user_active.html'
    return render(request, template_name, {
        'profiles': profiles,
        'group': group,  # Asegúrate de pasar el grupo a la plantilla
        'user_list': user_list,
        'paginator': paginator,
        'page': page,
        'search': search
    })
"""
   list_user_block Muestra una lista de usuarios bloqueados de un grupo específico con opción de búsqueda y paginación.

    1. Verifica que el usuario tenga permisos adecuados para acceder a esta sección.
    2. Obtiene los usuarios bloqueados del grupo especificado.
    3. Filtra la lista de usuarios basada en una búsqueda opcional.
    4. Pagina los resultados y renderiza la plantilla con la lista de usuarios bloqueados.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.
    - group_id (int): El ID del grupo para filtrar los usuarios.
    - page (int, opcional): El número de página para la paginación.

    Retorno:
    - HttpResponse: Renderiza la plantilla 'list_user_block.html' con la lista de usuarios bloqueados.
"""

@login_required    
def list_user_block(request, group_id, page=None):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id not in [1, 2]:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')

    search = request.GET.get('search')
    
    if page is None:
        page = request.GET.get('page')
    
    group = Group.objects.get(pk=group_id)
    user_array = User.objects.filter(is_active=False, profile__group_id=group_id)
    
    if search:
        user_array = user_array.filter(first_name__icontains=search)

    user_all = []
    for us in user_array:
        profile_data = Profile.objects.get(user_id=us.id)
        name = us.first_name + ' ' + us.last_name
        user_all.append({'id': us.id, 'user_name': us.username, 'name': name, 'mail': us.email})

    paginator = Paginator(user_all, 8)
    user_list = paginator.get_page(page)
    template_name = 'administrator/list_user_block.html'
    return render(request, template_name, {'profiles': profiles, 'group': group, 'user_list': user_list, 'paginator': paginator, 'page': page, 'search': search})


"""
    user_block Bloquea a un usuario desactivando su cuenta.

    1. Verifica que el usuario tenga permisos adecuados para realizar esta acción.
    2. Cambia el estado de la cuenta del usuario especificado a inactivo.
    3. Redirige a la lista de usuarios activos después de bloquear la cuenta.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.
    - user_id (int): El ID del usuario a bloquear.

    Retorno:
    - HttpResponseRedirect: Redirige a la lista de usuarios activos o muestra un mensaje de error.
"""
@login_required
def user_block(request,user_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')

    user_data_count = User.objects.filter(pk=user_id).count()
    user_data = User.objects.get(pk=user_id)
    profile_data = Profile.objects.get(user_id=user_id)       
    if user_data_count == 1:
        User.objects.filter(pk=user_id).update(is_active='f')
        messages.add_message(request, messages.INFO, 'Usuario '+user_data.first_name +' '+user_data.last_name+' eliminado con éxito')
        return redirect('list_user_active',profile_data.group_id)        
    else:
        messages.add_message(request, messages.INFO, 'Hubo un error al eliminar el Usuario '+user_data.first_name +' '+user_data.last_name)
        return redirect('list_user_active',profile_data.group_id)      

"""
    user_activate Activa una cuenta de usuario que está actualmente desactivada.

    1. Verifica que el usuario tenga permisos adecuados para realizar esta acción.
    2. Cambia el estado de la cuenta del usuario especificado a activo.
    3. Redirige a la lista de usuarios bloqueados después de activar la cuenta.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.
    - user_id (int): El ID del usuario a activar.

    Retorno:
    - HttpResponseRedirect: Redirige a la lista de usuarios bloqueados o muestra un mensaje de error.
"""      
@login_required
def user_activate(request,user_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    user_data_count = User.objects.filter(pk=user_id).count()
    user_data = User.objects.get(pk=user_id)
    profile_data = Profile.objects.get(user_id=user_id)       
    if user_data_count == 1:
        User.objects.filter(pk=user_id).update(is_active='t')
        messages.add_message(request, messages.INFO, 'Usuario '+user_data.first_name +' '+user_data.last_name+' recuperado con éxito')
        return redirect('list_user_block',profile_data.group_id)        
    else:
        messages.add_message(request, messages.INFO, 'Hubo un error al activar el Usuario '+user_data.first_name +' '+user_data.last_name)
        return redirect('list_user_block',profile_data.group_id)        
"""
    user_delete Elimina una cuenta de usuario de la base de datos.

    1. Verifica que el usuario tenga permisos adecuados para realizar esta acción.
    2. Elimina tanto el perfil como la cuenta del usuario especificado.
    3. Redirige a la lista de usuarios bloqueados después de eliminar la cuenta.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.
    - user_id (int): El ID del usuario a eliminar.

    Retorno:
    - HttpResponseRedirect: Redirige a la lista de usuarios bloqueados o muestra un mensaje de error.
"""
@login_required
def user_delete(request,user_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')

    user_data_count = User.objects.filter(pk=user_id).count()
    user_data = User.objects.get(pk=user_id)
    profile_data = Profile.objects.get(user_id=user_id)       
    if user_data_count == 1:
        #Profile.objects.filter(user_id=user_id).delete()
        Profile.objects.filter(user_id=user_id).delete()
        User.objects.filter(pk=user_id).delete()
        messages.add_message(request, messages.INFO, 'Usuario '+user_data.first_name +' '+user_data.last_name+' eliminado con éxito')
        return redirect('list_user_block',profile_data.group_id)        
    else:
        messages.add_message(request, messages.INFO, 'Hubo un error al eliminar el Usuario '+user_data.first_name +' '+user_data.last_name)
        return redirect('list_user_block',profile_data.group_id) 
         
    

"""
   carga_masiva_user Muestra la página de carga masiva de usuarios.

    Verifica que el usuario tenga permisos adecuados para realizar esta acción.
    Renderiza la plantilla 'carga_masiva_user.html' con el perfil del usuario.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.

    Retorno:
    - HttpResponse: Renderiza la plantilla 'carga_masiva_user.html' con el contexto del perfil del usuario.
"""
@login_required
def carga_masiva_user(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'administrator/carga_masiva_user.html'
    return render(request, template_name, {'profiles': profile})
"""
    import_file_user Genera un archivo Excel de ejemplo para importar usuarios.

    Verifica que el usuario tenga permisos adecuados para realizar esta acción.
    Genera un archivo Excel con una fila de ejemplo y lo descarga automáticamente.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.

    Retorno:
    - HttpResponse: Descarga el archivo Excel con el nombre 'archivo_importacion_usuario.xlsx'.
"""
@login_required
def import_file_user(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="archivo_importacion_usuario.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = 'carga_masiva'
    
    columns = ['Rut', 'Correo', 'Nombre', 'Apellido', ' Teléfono', 'Dirección', 'Región', 'Comuna']
    ws.append(columns)
    
    example_data = [ 
        'ej: 17605812-2',
        'ej: bc@gmail.com',
        'ej: Nombre usuario',
        'ej: Apellido usuario',
        'ej: 955642334',
        'ej: Av. central 123',
        'ej: Tarapacá',
        'ej: Iquique'
    ]
    ws.append(example_data)
    
    wb.save(response)
    return response


"""
    carga_masiva_user_save Procesa y guarda los usuarios importados desde un archivo Excel.

    Verifica que el usuario tenga permisos adecuados para realizar esta acción.
    Lee un archivo Excel cargado por el usuario, valida los datos y crea usuarios y perfiles en la base de datos.

    Parámetros:
    - request (HttpRequest): El objeto de solicitud HTTP.

    Retorno:
    - HttpResponseRedirect: Redirige a la página de formulario de carga masiva de usuarios o muestra un mensaje de error.
"""

@login_required
def carga_masiva_user_save(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        try:
            # Leer el archivo Excel
            uploaded_file = request.FILES['myfile']
            print("Archivo recibido: ", uploaded_file.name)
            print("Tamaño del archivo: ", uploaded_file.size)
            print("Tipo de contenido del archivo: ", uploaded_file.content_type)

            data = pd.read_excel(uploaded_file, engine='openpyxl', skiprows=1)
            df = pd.DataFrame(data)
            print("Contenido del DataFrame después de la lectura:")
            print(df)  # Mostrar el contenido del DataFrame para verificar los datos

            if df.empty:
                messages.add_message(request, messages.ERROR, 'El archivo Excel está vacío o no contiene datos válidos.')
                return redirect('carga_masiva_user_form')

            acc = 0

            # Obtener los usuarios activos una vez antes de iterar
            usuarios_activos = User.objects.filter(is_active=True).values_list('username', 'profile__rut')
            emails_activos = {usuario[0] for usuario in usuarios_activos}
            ruts_activos = {usuario[1] for usuario in usuarios_activos}
            print("RUTs Activos: ", ruts_activos)
            print("Emails Activos: ", emails_activos)

            for item in df.itertuples(index=False):
                rut = str(item[0])
                email = str(item[1])
                nombre = str(item[2])
                apellido = str(item[3])
                mobile = str(item[4])
                address = str(item[5])
                region = str(item[6])
                comuna = str(item[7])

                print(f"Procesando RUT: {rut}, Email: {email}")

                if rut in ruts_activos:
                    messages.add_message(request, messages.INFO, f'El RUT "{rut}" ya existe en nuestros registros.')
                    continue

                if email in emails_activos:
                    messages.add_message(request, messages.INFO, f'El correo electrónico "{email}" ya existe en nuestros registros.')
                    continue

                if not validar_rut(rut, request):
                    messages.add_message(request, messages.INFO, f'El RUT "{rut}" no es válido.')
                    continue

                if not validar_email(email, request):
                    messages.add_message(request, messages.INFO, f'El correo electrónico "{email}" no es válido.')
                    continue

                if not validar_string(nombre, request) or not validar_string(apellido, request):
                    messages.add_message(request, messages.INFO, 'El nombre y/o apellido no son válidos.')
                    continue

                if not validar_numero(mobile, request):
                    messages.add_message(request, messages.INFO, f'El número de teléfono "{mobile}" no es válido.')
                    continue

                new_user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=nombre,
                    last_name=apellido,
                    password=User.objects.make_random_password(),
                    is_active=True
                )

                new_profile = Profile(
                    user=new_user,
                    group_id=1,
                    mobile=mobile,
                    address=address,
                    region=region,
                    comuna=comuna,
                    rut=rut
                )
                new_profile.save()

                acc += 1

            messages.add_message(request, messages.INFO, f'Carga masiva finalizada, se importaron {acc} registros')
            return redirect('carga_masiva_user_form')

        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Error al procesar el archivo: {str(e)}')
            return redirect('carga_masiva_user_form')

    return HttpResponseRedirect(reverse('carga_masiva_user_form'))



@login_required
def new_group(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if group_name:
            new_group = Group.objects.create(name=group_name)
            return redirect('user_main')
        else:
            messages.add_message(request, messages.ERROR, 'El nombre del grupo no puede estar vacío')
            return redirect('new_group')
    else:
        template_name = 'administrator/new_group.html'
        return render(request,template_name,{'profiles':profile})

       







def ejemplo_query_set(request):
    #los query set que estan acontinuación retornan elementos iterables
    #para obtener todos los datos de un modelo
    user_array =  User.objects.all()
    #para obtener todos los datos de un modelo ordenados por algún criterio
    user_array =  User.objects.all().order_by('username') #Ascendente
    user_array =  User.objects.all().order_by('-username') #Descendente
    #para obtener todos los datos de un modelo filtrado por algún criterio
    #para obtener todos los datos de un modelo excluyendo en base a algún criterio
    user_array =  User.objects.all().exclude(username='1234567')
    #si el criterio no existe retornará una lista vacia
    user_array =  User.objects.filter(username='1234567')  
    user_array =  User.objects.filter(username='1234567').order_by('username')#Ascendente
    user_array =  User.objects.filter(username='1234567').order_by('-username')#Descendente
    #para obtener todos los datos de un modelo filtrado por mas de un criterio
    user_array =  User.objects.filter(username='1234567').filter(is_active='t')  
    user_array =  User.objects.filter(username='1234567').filter(is_active='t').order_by('username')#Ascendente
    user_array =  User.objects.filter(username='1234567').filter(is_active='t').order_by('-username')#Descendente
    #para obtener todos los datos de un modelo filtrado por un criterio u otro
    #para usar el o debe importarlo al inicio del archivo from django.db.models Q
    user_array =  User.objects.filter(Q(username='1234567')|Q(is_active='t'))  
    user_array =  User.objects.filter(Q(username='1234567')|Q(is_active='t')).order_by('username')#Ascendente
    user_array =  User.objects.filter(Q(username='1234567')|Q(is_active='t')).order_by('-username')#Descendente

    #para obtener un solo registro
    '''
    si bien se suele usar con el id (pk), se pueden usar con cualquier otro criterio, de usarlo de esta forma debe 
    estar seguro de que le retornará un solo registro, ya que caso contrario le arrojará un error
    '''
    user_data = User.objects.get(pk=1)
    #si desea usar con otro criterio distinto a comparar con pk 
    user_data = User.objects.filter(is_active='t').first()#retorna el primer elemento de la lista
    #para actualizar registros
    User.objects.filter(pk=1).update(is_active='f')#actualiza el registro asociado al id
    User.objects.filter(is_active='f').update(is_active='t')#actualiza todos los registros que cumplen con el criterio
    #para contar registros
    user_data_count = User.objects.filter(pk=1).count()
    #la creación de registros la abordaremos más adelante


    print(user_data_count)
    return redirect('login')



