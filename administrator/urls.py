
from django.conf.urls import url, include
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from administrator import views
from proveedores import views as proveedores_views
from inventario import views as inventario_views

administrator_patterns = [
    path('admin_main', views.admin_main,name="admin_main"),
    path('proveedores_main', proveedores_views.proveedores_main,name="proveedores_main"),
    path('orden_main', proveedores_views.orden_main,name="orden_main"),
    #flujo usuarios
    path('perfil_main', views.perfil_main,name="perfil_main"),
    path('users_main', views.users_main,name="users_main"),
    path('new_user/',views.new_user, name='new_user'),
    path('user_block/<user_id>/',views.user_block, name='user_block'),
    path('user_activate/<user_id>',views.user_activate, name='user_activate'),
    path('user_delete/<user_id>',views.user_delete, name='user_delete'),
    path('edit_user/<user_id>/',views.edit_user, name='edit_user'),
    path('edit_perfil',views.edit_perfil, name='edit_perfil'),
    path('list_main/<group_id>/',views.list_main, name='list_main'),     
    path('list_user_active/<group_id>/',views.list_user_active, name='list_user_active'),     
    path('list_user_active/<group_id>/<page>/',views.list_user_active, name='list_user_active'),     
    path('list_user_block/<group_id>/',views.list_user_block, name='list_user_block'),     
    path('list_user_block/<group_id>/<page>/',views.list_user_block, name='list_user_block'),  
    path('new_group/', views.new_group, name='new_group'),
    path('user/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('administrator/user/list/', views.list_users, name='list_users'),
    path('carga_masiva_user/',views.carga_masiva_user,name="carga_masiva_user"),

    path('carga_masiva_user_save/',views.carga_masiva_user_save,name="carga_masiva_user_save"),
    path('import_file_user/',views.import_file_user,name="import_file_user"),
    
    #BORRAR
    path('ejemplo_query_set/',views.ejemplo_query_set, name='ejemplo_query_set'),  
    ]  
