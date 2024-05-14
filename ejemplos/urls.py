from django.urls import path
from ejemplos import views #importará los métodos que generemos en nuestra app
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
ejemplos_urlpatterns = [
    path('ejemplos_main/',views.ejemplos_main,name="ejemplos_main"),
    path('ejemplos_habilidad_add/',views.ejemplos_habilidad_add,name="ejemplos_habilidad_add"),
    path('ejemplos_habilidad_save/',views.ejemplos_habilidad_save,name="ejemplos_habilidad_save"),
    path('ejemplos_habilidad_ver/<habilidad_id>/',views.ejemplos_habilidad_ver,name="ejemplos_habilidad_ver"),
    path('ejemplos_list_habilidades/',views.ejemplos_list_habilidades,name="ejemplos_list_habilidades"),
    path('ejemplos_carga_masiva/',views.ejemplos_carga_masiva,name="ejemplos_carga_masiva"),
    path('ejemplos_carga_masiva_save/',views.ejemplos_carga_masiva_save,name="ejemplos_carga_masiva_save"),
    path('import_file/',views.import_file,name="import_file"),
    #muchos a muchos
    path('ejemplos_autor_new/',views.ejemplos_autor_new,name="ejemplos_autor_new"),
    path('ejemplos_autor_save/',views.ejemplos_autor_save,name="ejemplos_autor_save"),
    path('ejemplos_autor_list/',views.ejemplos_autor_list,name="ejemplos_autor_list"),
    path('ejemplos_proyect_new/',views.ejemplos_proyect_new,name="ejemplos_proyect_new"),
    path('ejemplos_proyect_save/',views.ejemplos_proyect_save,name="ejemplos_proyect_save"),
    path('ejemplos_proyect_list/',views.ejemplos_proyect_list,name="ejemplos_proyect_list"),
    path('ejemplos_proyect_edit/<proyecto_id>/',views.ejemplos_proyect_edit,name="ejemplos_proyect_edit"),
    path('ejemplos_proyect_edit_save/',views.ejemplos_proyect_edit_save,name="ejemplos_proyect_edit_save"),
    #reportes
    path('reportes_main/',views.reportes_main,name="reportes_main"),
    path('reporte_todas_habilidades/',views.reporte_todas_habilidades,name="reporte_todas_habilidades"),
    path('reporte_habilidades_nombre/',views.reporte_habilidades_nombre,name="reporte_habilidades_nombre"),
    #ejemplos correos
    path('ejemplos_correo1/',views.ejemplos_correo1,name="ejemplos_correo1"),
    path('ejemplos_correo2/',views.ejemplos_correo2,name="ejemplos_correo2"),
    #ejemplos pdf
    path('lista_habilidades_pdf/',views.lista_habilidades_pdf,name="lista_habilidades_pdf"),
    #ejemplo dashboard
    path('ejemplos_dashboard/',views.ejemplos_dashboard,name="ejemplos_dashboard"),
    
    #endPoints
    path('ejemplos_habilidad_add_rest/', views.ejemplos_habilidad_add_rest),  
    path('ejemplos_habilidad_list_rest/', views.ejemplos_habilidad_list_rest),  
    path('ejemplos_habilidad_get_element_rest/', views.ejemplos_habilidad_get_element_rest),  
    path('ejemplos_habilidad_update_element_rest/', views.ejemplos_habilidad_update_element_rest), 
    path('ejemplos_habilidad_del_element_rest/', views.ejemplos_habilidad_del_element_rest), 
    path('ejemplos_habilidad_list_date_rest/', views.ejemplos_habilidad_list_date_rest), 
    path('ejemplos_habilidad_list_range_date_rest/', views.ejemplos_habilidad_list_range_date_rest), 
    path('ejemplos_habilidad_list_contains/', views.ejemplos_habilidad_list_contains), 

    path("product_list_rest/",views.product_list_rest),
    path("product_edit_rest/",views.product_edit_rest),
    path("product_add_rest/",views.product_add_rest),
    path("product_del_rest/",views.product_del_rest),
    
    path("provider_list_rest/",views.provider_list_rest),
    path("provider_edit_rest/",views.provider_edit_rest),
    path("provider_add_rest/",views.provider_add_rest),
    path("provider_del_rest/",views.provider_del_rest),

    path("category_list_rest/",views.category_list_rest),
    path("category_edit_rest/",views.category_edit_rest),
    path("category_add_rest/",views.category_add_rest),
    path("category_del_rest/",views.category_del_rest),

    ]

    