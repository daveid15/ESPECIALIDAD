from django.conf.urls import url, include
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from ventas import views

ventas_patterns = [
    path('ventas_main',views.ventas_main,name='ventas_main'),
    path('venta_crear', views.venta_crear, name='venta_crear'),
    path('venta_save', views.venta_save,name='venta_save'),
    path('venta_list', views.venta_list, name='venta_list'),
    path('detalle_orden_venta/<int:orden_id>/', views.detalle_orden_venta, name='detalle_orden_venta')
]
 