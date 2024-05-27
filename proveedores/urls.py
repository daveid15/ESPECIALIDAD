from django.conf.urls import url, include
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from proveedores import views
from .views import descarga_reporte

proveedores_patterns = [
    
    path('proveedores_main', views.proveedores_main,name='proveedores_main'),
    path('proveedores_crear', views.proveedores_crear,name='proveedores_crear'),
    
    path('proveedor_edit/<int:proveedor_id>/', views.proveedor_edit,name='proveedor_edit'),
    path('proveedor_save/', views.proveedor_save,name='proveedor_save'),
    path('proveedor_list/', views.proveedor_list,name='proveedor_list'),
    
    path('proveedor_delete/<int:proveedor_id>/', views.proveedor_delete,name='proveedor_delete'),
    path('proveedor_ver/<int:proveedor_id>/', views.proveedor_ver,name='proveedor_ver'),
    path('carga_masiva_proveedor/',views.carga_masiva_proveedor,name="carga_masiva_proveedor"),
    path('carga_masiva_proveedor_save/',views.carga_masiva_proveedor_save,name="carga_masiva_proveedor_save"),
    path('import_file_proveedor/',views.import_file_proveedor,name="import_file_proveedor"),
    path('descarga_reporte/',views.descarga_reporte,name="descarga_reporte"),
    path('proveedores/seleccion/', views.seleccion_proveedores, name='seleccion_proveedores'),
    path('proveedores/activos/', views.proveedores_activos, name='proveedores_activos'),
    path('proveedores/eliminados/', views.proveedores_eliminados, name='proveedores_eliminados'),
    path('proveedores/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('proveedores/restaurar/<int:proveedor_id>/', views.restaurar_proveedor, name='restaurar_proveedor'),


#Órden de Compra
    path('orden_main', views.orden_main,name='orden_main'),
    path('orden_crear/', views.orden_crear, name='orden_crear'),
    path('orden_save', views.orden_save,name='orden_save'),
    path('lista_orden/<int:grupo_id>/', views.lista_orden, name='lista_orden'),
    path('orden_list_enviada/',views.orden_list_enviada,name='orden_list_enviada'),
    path('orden_list_rechazada/',views.orden_list_rechazada,name='orden_list_rechazada'),
    path('orden_list_aceptada/',views.orden_list_aceptada,name='orden_list_aceptada'),
    path('orden_list_anulada/',views.orden_list_anulada,name='orden_list_anulada'),
    path('cambiar_estado_orden_enviada/<int:orden_id>/', views.cambiar_estado_orden_enviada, name='cambiar_estado_orden_enviada'),
    path('cambiar_estado_orden_rechazada/<int:orden_id>/', views.cambiar_estado_orden_rechazada, name='cambiar_estado_orden_rechazada'),
    path('cambiar_estado_orden_aceptada/<int:orden_id>/', views.cambiar_estado_orden_aceptada, name='cambiar_estado_orden_aceptada'),
    path('eliminar_orden/<int:orden_id>/', views.eliminar_orden, name='eliminar_orden'),
    path('detalle_orden_de_compra_enviada/<int:orden_id>/', views.detalle_orden_de_compra_enviada, name='detalle_orden_de_compra_enviada'),
    path('detalle_orden_de_compra_aceptada/<int:orden_id>/', views.detalle_orden_de_compra_aceptada, name='detalle_orden_de_compra_aceptada'),
    path('detalle_orden_de_compra_rechazada/<int:orden_id>/', views.detalle_orden_de_compra_rechazada, name='detalle_orden_de_compra_rechazada'),
    path('detalle_orden_de_compra_anulada/<int:orden_id>/', views.detalle_orden_de_compra_anulada, name='detalle_orden_de_compra_anulada'),
    path('editar_orden/<int:orden_id>/', views.editar_orden, name='editar_orden'),
    path('get_chart_oc_1', views.get_chart_oc_1, name = 'get_chart_oc_1'),
    path('get_chart_oc_2', views.get_chart_oc_2, name = 'get_chart_oc_2'),
    
    
    #path('', views.listar_productos, name='listar_productos'),
    #path('agregar/', views.agregar_producto, name='agregar_producto'),
    #path('actualizar/<int:pk>/', views.actualizar_producto, name='actualizar_producto'),
    #path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    #path('proveedor_edit/<int:proveedor_id>/', views.proveedor_edit,name='proveedor_edit'),
    #path('proveedor_edit', views.proveedor_edit,name='proveedor_edit'),
]