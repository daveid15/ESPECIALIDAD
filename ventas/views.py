from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import JsonResponse
from random import randrange
from django.db.models import Sum
from django.db.models import F, ExpressionWrapper, DecimalField

from registration.models import Profile
from ventas.models import Prod_venta, Orden_venta, Venta_producto
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Sum
from django.http import JsonResponse
from datetime import timedelta
from django.db.models.functions import TruncMinute
from administrator.views import validar_string, validar_int

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Prod_venta, Orden_venta, Venta_producto
from django.contrib.auth.decorators import login_required


def ventas_main(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tienes permisos')
        return redirect('check_group_main')

    template_name = 'ventas/ventas_main.html'
    return render(request, template_name, {'profiles': profiles})

def get_chart_data(_request):
    productos_venta = ['Completo Italiano', 'Completo Personalizado', 'Bebida']
    
    # Lista para almacenar las ganancias por producto
    ganancias_por_producto = []
    
    # Iterar sobre cada producto
    for producto in productos_venta:
        # Obtener el producto correspondiente
        prod_venta = Prod_venta.objects.get(nombre_producto=producto)
        
        # Calcular la ganancia total del producto sumando el producto de la cantidad y el precio de cada venta
        ganancia_total = Venta_producto.objects.filter(producto=prod_venta).aggregate(
            ganancia_total=Sum(ExpressionWrapper(F('cantidad') * F('precio_producto'), output_field=DecimalField()))
        )['ganancia_total'] or 0
        
        # Agregar la ganancia total a la lista
        ganancias_por_producto.append(ganancia_total)
    
    chart_data = {
        "title": {
            "text": 'Ganancias de Productos Vendidos'
        },
        "tooltip": {
            "trigger": 'axis',
            "axisPointer": {
                "type": 'shadow'
            }
        },
        'xAxis': {
            'type': 'category',
            'data': productos_venta, 'itemStyle': {'color': '#c4a0ff'}
        },
        'yAxis': {
            'type': 'value'
        },
        'series': [
            {
                'data': ganancias_por_producto, 'itemStyle': {'color': '#c4a0ff'},
                'type': 'bar'
            }
        ]
    }

    return JsonResponse(chart_data)


def get_chart_data_venta(_request):
    # Tiempo actual
    now = timezone.now()

    # Obtener el tiempo de inicio almacenado en la caché
    start_time = cache.get('start_time')

    if start_time is None:
        # Si no hay tiempo de inicio, establecerlo como el tiempo actual
        start_time = now
        cache.set('start_time', start_time)

    # Calcular la diferencia de tiempo
    time_elapsed = now - start_time

    # Valor fijo de referencia (meta)
    fixed_value = 1000000

    if time_elapsed >= timedelta(minutes=1): #DEFINICIÓN DEL LAPSO DE TIEMPO
        # Si ha pasado más de un minuto, reiniciar el valor dinámico y el tiempo de inicio
        dynamic_value = 0
        cache.set('start_time', now)
    else:
        # Calcular el valor dinámico actual
        dynamic_value = Orden_venta.objects.aggregate(total_ventas=Sum('total_venta'))['total_ventas'] or 0

    empty_value = fixed_value - dynamic_value  # Valor restante para completar el 100%

    chart_data = {
        'title': {
            'text': 'Meta: $1.000.000',
            'left': 'center'
        },
        'tooltip': {
            'trigger': 'item'
        },
        'legend': {
            'top': '5%',
            'left': 'center'
        },
        'series': [
            {
                'name': 'Ventas',
                'type': 'pie',
                'radius': ['40%', '70%'],
                'center': ['50%', '70%'],
                'startAngle': 180,
                'endAngle': 360,
                'label': {
                    'show': True,
                    'formatter': '{b}: {c} ({d}%)'
                },
                'data': [
                    {'value': dynamic_value, 'name': 'Ganancias Totales'},
                    {'value': empty_value, 'name': 'Ganancias Faltantes', 'itemStyle': {'color': '#cccccc'}}
                ]
            }
        ]
    }

    return JsonResponse(chart_data)



def get_chart_data_completos_bebidas(_request):
    # Consulta los datos de la base de datos 
    completos = Venta_producto.objects.filter(producto__nombre_producto='Completo Italiano').aggregate(total=Sum('cantidad'))['total'] or 0
    completos_personalizados = Venta_producto.objects.filter(producto__nombre_producto='Completo Personalizado').aggregate(total=Sum('cantidad'))['total'] or 0
    bebidas = Venta_producto.objects.filter(producto__nombre_producto='Bebida').aggregate(total=Sum('cantidad'))['total'] or 0

    # Datos del gráfico
    categorias = ['Italianos', 'Personalizados', 'Bebidas']
    cantidades = [completos, completos_personalizados, bebidas]

    # Formatear datos para ECharts
    chart_data = {
        "title": {
            "text": 'Cantidad Productos Vendidos'
        },
        "tooltip": {
            "trigger": 'axis',
            "axisPointer": {
                "type": 'shadow'
            }
        },
        "xAxis": {
            "type": 'category',
            "data": categorias
        },
        "yAxis": {
            "type": 'value'
        },
        "series": [
            {
                "name": 'Ventas',
                "type": 'bar',
                "data": cantidades, 'itemStyle': {'color': '#f2a0ff'}
            }
        ]
    }

    return JsonResponse(chart_data)


"""
    venta_save Vista para procesar el formulario de creación de una orden de venta.

    Métodos HTTP admitidos: POST
    Requiere autenticación del usuario.

    Funcionalidad:
    - Valida la información del cliente.
    - Valida las cantidades de productos ingresadas.
    - Crea una nueva orden de venta en transacción atómica.
    - Registra cada producto vendido en la orden con su cantidad y precio.
    - Calcula y guarda el total de la venta.

    Retorna:
    - Redirige a 'venta_crear' después de procesar la orden de venta.
    - Muestra mensajes de éxito o error según el resultado.

    Errores manejados:
    - Si no se proporciona toda la información del cliente.
    - Si las cantidades ingresadas no son números enteros válidos.
    - Si no se agrega al menos un producto con cantidad mayor a 0.
    - Cualquier error durante la creación de la orden de venta.

"""

@login_required
def venta_save(request):
    if request.method == 'POST':
        cliente_name = request.POST.get('cliente_name')
        cliente_last_name = request.POST.get('cliente_last_name')
        producto_venta = ['Completo Italiano', 'Completo Personalizado', 'Bebida']
        cantidades = [
            request.POST.get('cantidad_italiano'),
            request.POST.get('cantidad_personalizado'),
            request.POST.get('cantidad_bebida')
        ]
        cliente_venta = f"{cliente_name} {cliente_last_name}"
        
        # Validar que se ha proporcionado toda la información del cliente
        if not cliente_name or not cliente_last_name:
            messages.error(request, 'Debes ingresar toda la información del cliente')
            return redirect('venta_crear')

        try:
            cantidades_validas = [int(cant) if cant else 0 for cant in cantidades]
        except ValueError:
            messages.error(request, 'Las cantidades deben ser números enteros válidos')
            return redirect('venta_crear')
        
        # Comprobar que al menos un producto tenga una cantidad mayor a 0
        if all(cant == 0 for cant in cantidades_validas):
            messages.error(request, 'ERROR: Debe haber al menos un producto agregado para crear la venta')
            return redirect('venta_crear')

        try:
            with transaction.atomic():
                orden_venta = Orden_venta.objects.create(cliente_venta=cliente_venta)
                total_venta = 0

                for prod, cant in zip(producto_venta, cantidades_validas):
                    if cant > 0:
                        producto_instancia = Prod_venta.objects.get(nombre_producto=prod)
                        Venta_producto.objects.create(
                            producto=producto_instancia,
                            cantidad=cant,
                            id_orden=orden_venta,
                            precio_producto=producto_instancia.precio
                        )
                        total_venta += producto_instancia.precio * cant

                orden_venta.total_venta = total_venta
                orden_venta.save()

                messages.success(request, f'Orden de Venta #{orden_venta.numero_orden} creada con éxito')
                return redirect('venta_crear')
        except Exception as e:
            messages.error(request, f'Error al crear la orden: {str(e)}')
            return redirect('venta_crear')
    else:
        messages.error(request, 'Error en el método de envío')
        return redirect('venta_crear')
    
@login_required
def venta_list(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')

    search_query = request.GET.get('search')
    ordenes = Orden_venta.objects.all()
    
    if search_query:
        ordenes = ordenes.filter(cliente_venta__icontains=search_query)

    paginator = Paginator(ordenes, 5)
    page_number = request.GET.get('page')

    try:
        ordenes = paginator.page(page_number)
    except PageNotAnInteger:
        ordenes = paginator.page(1)
    except EmptyPage:
        ordenes = paginator.page(paginator.num_pages)
        
    return render(request, 'ventas/venta_list.html', {'ordenes': ordenes, 'search_query': search_query})
    
@login_required
def venta_crear(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id not in [1, 2]:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')
    
    productos = Prod_venta.objects.all()
    template_name = 'ventas/venta_crear.html'
    orden = Orden_venta.objects.all()
    
    return render(request, template_name, {'profiles': profiles, 'productos': productos})

@login_required
def detalle_orden_venta(request, orden_id):
    orden = Orden_venta.objects.get(numero_orden=orden_id)
    ventas_productos = orden.venta_producto_set.all()  # Utiliza el nombre del modelo en minúsculas seguido de _set para acceder a los objetos relacionados
    return render(request, 'detalle_orden_venta.html', {'orden': orden, 'ventas_productos': ventas_productos})

