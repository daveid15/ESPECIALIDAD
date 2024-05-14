from django.conf.urls import url, include
from django.urls import path
from inventario import views
from django.views.decorators.csrf import csrf_exempt

inventario_patterns = [
    
    #Productos
    path('inventario_main', views.inventario_main,name='inventario_main'),
    path('crear_producto/',views.crear_producto,name='crear_producto'),
    path('producto_save/',views.producto_save,name='producto_save'),
    path('carga_masiva_producto/',views.carga_masiva_producto,name="carga_masiva_producto"),
    path('carga_masiva_producto_save/',views.carga_masiva_producto_save,name="carga_masiva_producto_save"),
    path('import_file_producto/',views.import_file_producto,name="import_file_producto"),
    path('producto_ver/<product_id>/',views.producto_ver,name='producto_ver'),
    path('producto_edit/<int:product_id>/', views.producto_edit, name='producto_edit'),
    path('producto_list/',views.producto_list,name='producto_list'),
    path('descarga_reporte_producto/',views.descarga_reporte_producto,name="descarga_reporte_producto"),
    path('reportes_main_productos/',views.reportes_main_productos,name="reportes_main_productos"),
    path('reporte_producto_filtro/',views.reporte_producto_filtro,name="reporte_producto_filtro"),
    path('producto_delete/<int:product_id>/', views.producto_delete, name='producto_delete'),


    ]  
    
