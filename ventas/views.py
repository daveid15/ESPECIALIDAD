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
        'xAxis': {
            'type': 'category',
            'data': productos_venta
        },
        'yAxis': {
            'type': 'value'
        },
        'series': [
            {
                'data': ganancias_por_producto,
                'type': 'bar'
            }
        ]
    }

    return JsonResponse(chart_data)


from django.utils import timezone
from django.core.cache import cache
from django.db.models import Sum
from django.http import JsonResponse
from datetime import timedelta


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

    if time_elapsed >= timedelta(minutes=1): #SE PUEDE CAMBIAR POR HOURS O MINUTES DEPENDIENDO DE LOQ SE BUSKE
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



@login_required
def venta_save(request):
    if request.method == 'POST':
        cliente_name = request.POST.get('cliente_name')
        cliente_last_name = request.POST.get('cliente_last_name')
        producto_venta = ['Completo Italiano', 'Completo Personalizado', 'Bebida']  # Esto debería obtenerse del formulario: request.POST.getlist('producto_venta')
        cantidad_venta = request.POST.getlist('cantidad_venta')
        cliente_venta = f"{cliente_name} {cliente_last_name}"
        
        # Comprobar si se ha proporcionado toda la información
        if not all([cliente_name, cliente_last_name]):
            messages.error(request, 'Debes ingresar toda la información')
            return redirect('venta_crear')
        
        # Comprobar que al menos un producto tenga una cantidad mayor a 0
        cantidades_validas = [int(cant) if cant else 0 for cant in cantidad_venta]
        if all(cant == 0 for cant in cantidades_validas):
            messages.error(request, 'ERROR: Debe haber al menos un producto agregado cpara crear la venta')
            return redirect('venta_crear')
        
        try:
            with transaction.atomic():
                orden_venta = Orden_venta.objects.create(cliente_venta=cliente_venta)
                total_venta = 0

                for prod, cant in zip(producto_venta, cantidades_validas):
                    producto_instancia = Prod_venta.objects.get(nombre_producto=prod)
                    venta_producto = Venta_producto.objects.create(producto=producto_instancia, cantidad=cant, id_orden=orden_venta, precio_producto=producto_instancia.precio)
                    venta_producto.save()
                    total_venta += producto_instancia.precio * cant

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
def venta_list(request, page=None, search=None):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tienes permisos')
        return redirect('check_group_main')

    search = request.GET.get('search')
    ordenes = Orden_venta.objects.all()
    total_ventas = ordenes.aggregate(total_ventas=Sum('total_venta'))['total_ventas'] or 0  # Valor dinámico actual
    
    if search:
        ordenes = ordenes.filter(Q(cliente_venta__icontains=search))

    paginator = Paginator(ordenes, 10)
    pagina_numero = request.GET.get('pagina')
    
    try:
        ordenes = paginator.page(pagina_numero)
    except PageNotAnInteger:
        ordenes = paginator.page(1)
    except EmptyPage:
        ordenes = paginator.page(paginator.num_pages)
        
    return render(request, 'ventas/venta_list.html', {'ordenes': ordenes, 'search': search, 'pagina_obj': ordenes, 'total_ventas': total_ventas})
    
@login_required
def venta_crear(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id not in [1, 2]:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')
    
    productos = Prod_venta.objects.all()
    template_name = 'ventas/venta_crear.html'
    
    return render(request, template_name, {'profiles': profiles, 'productos': productos})

@login_required
def detalle_orden_venta(request, orden_id):
    orden = Orden_venta.objects.get(numero_orden=orden_id)
    ventas_productos = orden.venta_producto_set.all()  # Utiliza el nombre del modelo en minúsculas seguido de _set para acceder a los objetos relacionados
    return render(request, 'detalle_orden_venta.html', {'orden': orden, 'ventas_productos': ventas_productos})

#DASHBOARD

@login_required
def get_chart_ventas(request):
    colors = ['blue', 'orange', 'red', 'black', 'yellow', 'green', 'magenta', 'lightblue', 'purple', 'brown']
    random_color = colors[randrange(0, len(colors))]

    serie = [randrange(100, 400) for _ in range(7)]

    chart = {
        'tooltip': {
            'show': True,
            'trigger': "axis",
            'triggerOn': "mousemove|click"
        },
        'xAxis': [
            {
                'type': "category",
                'data': ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            }
        ],
        'yAxis': [
            {
                'type': "value"
            }
        ],
        'series': [
            {
                'data': serie,
                'type': "line",
                'itemStyle': {
                    'color': random_color
                },
                'lineStyle': {
                    'color': random_color
                }
            }
        ]
    }

    return JsonResponse(chart)
