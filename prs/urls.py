
from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    # Logins
    path('login/', login_view, name='login'),
    path('register/', registrar_view, name='register'),
    path('logout/', logout_usuario,name='logout'),
    path('force-password-reset/', force_password_reset, name='force_password_reset'),
    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    path('fechamento-turno/', fechamento_turno, name='fechamentoTurno'),
    path('carregamento/', carregamento, name='carregamento'),
    path('diario-bordo-lista/', diario_bordo_lista, name='diario-bordo-lista'),
    path('diario-bordo/', diarioBordo, name='diario-bordo'),
    path('finalizar-diario-bordo/<int:entrada_id>/', finalizar_diario_bordo, name='finalizar-diario-bordo'),
    path('agua-extrusoura/', aguaExtrusoura, name='agua-extrusoura'),
    path('fechamento-bag-pe/', fechamentoBag, name='fechamento-bag-pe'),
    path('inventario/', inventario, name='inventario'),
    path('plil/', plil, name='plil'),
    path('plil/criar-template/', plil_criar_template, name='plil_criar_template'),
    path('plil/atribuir-tarefa/', plil_atribuir_tarefa, name='plil_atribuir_tarefa'),
    path('plil/executar/<int:tarefa_id>/', plil_executar_tarefa, name='plil_executar_tarefa'),
    path('plil/remover/<int:tarefa_id>/', plil_remover_tarefa, name='plil_remover_tarefa'),
    path('plil/templates/', plil_templates, name='plil_templates'),
    path('plil/templates/editar/<int:template_id>/', plil_editar_template, name='plil_editar_template'),
    path('plil/templates/toggle/<int:template_id>/', plil_toggle_template, name='plil_toggle_template'),
    path('plil/templates/excluir/<int:template_id>/', plil_excluir_template, name='plil_excluir_template'),
    path('plil/templates/visualizar/<int:template_id>/', plil_visualizar_template, name='plil_visualizar_template'),
    path('etiqueta/', etiqueta, name='etiqueta'),
    path('relatorio-turno/', relatorioTurno, name='relatorioTurno'),
    path('relatorio-extrusoura/', relatorioExtrusoura, name='relatorioExtrusoura'),
    path('relatorio-carregamento/', relatorioCarregamento, name='relatorioCarregamento'),
    path('relatorio-plil/', relatorioPlil, name='relatorioPlil'),
    path('relatorio-etiquetas/', relatorioEtiquetas, name='relatorioEtiquetas'),
    path('relatorio-geral/', relatorioGeral, name='relatorioGeral'),
    path('conteudo-principal/', conteudoPrincipal, name='conteudoPrincipal'),
    path('cadastros-gerenciamento/', cadastrosGerenciamento, name='cadastrosGerenciamento'),
    path('configuracao/', configuracao, name='configuracao'),
    # Dashboard AJAX
    path('marcar-carregamento-concluido/<int:carregamento_id>/', marcar_carregamento_concluido, name='marcar_carregamento_concluido'),
    path('marcar-carregamento-cancelado/<int:carregamento_id>/', marcar_carregamento_cancelado, name='marcar_carregamento_cancelado'),
    # Exportação de Relatórios
    path('exportar-excel/<str:tipo_relatorio>/', exportar_relatorio_excel, name='exportar_relatorio_excel'),
    path('exportar-pdf/<str:tipo_relatorio>/', exportar_relatorio_pdf, name='exportar_relatorio_pdf'),
    # Exportação de Dados do Banco
    path('api/exportar-dados-banco/', exportar_dados_banco, name='exportar_dados_banco'),
    
]