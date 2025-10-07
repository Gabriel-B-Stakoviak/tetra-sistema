from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *

# ================================================================================
class CarrosselImagemAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ordem', 'ativo', 'data_criacao', 'criado_por']
    list_filter = ['ativo', 'ordem', 'data_criacao']
    search_fields = ['titulo', 'descricao']
    ordering = ['ordem', 'data_criacao']
    readonly_fields = ['data_criacao', 'criado_por']
    
    fieldsets = (
        ('Informações da Imagem', {
            'fields': ('titulo', 'imagem', 'descricao')
        }),
        ('Configurações', {
            'fields': ('ordem', 'ativo')
        }),
        ('Informações do Sistema', {
            'fields': ('data_criacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
    
    def has_module_permission(self, request):
        """Apenas administrador, gerente e administrativo podem acessar"""
        if hasattr(request.user, 'perfil'):
            return request.user.perfil.cargo in ['administrador', 'gerente', 'administrativo']
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Apenas administrador, gerente e administrativo podem adicionar"""
        if hasattr(request.user, 'perfil'):
            return request.user.perfil.cargo in ['administrador', 'gerente', 'administrativo']
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Apenas administrador, gerente e administrativo podem editar"""
        if hasattr(request.user, 'perfil'):
            return request.user.perfil.cargo in ['administrador', 'gerente', 'administrativo']
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Apenas administrador e gerente podem deletar"""
        if hasattr(request.user, 'perfil'):
            return request.user.perfil.cargo in ['administrador', 'gerente']
        return request.user.is_superuser

# ================================================================================
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['nome', 're', 'cargo', 'ativo', 'data_criacao']
    list_filter = ['cargo', 'ativo', 'data_criacao']
    search_fields = ['nome', 're']
    ordering = ['nome']

# ================================================================================
# Registrar os modelos
admin.site.register(Perfil, PerfilAdmin)
admin.site.register(CarrosselImagem, CarrosselImagemAdmin)
admin.site.register(FechamentoTurno)
admin.site.register(DiarioBordo)
admin.site.register(AguaCloro)
admin.site.register(FechamentoBag)
admin.site.register(Inventario)
admin.site.register(Carregamento)
admin.site.register(Plil)
admin.site.register(Etiqueta)
admin.site.register(RelatorioTurno)
admin.site.register(RelatorioExtrusoura)
admin.site.register(RelatorioInventario)
admin.site.register(RelatorioCarregamento)
admin.site.register(RelatorioPlil)
admin.site.register(RelatorioEtiqueta)
admin.site.register(RelatorioGeral)
admin.site.register(ConteudoPrincipal)
admin.site.register(Cadastro)
