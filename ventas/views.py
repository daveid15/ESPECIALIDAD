from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from registration.models import Profile
from ventas.models import Prod_venta, Orden_venta, Venta_producto

@login_required
def ventas_main(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1 and profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tienes permisos')
        return redirect('check_group_main')
    template_name = 'ventas/ventas_main.html'
    return render(request, template_name, {'profiles': profiles})

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
        
    return render(request, 'ventas/venta_list.html', {'ordenes': ordenes, 'search': search, 'pagina_obj': ordenes})
    
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
