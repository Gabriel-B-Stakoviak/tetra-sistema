from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .forms import RegistroForm, FechamentoTurnoForm, DiarioBordoForm, AguaCloroForm, EditarPerfilForm, ForcePasswordResetForm, CarregamentoForm, EmpresaForm, TarefaTemplateForm, AtribuirTarefaForm, ExecutarTarefaForm
from django.shortcuts import get_list_or_404
from .models import *
from datetime import datetime, time, timedelta
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Count, Avg, Q, Max
import io
import json
import xlsxwriter
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import json

# Create your views here.
def home(request):
    # Buscar imagens ativas do carrossel ordenadas por ordem
    imagens_carrossel = CarrosselImagem.objects.filter(ativo=True).order_by('ordem', 'data_criacao')[:5]
    
    context = {
        'imagens_carrossel': imagens_carrossel,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# Logins e Registro
def registrar_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('login')
            except Exception as e:
                form.add_error(None, f'Erro ao criar usuário: {str(e)}')
    else:
        form = RegistroForm()
    return render(request, 'login/register_view.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            return render(request, 'login/login_view.html', {
                'error': 'Por favor, preencha todos os campos.'
            })

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                try:
                    perfil = user.perfil
                    if perfil.ativo:
                        # Verificar se o usuário precisa redefinir a senha
                        if perfil.force_password_reset:
                            # Fazer login temporário para permitir redefinição
                            login(request, user)
                            return redirect('force_password_reset')
                        else:
                            login(request, user)
                            return redirect('dashboard')
                    else:
                        return render(request, 'login/login_view.html', {
                            'error': 'Sua conta ainda não foi ativada por um gerente ou administrador. Entre em contato com a administração.'
                        })
                except Perfil.DoesNotExist:
                    return render(request, 'login/login_view.html', {
                        'error': 'Perfil não encontrado. Entre em contato com o administrador.'
                    })
            else:
                return render(request, 'login/login_view.html', {
                    'error': 'Sua conta está desativada. Entre em contato com o administrador.'
                })
        else:
            return render(request, 'login/login_view.html', {
                'error': 'Usuário ou senha inválidos.'
            })

    return render(request, 'login/login_view.html')

@login_required
def force_password_reset(request):
    try:
        perfil = request.user.perfil
        
        # Verificar se realmente precisa redefinir a senha
        if not perfil.force_password_reset:
            return redirect('dashboard')
            
        if request.method == 'POST':
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')
            
            if not nova_senha or not confirmar_senha:
                return render(request, 'login/force_password_reset.html', {
                    'error': 'Por favor, preencha todos os campos.',
                    'perfil': perfil
                })
            
            if nova_senha != confirmar_senha:
                return render(request, 'login/force_password_reset.html', {
                    'error': 'As senhas não coincidem.',
                    'perfil': perfil
                })
            
            if len(nova_senha) < 8:
                return render(request, 'login/force_password_reset.html', {
                    'error': 'A senha deve ter pelo menos 8 caracteres.',
                    'perfil': perfil
                })
            
            # Atualizar a senha e remover a flag de força reset
            request.user.set_password(nova_senha)
            request.user.save()
            perfil.force_password_reset = False
            perfil.save()
            
            return redirect('dashboard')
            
    except Perfil.DoesNotExist:
        return redirect('register')
    
    return render(request, 'login/force_password_reset.html', {'perfil': perfil})

@login_required
def dashboard(request):
    try:
        perfil = request.user.perfil
        
        # Verificar se o usuário precisa redefinir a senha
        if perfil.force_password_reset:
            return redirect('force_password_reset')
            
    except Perfil.DoesNotExist:
        # Se o usuário não tem perfil, redireciona para criar um
        return redirect('register')
    
    # Buscar totais de fardo por turno
    turno1_total = FechamentoTurno.objects.filter(turno='A').aggregate(
        total=Sum('total_fardo')
    )['total'] or 0
    
    turno2_total = FechamentoTurno.objects.filter(turno='B').aggregate(
        total=Sum('total_fardo')
    )['total'] or 0
    
    turno3_total = FechamentoTurno.objects.filter(turno='C').aggregate(
        total=Sum('total_fardo')
    )['total'] or 0
    
    # Buscar totais de reversão por turno
    turno1_reversao = FechamentoTurno.objects.filter(turno='A').aggregate(
        total=Sum('reversao')
    )['total'] or 0
    
    turno2_reversao = FechamentoTurno.objects.filter(turno='B').aggregate(
        total=Sum('reversao')
    )['total'] or 0
    
    turno3_reversao = FechamentoTurno.objects.filter(turno='C').aggregate(
        total=Sum('reversao')
    )['total'] or 0
 
    # Calcular totais gerais (soma de todos os turnos)
    total_geral_fardos = turno1_total + turno2_total + turno3_total
    total_geral_reversao = turno1_reversao + turno2_reversao + turno3_reversao
    
    # Buscar carregamentos recentes (últimos 10)
    carregamentos = CarregamentoDashboard.objects.select_related('empresa', 'criado_por').order_by('-data_criacao')[:10]
    
    context = {
        'perfil': perfil,
        'turno1_total': turno1_total,
        'turno2_total': turno2_total,
        'turno3_total': turno3_total,
        'turno1_reversao': turno1_reversao,
        'turno2_reversao': turno2_reversao,
        'turno3_reversao': turno3_reversao,
        'total_geral_fardos': total_geral_fardos,
        'total_geral_reversao': total_geral_reversao,
        'carregamentos': carregamentos,
    }
    
    return render(request, 'login/dashboard/dashboard.html', context)

@login_required
def marcar_carregamento_concluido(request, carregamento_id):
    """View para marcar carregamento como concluído via AJAX"""
    if request.method == 'POST':
        try:
            carregamento = get_object_or_404(CarregamentoDashboard, id=carregamento_id)
            carregamento.marcar_concluido(request.user)
            return JsonResponse({
                'success': True,
                'message': 'Carregamento marcado como concluído!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao marcar carregamento: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

def marcar_carregamento_cancelado(request, carregamento_id):
    """View para marcar carregamento como cancelado via AJAX"""
    if request.method == 'POST':
        try:
            carregamento = get_object_or_404(CarregamentoDashboard, id=carregamento_id)
            carregamento.marcar_cancelado(request.user)
            return JsonResponse({
                'success': True,
                'message': 'Carregamento cancelado com sucesso!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao cancelar carregamento: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

######################################################################
def detectar_turno_atual():
    """
    Detecta o turno atual baseado no horário:
    Turno A: 06:15 às 14:15
    Turno B: 14:15 às 22:20  
    Turno C: 22:20 às 06:15
    """
    agora = timezone.localtime(timezone.now()).time()
    
    # Turno A: 06:15 às 14:15
    if time(6, 15) <= agora < time(14, 15):
        return 'A'
    # Turno B: 14:15 às 22:20
    elif time(14, 15) <= agora < time(22, 20):
        return 'B'
    # Turno C: 22:20 às 06:15 (atravessa meia-noite)
    else:
        return 'C'

@login_required
def fechamento_turno(request):
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, 'Usuário sem perfil cadastrado.')
        return redirect('dashboard')
    
    turno_atual = detectar_turno_atual()
    agora_local = timezone.localtime(timezone.now())
    
    if request.method == 'POST':
        form = FechamentoTurnoForm(request.POST)
        if form.is_valid():
            fechamento = form.save(commit=False)
            fechamento.re = perfil.re
            fechamento.nome = perfil.nome
            fechamento.turno = turno_atual
            fechamento.save()
            
            return redirect('dashboard')
    else:
        form = FechamentoTurnoForm()
    
    context = {
        'form': form,
        'perfil': perfil,
        'turno_atual': turno_atual,
        'horario_atual': agora_local.strftime('%H:%M'),
    }
    
    return render(request, 'login/dashboard/fechamento_turno.html', context)
        
@login_required
def carregamento(request):
    perfil = request.user.perfil
    
    # Processar formulário de carregamento
    if request.method == 'POST':
        form_carregamento = CarregamentoForm(request.POST)
        if form_carregamento.is_valid():
            nome_empresa = form_carregamento.cleaned_data['empresa'].strip()
            material = form_carregamento.cleaned_data['material']
            
            # Buscar ou criar a empresa
            empresa, created = Empresa.objects.get_or_create(
                nome__iexact=nome_empresa,  # Busca case-insensitive
                defaults={
                    'nome': nome_empresa,
                    'criado_por': request.user,
                    'ativo': True
                }
            )
            
            # Criar o carregamento
            carregamento = CarregamentoDashboard.objects.create(
                empresa=empresa,
                material=material,
                criado_por=request.user
            )
            
            return redirect('carregamento')
    
    # Formulário vazio para GET
    form_carregamento = CarregamentoForm()
    
    # Buscar registros de carregamento
    carregamentos = CarregamentoDashboard.objects.all().order_by('-data_criacao')
    
    context = {
        'perfil': perfil,
        'form_carregamento': form_carregamento,
        'carregamentos': carregamentos,
    }
    
    return render(request, 'login/dashboard/carregamento.html', context)

@login_required
def diario_bordo_lista(request):
    """View para listar todos os registros do Diário de Bordo"""
    perfil = request.user.perfil
    registros = DiarioBordo.objects.all().order_by('-data_criacao', '-data', '-turno')
    
    context = {
        'perfil': perfil,
        'registros': registros
    }
    return render(request, 'login/dashboard/extrusoura_lista/diario_bordo_lista.html', context)

@login_required
def diarioBordo(request):
    perfil = request.user.perfil
    turno_atual = detectar_turno_atual()
    
    if request.method == 'POST':
        form = DiarioBordoForm(request.POST)
        if form.is_valid():
            entrada = form.save(commit=False)
            # Garantir que os dados automáticos sejam preenchidos
            agora_local = timezone.localtime(timezone.now())
            entrada.re = perfil.re
            entrada.data = agora_local.date()
            entrada.turno = turno_atual
            entrada.inicio = agora_local
            entrada.save()
            return redirect('diario-bordo-lista')
    else:
        form = DiarioBordoForm()
    
    agora_utc = timezone.now()
    agora_local = timezone.localtime(agora_utc)
    context = {
         'perfil': perfil,
         'form': form,
         'turno_atual': turno_atual,
         'data_atual': agora_local.strftime('%d/%m/%Y'),
         'horario_atual': agora_local.strftime('%H:%M')
     }
    return render(request, 'login/dashboard/extrusoura_lista/diario_bordo.html', context)

@login_required
def finalizar_diario_bordo(request, entrada_id):
    if request.method == 'POST':
        entrada = get_object_or_404(DiarioBordo, id=entrada_id)
        agora_utc = timezone.now()
        agora_local = timezone.localtime(agora_utc)
        entrada.fim = agora_utc  # Salva em UTC no banco
        entrada.save()
        return JsonResponse({
            'success': True,
            'fim': agora_local.strftime('%d/%m/%Y %H:%M'),  # Retorna em horário local
            'fim_formatado': agora_local.strftime('%H:%M')  # Retorna em horário local
        })
    return JsonResponse({'success': False})

@login_required
def aguaExtrusoura(request):
    perfil = request.user.perfil
    
    if request.method == 'POST':
        form = AguaCloroForm(request.POST)
        if form.is_valid():
            agua_cloro = form.save(commit=False)
            
            # Preencher campos automáticos
            agua_cloro.re = perfil.re
            agua_cloro.turno = detectar_turno_atual()
            
            agua_cloro.save()
            return redirect('agua-extrusoura')
    else:
        form = AguaCloroForm()
    
    # Dados para exibição automática
    agora_local = timezone.localtime(timezone.now())
    data_atual = agora_local.strftime('%d/%m/%Y')
    horario_atual = agora_local.strftime('%H:%M')
    turno_atual = detectar_turno_atual()
    
    context = {
        'perfil': perfil,
        'form': form,
        'data_atual': data_atual,
        'horario_atual': horario_atual,
        'turno_atual': turno_atual,
        're_atual': perfil.re
    }
    
    return render(request, 'login/dashboard/extrusoura_lista/agua_extrusoura.html', context)

@login_required
def fechamentoBag(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/extrusoura_lista/fechamento_bag-pe.html', {'perfil': perfil})

@login_required
def inventario(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/inventario.html', {'perfil': perfil})

@login_required
def plil(request):
    perfil = request.user.perfil
    
    # Buscar tarefas do usuário atual
    minhas_tarefas = Plil.objects.filter(re_responsavel=perfil.re).order_by('data_prevista')
    
    # Se for admin/gerente/administrativo, buscar todas as tarefas
    todas_tarefas = None
    if perfil.cargo in ['administrador', 'gerente', 'administrativo']:
        todas_tarefas = Plil.objects.all().order_by('-data_atribuicao')
    
    # Formulários
    form_template = TarefaTemplateForm()
    form_atribuir = AtribuirTarefaForm()
    form_executar = ExecutarTarefaForm()
    
    context = {
        'perfil': perfil,
        'minhas_tarefas': minhas_tarefas,
        'todas_tarefas': todas_tarefas,
        'form_template': form_template,
        'form_atribuir': form_atribuir,
        'form_executar': form_executar,
    }
    
    return render(request, 'login/dashboard/plil.html', context)

@login_required
def plil_criar_template(request):
    """View para criar novos templates de tarefa"""
    perfil = request.user.perfil
    
    # Verificar permissão
    if perfil.cargo not in ['administrador', 'gerente', 'administrativo']:
        messages.error(request, 'Você não tem permissão para criar templates de tarefa.')
        return redirect('plil')
    
    if request.method == 'POST':
        form = TarefaTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.criado_por = request.user
            template.save()
            # messages.success(request, 'Template de tarefa criado com sucesso!')
        else:
            messages.error(request, 'Erro ao criar template. Verifique os dados informados.')
    
    return redirect('plil')

@login_required
def plil_atribuir_tarefa(request):
    """View para atribuir tarefas a funcionários"""
    perfil = request.user.perfil
    
    # Verificar permissão
    if perfil.cargo not in ['administrador', 'gerente', 'administrativo']:
        messages.error(request, 'Você não tem permissão para atribuir tarefas.')
        return redirect('plil')
    
    if request.method == 'POST':
        form = AtribuirTarefaForm(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.atribuida_por = request.user
            
            # Buscar o nome do responsável pelo RE
            try:
                perfil_responsavel = Perfil.objects.get(re=tarefa.re_responsavel)
                tarefa.nome_responsavel = perfil_responsavel.nome
            except Perfil.DoesNotExist:
                tarefa.nome_responsavel = f"RE {tarefa.re_responsavel}"
            
            tarefa.save()
            # messages.success(request, f'Tarefa atribuída com sucesso para {tarefa.nome_responsavel}!')
        else:
            messages.error(request, 'Erro ao atribuir tarefa. Verifique os dados informados.')
    
    return redirect('plil')

@login_required
def plil_executar_tarefa(request, tarefa_id):
    """View para marcar tarefa como executada"""
    tarefa = get_object_or_404(Plil, id=tarefa_id)
    perfil = request.user.perfil
    
    # Verificar se o usuário pode executar esta tarefa
    if tarefa.re_responsavel != perfil.re:
        messages.error(request, 'Você não tem permissão para executar esta tarefa.')
        return redirect('plil')
    
    if request.method == 'POST':
        form = ExecutarTarefaForm(request.POST)
        if form.is_valid():
            tarefa.status = 'executada'
            tarefa.data_execucao = timezone.now()
            tarefa.observacoes_execucao = form.cleaned_data['observacoes_execucao']
            tarefa.save()
            # messages.success(request, 'Tarefa marcada como executada!')
        else:
            messages.error(request, 'Erro ao executar tarefa.')
    
    return redirect('plil')

@login_required
def plil_remover_tarefa(request, tarefa_id):
    """View para remover tarefa"""
    tarefa = get_object_or_404(Plil, id=tarefa_id)
    perfil = request.user.perfil
    
    # Verificar permissão
    if perfil.cargo not in ['administrador', 'gerente', 'administrativo']:
        messages.error(request, 'Você não tem permissão para remover tarefas.')
        return redirect('plil')
    
    tarefa.delete()
    # messages.success(request, 'Tarefa removida com sucesso!')
    return redirect('plil')

@login_required
def plil_templates(request):
    """View para gerenciar templates de tarefa"""
    perfil = request.user.perfil
    
    # Verificar permissão
    if perfil.cargo not in ['administrador', 'gerente', 'administrativo']:
        messages.error(request, 'Você não tem permissão para gerenciar templates.')
        return redirect('plil')
    
    # Buscar todos os templates com contagem de tarefas ativas
    from django.db.models import Count, Q
    templates = TarefaTemplate.objects.select_related('criado_por').annotate(
        tarefas_ativas=Count('plil', filter=Q(plil__status__in=['pendente', 'atrasada']))
    ).order_by('-data_criacao')
    
    context = {
        'perfil': perfil,
        'templates': templates,
    }
    
    return render(request, 'login/dashboard/plil_templates.html', context)

@login_required
def plil_editar_template(request, template_id):
    """View para editar template de tarefa"""
    template = get_object_or_404(TarefaTemplate, id=template_id)
    perfil = request.user.perfil
    
    # Verificar permissão
    if perfil.cargo not in ['administrador', 'gerente', 'administrativo']:
        messages.error(request, 'Você não tem permissão para editar templates.')
        return redirect('plil_templates')
    
    if request.method == 'POST':
        form = TarefaTemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Template atualizado com sucesso!'})
        else:
            return JsonResponse({
                'success': False,
                'html': render_to_string('login/dashboard/plil_editar_template_form.html', {
                    'form': form,
                    'template': template
                })
            })
    else:
        form = TarefaTemplateForm(instance=template)
    
    return JsonResponse({
        'html': render_to_string('login/dashboard/plil_editar_template_form.html', {
            'form': form,
            'template': template
        })
    })

@login_required
def plil_toggle_template(request, template_id):
    """View para ativar/desativar template"""
    template = get_object_or_404(TarefaTemplate, id=template_id)
    perfil = request.user.perfil
    
    # Verificar permissão
    if perfil.cargo not in ['administrador', 'gerente', 'administrativo']:
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    template.ativo = not template.ativo
    template.save()
    
    status = 'ativado' if template.ativo else 'desativado'
    return JsonResponse({
        'success': True, 
        'message': f'Template {status} com sucesso!',
        'ativo': template.ativo
    })

@login_required
def plil_excluir_template(request, template_id):
    """View para excluir template"""
    template = get_object_or_404(TarefaTemplate, id=template_id)
    perfil = request.user.perfil
    
    # Verificar permissão
    if perfil.cargo not in ['administrador', 'gerente', 'administrativo']:
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    # Verificar se há tarefas associadas
    if template.plil_set.exists():
        return JsonResponse({
            'success': False, 
            'message': 'Não é possível excluir template com tarefas associadas'
        })
    
    template.delete()
    return JsonResponse({'success': True, 'message': 'Template excluído com sucesso!'})

@login_required
def plil_visualizar_template(request, template_id):
    """View para visualizar detalhes do template"""
    template = get_object_or_404(TarefaTemplate, id=template_id)
    perfil = request.user.perfil
    
    # Verificar permissão
    if perfil.cargo not in ['administrador', 'gerente', 'administrativo']:
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    # Estatísticas do template
    tarefas = template.plil_set.all()
    stats = {
        'total_tarefas': tarefas.count(),
        'pendentes': tarefas.filter(status='pendente').count(),
        'executadas': tarefas.filter(status='executada').count(),
        'atrasadas': tarefas.filter(status='atrasada').count(),
    }
    
    return JsonResponse({
        'html': render_to_string('login/dashboard/plil_visualizar_template.html', {
            'template': template,
            'stats': stats,
            'tarefas_recentes': tarefas.order_by('-data_atribuicao')[:10]
        })
    })

@login_required
def etiqueta(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/etiqueta.html', {'perfil': perfil})

@login_required
def relatorioTurno(request):
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg, Q
    
    perfil = request.user.perfil
    
    # Filtros de data
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    turno_filtro = request.GET.get('turno')
    
    # Definir período padrão (últimos 30 dias)
    if not data_inicio:
        data_inicio = (timezone.now() - timedelta(days=30)).date()
    else:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    
    if not data_fim:
        data_fim = timezone.now().date()
    else:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    
    # Buscar dados de fechamento de turno
    fechamentos = FechamentoTurno.objects.filter(
        data_hora__date__range=[data_inicio, data_fim]
    )
    
    if turno_filtro:
        fechamentos = fechamentos.filter(turno=turno_filtro)
    
    # Estatísticas
    total_fechamentos = fechamentos.count()
    total_fardos = fechamentos.aggregate(Sum('total_fardo'))['total_fardo__sum'] or 0
    total_reversao = fechamentos.aggregate(Sum('reversao'))['reversao__sum'] or 0
    media_fardos = fechamentos.aggregate(Avg('total_fardo'))['total_fardo__avg'] or 0
    
    # Dados para gráficos
    fechamentos_por_turno = fechamentos.values('turno').annotate(
        total=Count('id'),
        fardos=Sum('total_fardo')
    ).order_by('turno')
    
    # Evolução diária
    evolucao_diaria = fechamentos.extra(
        select={'dia': 'date(data_hora)'}
    ).values('dia').annotate(
        total_fardos=Sum('total_fardo'),
        total_fechamentos=Count('id')
    ).order_by('dia')
    
    # Resumo por turno
    resumo_turnos = []
    for turno in ['A', 'B', 'C']:
        turno_fechamentos = fechamentos.filter(turno=turno)
        total_turno = turno_fechamentos.aggregate(Sum('total_fardo'))['total_fardo__sum'] or 0
        reversao_turno = turno_fechamentos.aggregate(Sum('reversao'))['reversao__sum'] or 0
        
        resumo_turnos.append({
            'turno': turno,
            'total_fardos': total_turno,
            'total_reversao': reversao_turno
        })
    
    context = {
        'perfil': perfil,
        'dados_turno': fechamentos.order_by('-data_hora'),
        'total_fechamentos': total_fechamentos,
        'total_fardos': total_fardos,
        'total_reversao': total_reversao,
        'media_fardos': round(media_fardos, 2),
        'fechamentos_por_turno': fechamentos_por_turno,
        'evolucao_diaria': evolucao_diaria,
        'resumo_turnos': resumo_turnos,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'turno_filtro': turno_filtro,
    }
    
    return render(request, 'login/dashboard/relatorio/relatorio_turno.html', context)

@login_required
def relatorioExtrusoura(request):
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg, Q
    
    perfil = request.user.perfil
    
    # Filtros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    turno_filtro = request.GET.get('turno')
    status_filtro = request.GET.get('status')
    
    # Definir período padrão (últimos 30 dias)
    if not data_inicio:
        data_inicio = (timezone.now() - timedelta(days=30)).date()
    else:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    
    if not data_fim:
        data_fim = timezone.now().date()
    else:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    
    # Buscar dados do diário de bordo
    registros = DiarioBordo.objects.filter(
        data_criacao__date__range=[data_inicio, data_fim]
    )
    
    if turno_filtro:
        registros = registros.filter(turno=turno_filtro)
    
    if status_filtro:
        if status_filtro == 'finalizado':
            registros = registros.filter(fim__isnull=False)
        elif status_filtro == 'em_andamento':
            registros = registros.filter(fim__isnull=True)
    
    # Estatísticas
    total_registros = registros.count()
    # Registros finalizados que NÃO são máquina parada
    registros_finalizados = registros.filter(fim__isnull=False, maquina_parada=False).count()
    registros_em_andamento = registros.filter(fim__isnull=True).count()
    
    # Calcular tempos médios separados
    registros_com_tempo = registros.filter(fim__isnull=False, inicio__isnull=False)
    
    # Tempo médio para registros COM máquina parada
    registros_maquina_parada_tempo = registros_com_tempo.filter(maquina_parada=True)
    tempo_medio_maquina_parada = 0
    if registros_maquina_parada_tempo.exists():
        tempos_parada = []
        for registro in registros_maquina_parada_tempo:
            if registro.inicio and registro.fim:
                tempo_minutos = (registro.fim - registro.inicio).total_seconds() / 60
                tempos_parada.append(tempo_minutos)
        if tempos_parada:
            tempo_medio_maquina_parada = sum(tempos_parada) / len(tempos_parada)
    
    # Tempo médio para registros SEM máquina parada
    registros_sem_maquina_parada_tempo = registros_com_tempo.filter(maquina_parada=False)
    tempo_medio_sem_maquina_parada = 0
    if registros_sem_maquina_parada_tempo.exists():
        tempos_normal = []
        for registro in registros_sem_maquina_parada_tempo:
            if registro.inicio and registro.fim:
                tempo_minutos = (registro.fim - registro.inicio).total_seconds() / 60
                tempos_normal.append(tempo_minutos)
        if tempos_normal:
            tempo_medio_sem_maquina_parada = sum(tempos_normal) / len(tempos_normal)
    
    # Tempo médio geral (para compatibilidade)
    tempo_medio = 0
    if registros_com_tempo.exists():
        tempos = []
        for registro in registros_com_tempo:
            if registro.inicio and registro.fim:
                tempo_minutos = (registro.fim - registro.inicio).total_seconds() / 60
                tempos.append(tempo_minutos)
        if tempos:
            tempo_medio = sum(tempos) / len(tempos)
    
    # Dados para gráficos
    registros_por_turno = registros.values('turno').annotate(
        total=Count('id'),
        finalizados=Count('id', filter=Q(fim__isnull=False, maquina_parada=False))
    ).order_by('turno')
    
    # Estatísticas de máquina parada
    registros_maquina_parada = registros.filter(maquina_parada=True)
    total_maquina_parada = registros_maquina_parada.count()
    
    # Taxa de conclusão (% de registros finalizados vs total)
    taxa_conclusao = 0
    if total_registros > 0:
        taxa_conclusao = (registros_finalizados / total_registros) * 100
    
    # Aproveitamento da máquina (% tempo funcionando vs tempo total)
    aproveitamento_maquina = 0
    if total_registros > 0:
        registros_funcionando = total_registros - total_maquina_parada
        aproveitamento_maquina = (registros_funcionando / total_registros) * 100
    
    # Resumo por turnos incluindo máquina parada
    resumo_turnos = []
    for turno in ['A', 'B', 'C']:
        registros_turno = registros.filter(turno=turno)
        # Finalizados que NÃO são máquina parada
        finalizados_turno = registros_turno.filter(fim__isnull=False, maquina_parada=False).count()
        maquina_parada_turno = registros_turno.filter(maquina_parada=True).count()
        
        resumo_turnos.append({
            'turno': turno,
            'total_registros': registros_turno.count(),
            'finalizados': finalizados_turno,
            'maquina_parada': maquina_parada_turno
        })
    
    context = {
        'perfil': perfil,
        'dados_extrusora': registros.order_by('-data_criacao'),
        'total_registros': total_registros,
        'registros_finalizados': registros_finalizados,
        'registros_em_andamento': registros_em_andamento,
        'tempo_medio': round(tempo_medio, 2),
        'tempo_medio_maquina_parada': round(tempo_medio_maquina_parada / 60, 2),  # Converter para horas
        'tempo_medio_sem_maquina_parada': round(tempo_medio_sem_maquina_parada / 60, 2),  # Converter para horas
        'registros_por_turno': registros_por_turno,
        'registros_em_andamento_detalhes': registros.filter(fim__isnull=True),
        'total_maquina_parada': total_maquina_parada,
        'resumo_turnos': resumo_turnos,
        'taxa_conclusao': round(taxa_conclusao, 1),
        'aproveitamento_maquina': round(aproveitamento_maquina, 1),
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'turno_filtro': turno_filtro,
        'status_filtro': status_filtro,
    }
    
    return render(request, 'login/dashboard/relatorio/relatorio_extrusoura.html', context)

@login_required
def relatorioCarregamento(request):
    from datetime import datetime, timedelta
    from django.db.models import Count, Q
    
    perfil = request.user.perfil
    
    # Filtros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    empresa_filtro = request.GET.get('empresa')
    status_filtro = request.GET.get('status')
    
    # Definir período padrão (últimos 30 dias)
    if not data_inicio:
        data_inicio = (timezone.now() - timedelta(days=30)).date()
    else:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    
    if not data_fim:
        data_fim = timezone.now().date()
    else:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    
    # Buscar dados de carregamento
    carregamentos = CarregamentoDashboard.objects.filter(
        data_criacao__date__range=[data_inicio, data_fim]
    )
    
    if empresa_filtro:
        carregamentos = carregamentos.filter(empresa_id=empresa_filtro)
    
    if status_filtro:
        if status_filtro == 'concluido':
            carregamentos = carregamentos.filter(status='concluido')
        elif status_filtro == 'pendente':
            carregamentos = carregamentos.filter(status='pendente')
        elif status_filtro == 'cancelado':
            carregamentos = carregamentos.filter(status='cancelado')
    
    # Estatísticas
    total_carregamentos = carregamentos.count()
    carregamentos_concluidos = carregamentos.filter(status='concluido').count()
    carregamentos_pendentes = carregamentos.filter(status='pendente').count()
    carregamentos_cancelados = carregamentos.filter(status='cancelado').count()
    
    # Empresas únicas
    empresas = Empresa.objects.all()
    total_empresas = carregamentos.values('empresa').distinct().count()
    
    # Resumo por empresa
    resumo_empresas = carregamentos.values('empresa__nome').annotate(
        total=Count('id'),
        concluidos=Count('id', filter=Q(status='concluido')),
        pendentes=Count('id', filter=Q(status='pendente')),
        cancelados=Count('id', filter=Q(status='cancelado')),
        ultimo_carregamento=Max('data_criacao')
    ).order_by('-total')
    
    # Carregamentos pendentes em destaque
    carregamentos_pendentes_detalhes = carregamentos.filter(status='pendente').order_by('data_criacao')[:6]
    
    context = {
        'perfil': perfil,
        'dados_carregamento': carregamentos.order_by('-data_criacao'),
        'total_carregamentos': total_carregamentos,
        'carregamentos_concluidos': carregamentos_concluidos,
        'carregamentos_pendentes': carregamentos_pendentes,
        'carregamentos_cancelados': carregamentos_cancelados,
        'total_empresas': total_empresas,
        'empresas': empresas,
        'resumo_empresas': resumo_empresas,
        'carregamentos_pendentes_detalhes': carregamentos_pendentes_detalhes,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'empresa_filtro': empresa_filtro,
        'status_filtro': status_filtro,
    }
    
    return render(request, 'login/dashboard/relatorio/relatorio_carregamento.html', context)

@login_required
def relatorioPlil(request):
    context = {
        'titulo_relatorio': 'Relatório PLIL'
    }
    return render(request, 'login/dashboard/relatorio/em_desenvolvimento.html', context)

@login_required
def relatorioEtiquetas(request):
    context = {
        'titulo_relatorio': 'Relatório de Etiquetas'
    }
    return render(request, 'login/dashboard/relatorio/em_desenvolvimento.html', context)

@login_required
def relatorioGeral(request):
    context = {
        'titulo_relatorio': 'Relatório Geral'
    }
    return render(request, 'login/dashboard/relatorio/em_desenvolvimento.html', context)

@login_required
def conteudoPrincipal(request):
    perfil = request.user.perfil
    
    # Verificar se o usuário tem permissão (administrativo, gerente ou administrador)
    if perfil.cargo not in ['administrativo', 'gerente', 'administrador']:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_ativo':
            # Ativar/Desativar imagem
            imagem_id = request.POST.get('imagem_id')
            try:
                imagem = CarrosselImagem.objects.get(id=imagem_id)
                imagem.ativo = not imagem.ativo
                imagem.save()
                status = 'ativada' if imagem.ativo else 'desativada'
            except CarrosselImagem.DoesNotExist:
                messages.error(request, 'Imagem não encontrada.')
                
        elif action == 'excluir':
            # Excluir imagem
            imagem_id = request.POST.get('imagem_id')
            try:
                imagem = CarrosselImagem.objects.get(id=imagem_id)
                imagem.delete()
            except CarrosselImagem.DoesNotExist:
                messages.error(request, 'Imagem não encontrada.')
                
        else:
            # Adicionar nova imagem
            titulo = request.POST.get('titulo', '')
            descricao = request.POST.get('descricao', '')
            ordem = request.POST.get('ordem')
            imagem = request.FILES.get('imagem')
            
            if imagem and ordem:
                # Verificar se já existe uma imagem na mesma ordem
                if CarrosselImagem.objects.filter(ordem=ordem).exists():
                    messages.error(request, f'Já existe uma imagem na posição {ordem}.')
                else:
                    # Verificar limite de 5 imagens
                    if CarrosselImagem.objects.count() >= 5:
                        messages.error(request, 'Limite máximo de 5 imagens atingido.')
                    else:
                        try:
                            nova_imagem = CarrosselImagem.objects.create(
                                titulo=titulo,
                                imagem=imagem,
                                descricao=descricao,
                                ordem=int(ordem),
                                criado_por=request.user
                            )
                        except Exception as e:
                            messages.error(request, f'Erro ao adicionar imagem: {str(e)}')
            else:
                messages.error(request, 'Por favor, selecione uma imagem e uma posição.')
        
        return redirect('conteudoPrincipal')
    
    # Buscar todas as imagens do carrossel
    imagens_carrossel = CarrosselImagem.objects.all().order_by('ordem', 'data_criacao')
    
    # Obter ordens já ocupadas
    ordens_ocupadas = list(imagens_carrossel.values_list('ordem', flat=True))
    
    context = {
        'perfil': perfil,
        'imagens_carrossel': imagens_carrossel,
        'ordens_ocupadas': ordens_ocupadas,
    }
    
    return render(request, 'login/dashboard/conteudo_principal.html', context)

@login_required
def cadastrosGerenciamento(request):
    perfil = request.user.perfil
    
    # Verificar se o usuário tem permissão para acessar esta página
    if not perfil.pode_ativar_usuarios():
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    # Processar ações POST
    if request.method == 'POST':
        acao = request.POST.get('acao')
        usuario_id = request.POST.get('usuario_id')
        
        if acao == 'editar_perfil':
            try:
                # Verificar se o usuário tem permissão para editar
                if perfil.cargo not in ['gerente', 'administrador']:
                    messages.error(request, 'Você não tem permissão para editar perfis.')
                    return redirect('cadastrosGerenciamento')
                
                perfil_editado = get_object_or_404(Perfil, id=usuario_id)
                form = EditarPerfilForm(request.POST, instance=perfil_editado, user_perfil=perfil)
                if form.is_valid():
                    form.save()
                else:
                    messages.error(request, 'Erro ao atualizar perfil. Verifique os dados.')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar perfil: {str(e)}')
        
        elif acao == 'force_reset_senha':
            try:
                # Verificar se o usuário tem permissão para forçar reset
                if perfil.cargo not in ['gerente', 'administrador']:
                    messages.error(request, 'Você não tem permissão para forçar reset de senha.')
                    return redirect('cadastrosGerenciamento')
                
                confirmar_reset = request.POST.get('confirmar_reset')
                if not confirmar_reset:
                    # messages.error(request, 'Você deve confirmar a ação para forçar o reset de senha.')
                    return redirect('cadastrosGerenciamento')
                
                perfil_editado = get_object_or_404(Perfil, id=usuario_id)
                perfil_editado.force_password_reset = True
                perfil_editado.save()
            except Exception as e:
                messages.error(request, f'Erro ao forçar reset de senha: {str(e)}')
        
        elif acao == 'toggle_ativo':
            try:
                # Verificar se o usuário tem permissão para ativar/desativar
                if perfil.cargo not in ['gerente', 'administrador']:
                    messages.error(request, 'Você não tem permissão para ativar/desativar usuários.')
                    return redirect('cadastrosGerenciamento')
                
                perfil_editado = get_object_or_404(Perfil, id=usuario_id)
                perfil_editado.ativo = not perfil_editado.ativo
                perfil_editado.save()
                status = 'ativado' if perfil_editado.ativo else 'desativado'
            except Exception as e:
                messages.error(request, f'Erro ao alterar status: {str(e)}')
        
        elif acao == 'editar_usuario':
            try:
                # Verificar se o usuário tem permissão para editar
                if perfil.cargo not in ['gerente', 'administrador']:
                    messages.error(request, 'Você não tem permissão para editar usuários.')
                    return redirect('cadastrosGerenciamento')
                
                perfil_editado = get_object_or_404(Perfil, id=usuario_id)
                
                # Atualizar cargo
                novo_cargo = request.POST.get('cargo')
                if novo_cargo in ['administrador', 'gerente', 'administrativo', 'operador']:
                    perfil_editado.cargo = novo_cargo
                
                # Atualizar status ativo
                perfil_editado.ativo = request.POST.get('ativo') == 'on'
                
                # Alterar senha se fornecida
                nova_senha = request.POST.get('nova_senha')
                confirmar_senha = request.POST.get('confirmar_senha')
                
                if nova_senha:
                    if nova_senha != confirmar_senha:
                        messages.error(request, 'As senhas não coincidem.')
                        return redirect('cadastrosGerenciamento')
                    
                    if len(nova_senha) < 6:
                        messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
                        return redirect('cadastrosGerenciamento')
                    
                    # Alterar a senha do usuário Django
                    user = perfil_editado.user
                    user.set_password(nova_senha)
                    user.save()
                
                perfil_editado.save()
                
            except Exception as e:
                messages.error(request, f'Erro ao editar usuário: {str(e)}')
        
        return redirect('cadastrosGerenciamento')
    
    # Listar todos os usuários
    usuarios = Perfil.objects.all().order_by('-data_criacao')
    
    # Preparar formulários para cada usuário
    usuarios_com_forms = []
    for usuario in usuarios:
        editar_form = EditarPerfilForm(instance=usuario, user_perfil=perfil)
        usuarios_com_forms.append({
            'usuario': usuario,
            'editar_form': editar_form
        })
    
    context = {
        'perfil': perfil,
        'usuarios_com_forms': usuarios_com_forms,
        'total_usuarios': usuarios.count(),
        'usuarios_ativos': usuarios.filter(ativo=True).count(),
        'usuarios_inativos': usuarios.filter(ativo=False).count(),
    }
    
    return render(request, 'login/dashboard/cadastros_gerenciamento.html', context)

@login_required
def configuracao(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/configuracao.html', {'perfil': perfil})

def logout_usuario(request):
    logout(request)
    return redirect('home')

# Funções de Exportação
@login_required
def exportar_relatorio_excel(request, tipo_relatorio):
    """Exporta relatórios para Excel"""
    
    # Criar workbook em memória
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # Formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1
    })
    
    data_format = workbook.add_format({
        'border': 1,
        'align': 'center'
    })
    
    # Obter dados baseado no tipo de relatório
    if tipo_relatorio == 'turno':
        dados = obter_dados_turno_excel(request)
        worksheet = workbook.add_worksheet('Relatório de Turnos')
        
        # Cabeçalhos
        headers = ['Data', 'Turno', 'Responsável', 'RE', 'Total Fardos', 'Retrabalho', 'Eficiência (%)', 'Observações']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Dados
        for row, item in enumerate(dados, 1):
            worksheet.write(row, 0, item.get('data', ''), data_format)
            worksheet.write(row, 1, item.get('turno', ''), data_format)
            worksheet.write(row, 2, item.get('responsavel', ''), data_format)
            worksheet.write(row, 3, item.get('re', ''), data_format)
            worksheet.write(row, 4, item.get('total_fardos', 0), data_format)
            worksheet.write(row, 5, item.get('retrabalho', 0), data_format)
            worksheet.write(row, 6, item.get('eficiencia', 0), data_format)
            worksheet.write(row, 7, item.get('observacoes', ''), data_format)
    
    elif tipo_relatorio == 'extrusora':
        dados = obter_dados_extrusora_excel(request)
        worksheet = workbook.add_worksheet('Relatório de Extrusora')
        
        headers = ['Data', 'Turno', 'Responsável', 'Início', 'Fim', 'Duração', 'Status', 'Observações']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        for row, item in enumerate(dados, 1):
            worksheet.write(row, 0, item.get('data', ''), data_format)
            worksheet.write(row, 1, item.get('turno', ''), data_format)
            worksheet.write(row, 2, item.get('responsavel', ''), data_format)
            worksheet.write(row, 3, item.get('inicio', ''), data_format)
            worksheet.write(row, 4, item.get('fim', ''), data_format)
            worksheet.write(row, 5, item.get('duracao', ''), data_format)
            worksheet.write(row, 6, item.get('status', ''), data_format)
            worksheet.write(row, 7, item.get('observacoes', ''), data_format)
    
    elif tipo_relatorio == 'carregamento':
        dados = obter_dados_carregamento_excel(request)
        worksheet = workbook.add_worksheet('Relatório de Carregamento')
        
        headers = ['Data', 'Empresa', 'Produto', 'Quantidade', 'Status', 'Responsável', 'Observações']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        for row, item in enumerate(dados, 1):
            worksheet.write(row, 0, item.get('data', ''), data_format)
            worksheet.write(row, 1, item.get('empresa', ''), data_format)
            worksheet.write(row, 2, item.get('produto', ''), data_format)
            worksheet.write(row, 3, item.get('quantidade', 0), data_format)
            worksheet.write(row, 4, item.get('status', ''), data_format)
            worksheet.write(row, 5, item.get('responsavel', ''), data_format)
            worksheet.write(row, 6, item.get('observacoes', ''), data_format)
    

    
    # Ajustar largura das colunas
    worksheet.set_column('A:H', 15)
    
    workbook.close()
    output.seek(0)
    
    # Preparar resposta
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="relatorio_{tipo_relatorio}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    
    return response

@login_required
def exportar_relatorio_pdf(request, tipo_relatorio):
    """Exporta relatórios para PDF"""
    
    # Criar buffer em memória
    buffer = io.BytesIO()
    
    # Criar documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Centralizado
    )
    
    # Título
    titulo_map = {
        'turno': 'Relatório de Turnos',
        'extrusora': 'Relatório de Extrusora',
        'carregamento': 'Relatório de Carregamento',
        'plil': 'Relatório PLIL',
        'etiquetas': 'Relatório de Etiquetas',
        'geral': 'Relatório Geral'
    }
    
    titulo = Paragraph(titulo_map.get(tipo_relatorio, 'Relatório'), title_style)
    elements.append(titulo)
    elements.append(Spacer(1, 12))
    
    # Data de geração
    data_geracao = Paragraph(f"Gerado em: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal'])
    elements.append(data_geracao)
    elements.append(Spacer(1, 20))
    
    # Obter dados e criar tabela
    if tipo_relatorio == 'turno':
        dados = obter_dados_turno_pdf(request)
        headers = ['Data', 'Turno', 'Responsável', 'Total Fardos', 'Retrabalho', 'Eficiência (%)']
        table_data = [headers]
        
        for item in dados:
            table_data.append([
                item.get('data', ''),
                item.get('turno', ''),
                item.get('responsavel', ''),
                str(item.get('total_fardos', 0)),
                str(item.get('retrabalho', 0)),
                f"{item.get('eficiencia', 0)}%"
            ])
    
    elif tipo_relatorio == 'extrusora':
        dados = obter_dados_extrusora_pdf(request)
        headers = ['Data', 'Turno', 'Responsável', 'Duração', 'Status']
        table_data = [headers]
        
        for item in dados:
            table_data.append([
                item.get('data', ''),
                item.get('turno', ''),
                item.get('responsavel', ''),
                item.get('duracao', ''),
                item.get('status', '')
            ])
    
    elif tipo_relatorio == 'carregamento':
        dados = obter_dados_carregamento_pdf(request)
        headers = ['Data', 'Empresa', 'Produto', 'Quantidade', 'Status']
        table_data = [headers]
        
        for item in dados:
            table_data.append([
                item.get('data', ''),
                item.get('empresa', ''),
                item.get('produto', ''),
                str(item.get('quantidade', 0)),
                item.get('status', '')
            ])
    

    
    # Criar e estilizar tabela
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    
    # Preparar resposta
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{tipo_relatorio}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response

# Funções auxiliares para obter dados
def obter_dados_turno_excel(request):
    """Obtém dados do relatório de turno para Excel"""
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    turno_filtro = request.GET.get('turno', '')
    
    if not data_inicio:
        data_inicio = timezone.now().date() - timedelta(days=30)
    else:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    
    if not data_fim:
        data_fim = timezone.now().date()
    else:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    
    fechamentos = FechamentoTurno.objects.filter(
        data_hora__date__range=[data_inicio, data_fim]
    )
    
    if turno_filtro:
        fechamentos = fechamentos.filter(turno=turno_filtro)
    
    dados = []
    for fechamento in fechamentos:
        eficiencia = round((fechamento.total_fardo / (fechamento.total_fardo + fechamento.reversao) * 100) if (fechamento.total_fardo + fechamento.reversao) > 0 else 0, 1)
        dados.append({
            'data': fechamento.data_hora.strftime('%d/%m/%Y'),
            'turno': fechamento.turno,
            'responsavel': fechamento.nome,
            're': fechamento.re,
            'total_fardos': fechamento.total_fardo,
            'reversao': fechamento.reversao,
            'eficiencia': eficiencia,
            'observacoes': fechamento.observacao or ''
        })
    
    return dados

def obter_dados_turno_pdf(request):
    """Obtém dados do relatório de turno para PDF"""
    return obter_dados_turno_excel(request)

def obter_dados_extrusora_excel(request):
    """Obtém dados do relatório de extrusora para Excel"""
    from datetime import datetime, timedelta
    
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    turno_filtro = request.GET.get('turno')
    status_filtro = request.GET.get('status')
    
    if not data_inicio:
        data_inicio = timezone.now().date() - timedelta(days=30)
    else:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    
    if not data_fim:
        data_fim = timezone.now().date()
    else:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    
    # Buscar dados do diário de bordo (mesmo modelo usado no relatório)
    registros = DiarioBordo.objects.filter(
        data_criacao__date__range=[data_inicio, data_fim]
    )
    
    if turno_filtro:
        registros = registros.filter(turno=turno_filtro)
    
    if status_filtro:
        if status_filtro == 'finalizado':
            registros = registros.filter(fim__isnull=False)
        elif status_filtro == 'maquina_parada':
            registros = registros.filter(maquina_parada=True)
    
    dados = []
    for registro in registros:
        duracao = ''
        status = ''
        
        if registro.fim and registro.inicio:
            delta = registro.fim - registro.inicio
            horas = delta.total_seconds() // 3600
            minutos = (delta.total_seconds() % 3600) // 60
            duracao = f"{int(horas)}h {int(minutos)}m"
        
        # Determinar status
        if registro.maquina_parada:
            status = 'Máquina Parada'
        elif registro.fim:
            status = 'Finalizado'
        else:
            status = 'Em Andamento'
        
        dados.append({
            'data': registro.data_criacao.strftime('%d/%m/%Y'),
            'turno': registro.turno,
            'responsavel': registro.re,
            'inicio': registro.inicio.strftime('%H:%M') if registro.inicio else '',
            'fim': registro.fim.strftime('%H:%M') if registro.fim else '',
            'duracao': duracao,
            'status': status,
            'observacoes': registro.ocorrencias_turno or ''
        })
    
    return dados

def obter_dados_extrusora_pdf(request):
    """Obtém dados do relatório de extrusora para PDF"""
    return obter_dados_extrusora_excel(request)

def obter_dados_carregamento_excel(request):
    """Obtém dados do relatório de carregamento para Excel"""
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    empresa_filtro = request.GET.get('empresa')
    status_filtro = request.GET.get('status')
    
    if not data_inicio:
        data_inicio = timezone.now().date() - timedelta(days=30)
    else:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    
    if not data_fim:
        data_fim = timezone.now().date()
    else:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    
    # Usar CarregamentoDashboard que é o modelo correto usado no relatório
    carregamentos = CarregamentoDashboard.objects.filter(
        data_criacao__date__range=[data_inicio, data_fim]
    )
    
    # Aplicar filtros adicionais
    if empresa_filtro:
        carregamentos = carregamentos.filter(empresa_id=empresa_filtro)
    
    if status_filtro:
        if status_filtro == 'concluido':
            carregamentos = carregamentos.filter(status='concluido')
        elif status_filtro == 'pendente':
            carregamentos = carregamentos.filter(status='pendente')
    
    dados = []
    for carregamento in carregamentos:
        dados.append({
            'data_criacao': carregamento.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'empresa': carregamento.empresa.nome,
            'material': carregamento.material,
            'status': carregamento.get_status_display(),
            'data_conclusao': carregamento.data_conclusao.strftime('%d/%m/%Y %H:%M') if carregamento.data_conclusao else '',
            'concluido_por': carregamento.concluido_por.perfil.nome if carregamento.concluido_por and hasattr(carregamento.concluido_por, 'perfil') else (carregamento.concluido_por.username if carregamento.concluido_por else ''),
            'criado_por': carregamento.criado_por.perfil.nome if carregamento.criado_por and hasattr(carregamento.criado_por, 'perfil') else (carregamento.criado_por.username if carregamento.criado_por else '')
        })
    
    return dados

def obter_dados_carregamento_pdf(request):
    """Obtém dados do relatório de carregamento para PDF"""
    return obter_dados_carregamento_excel(request)

@login_required
def exportar_dados_banco(request):
    """Endpoint para fornecer TODOS os dados do banco para exportação Excel"""
    from django.http import JsonResponse
    from django.utils import timezone
    
    try:
        # 1. Dados de Perfis
        perfis = []
        for perfil in Perfil.objects.all():
            perfis.append([
                perfil.id,
                perfil.re,
                perfil.nome,
                perfil.sobrenome,
                perfil.get_cargo_display(),
                'Ativo' if perfil.ativo else 'Inativo',
                perfil.data_criacao.strftime('%d/%m/%Y %H:%M')
            ])
        
        # 2. Dados de Fechamento de Turno
        fechamento_turno = []
        for fechamento in FechamentoTurno.objects.all():
            fechamento_turno.append([
                fechamento.data_hora.strftime('%d/%m/%Y %H:%M'),
                fechamento.re,
                fechamento.nome,
                f'Turno {fechamento.turno}',
                fechamento.fardo_virgem,
                fechamento.fardo_laminado,
                fechamento.total_fardo,
                fechamento.reversao,
                fechamento.observacao
            ])
        
        # 3. Dados de Diário de Bordo
        diario_bordo = []
        for diario in DiarioBordo.objects.all():
            diario_bordo.append([
                diario.data.strftime('%d/%m/%Y') if diario.data else '',
                f'Turno {diario.turno}' if diario.turno else '',
                diario.re or '',
                diario.maquina_rodando,
                diario.maquina_disponivel,
                diario.inicio.strftime('%d/%m/%Y %H:%M') if diario.inicio else '',
                diario.fim.strftime('%d/%m/%Y %H:%M') if diario.fim else '',
                diario.ocorrencias_turno
            ])
        
        # 4. Dados de Água/Cloro
        agua_cloro = []
        for agua in AguaCloro.objects.all():
            agua_cloro.append([
                agua.data_hora.strftime('%d/%m/%Y %H:%M'),
                agua.re,
                f'Turno {agua.turno}',
                float(agua.cloro),
                float(agua.turbidez),
                agua.observacao
            ])
        
        # 5. Dados de Fechamento Bag
        fechamento_bag = []
        for bag in FechamentoBag.objects.all():
            fechamento_bag.append([
                bag.data.strftime('%d/%m/%Y'),
                bag.quantidade,
                bag.observacoes
            ])
        
        # 6. Dados de Inventário
        inventario = []
        for inv in Inventario.objects.all():
            inventario.append([
                inv.data.strftime('%d/%m/%Y'),
                inv.produto,
                inv.quantidade
            ])
        
        # 7. Dados de Carregamento
        carregamento = []
        for carr in Carregamento.objects.all():
            carregamento.append([
                carr.data_hora.strftime('%d/%m/%Y %H:%M'),
                carr.veiculo,
                carr.quantidade
            ])
        
        # 8. Dados de Templates de Tarefa
        templates_tarefa = []
        for template in TarefaTemplate.objects.all():
            templates_tarefa.append([
                template.id,
                template.titulo,
                template.descricao,
                template.get_periodicidade_display(),
                'Ativo' if template.ativo else 'Inativo',
                template.criado_por.username if template.criado_por else '',
                template.data_criacao.strftime('%d/%m/%Y %H:%M')
            ])
        
        # 9. Dados de PLIL
        plil = []
        for p in Plil.objects.all():
            plil.append([
                p.template.titulo,
                p.re_responsavel,
                p.nome_responsavel,
                p.data_prevista.strftime('%d/%m/%Y'),
                p.data_execucao.strftime('%d/%m/%Y %H:%M') if p.data_execucao else '',
                p.get_status_display(),
                p.observacoes_execucao,
                p.atribuida_por.username if p.atribuida_por else ''
            ])
        
        # 10. Dados de Etiquetas
        etiquetas = []
        for etiq in Etiqueta.objects.all():
            etiquetas.append([
                etiq.codigo,
                etiq.produto,
                etiq.data_criacao.strftime('%d/%m/%Y %H:%M')
            ])
        
        # 11. Dados de Relatório de Turno
        relatorio_turno = []
        for rel in RelatorioTurno.objects.all():
            relatorio_turno.append([
                rel.data.strftime('%d/%m/%Y'),
                f'Turno {rel.turno}',
                rel.conteudo
            ])
        
        # 12. Dados de Relatório de Extrusora
        relatorio_extrusora = []
        for rel in RelatorioExtrusoura.objects.all():
            relatorio_extrusora.append([
                rel.data.strftime('%d/%m/%Y'),
                rel.maquina,
                rel.producao
            ])
        
        # 13. Dados de Cadastro (Equipamentos)
        equipamentos = []
        for cadastro in Cadastro.objects.all():
            equipamentos.append([
                cadastro.id,
                cadastro.nome,
                cadastro.tipo,
                'Ativo' if cadastro.ativo else 'Inativo',
                cadastro.data_criacao.strftime('%d/%m/%Y %H:%M')
            ])
        
        # 14. Dados de Produção Mensal
        producao_mensal = []
        for prod in ProducaoMensal.objects.all():
            producao_mensal.append([
                f'{prod.mes:02d}/{prod.ano}',
                f'Turno {prod.turno}',
                prod.total_fardo,
                prod.total_reversao,
                prod.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')
            ])
        
        # 15. Dados de Carregamento Dashboard
        carregamento_dashboard = []
        for carr in CarregamentoDashboard.objects.all():
            carregamento_dashboard.append([
                carr.data.strftime('%d/%m/%Y'),
                carr.empresa.nome,
                carr.material,
                carr.get_status_display(),
                carr.data_criacao.strftime('%d/%m/%Y %H:%M'),
                carr.concluido_por.username if carr.concluido_por else '',
                carr.criado_por.username if carr.criado_por else ''
            ])
        
        # 16. Dados de Empresas
        empresas = []
        for emp in Empresa.objects.all():
            empresas.append([
                emp.id,
                emp.nome,
                'Ativo' if emp.ativo else 'Inativo',
                emp.data_criacao.strftime('%d/%m/%Y %H:%M')
            ])
        
        # Estruturar resposta com TODOS os dados
        data = {
            'perfis': perfis,
            'fechamento_turno': fechamento_turno,
            'diario_bordo': diario_bordo,
            'agua_cloro': agua_cloro,
            'fechamento_bag': fechamento_bag,
            'inventario': inventario,
            'carregamento': carregamento,
            'templates_tarefa': templates_tarefa,
            'plil': plil,
            'etiquetas': etiquetas,
            'relatorio_turno': relatorio_turno,
            'relatorio_extrusora': relatorio_extrusora,
            'equipamentos': equipamentos,
            'producao_mensal': producao_mensal,
            'carregamento_dashboard': carregamento_dashboard,
            'empresas': empresas,
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Erro ao obter dados: {str(e)}',
            'perfis': [],
            'fechamento_turno': [],
            'diario_bordo': [],
            'agua_cloro': [],
            'fechamento_bag': [],
            'inventario': [],
            'carregamento': [],
            'templates_tarefa': [],
            'plil': [],
            'etiquetas': [],
            'relatorio_turno': [],
            'relatorio_extrusora': [],
            'equipamentos': [],
            'producao_mensal': [],
            'carregamento_dashboard': [],
            'empresas': []
        }, status=500)