from django.urls import path
from perguntas import admin
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('admin/criar-enquete/', views.criar_enquete, name='admin_criar_enquete'),
    path('enquetes/', views.gerenciar_enquetes, name='gerenciar_enquetes'),
    path('usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('usuarios/registrar/', views.registrar_aluno, name='registrar_aluno'),
    path('admin/criar-enquete/', views.criar_enquete, name='admin_criar_enquete'),
    path('areas-interesse/', views.listar_areas_interesse, name='listar_areas_interesse'),
    path('enquete/<int:enquete_id>/responder/', views.gerenciar_enquetes, name='responder_enquete'),
    path('enquete/<int:enquete_id>/resultados/', views.gerenciar_enquetes, name='exibir_resultados'),
]
