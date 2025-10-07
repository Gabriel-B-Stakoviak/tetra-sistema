from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .forms import RegistroForm, FechamentoTurnoForm, DiarioBordoForm, AguaCloroForm, EditarPerfilForm, ForcePasswordResetForm
from django.shortcuts import get_list_or_404
from .models import *
from datetime import datetime, time
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

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
            
            messages.success(request, 'Senha redefinida com sucesso!')
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
    return render(request, 'login/dashboard/dashboard.html', {'perfil': perfil})

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
            
            messages.success(request, f'Fechamento do Turno {turno_atual} realizado com sucesso!')
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
    return render(request, 'login/dashboard/carregamento.html', {'perfil': perfil})

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
            messages.success(request, 'Entrada do Diário de Bordo registrada com sucesso!')
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
        entrada.fim = timezone.now()
        entrada.save()
        return JsonResponse({
            'success': True,
            'fim': entrada.fim.strftime('%d/%m/%Y %H:%M'),
            'fim_formatado': entrada.fim.strftime('%H:%M')
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
            messages.success(request, 'Registro de água da extrusora salvo com sucesso!')
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
    return render(request, 'login/dashboard/plil.html', {'perfil': perfil})

@login_required
def etiqueta(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/etiqueta.html', {'perfil': perfil})

@login_required
def relatorioTurno(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/relatorio/relatorio_turno.html', {'perfil': perfil})

@login_required
def relatorioExtrusoura(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/relatorio/relatorio_extrusoura.html', {'perfil': perfil})

@login_required
def relatorioCarregamento(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/relatorio/relatorio_carregamento.html', {'perfil': perfil})

@login_required
def relatorioPlil(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/relatorio/relatorio_plil.html', {'perfil': perfil})

@login_required
def relatorioEtiquetas(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/relatorio/relatorio_etiqueta.html', {'perfil': perfil})

@login_required
def relatorioGeral(request):
    perfil = request.user.perfil
    return render(request, 'login/dashboard/relatorio/relatorio_geral.html', {'perfil': perfil})

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
                messages.success(request, f'Imagem {status} com sucesso!')
            except CarrosselImagem.DoesNotExist:
                messages.error(request, 'Imagem não encontrada.')
                
        elif action == 'excluir':
            # Excluir imagem
            imagem_id = request.POST.get('imagem_id')
            try:
                imagem = CarrosselImagem.objects.get(id=imagem_id)
                imagem.delete()
                messages.success(request, 'Imagem excluída com sucesso!')
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
                            messages.success(request, 'Imagem adicionada com sucesso!')
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
                    messages.success(request, f'Perfil de {perfil_editado.nome} atualizado com sucesso!')
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
                    messages.error(request, 'Você deve confirmar a ação para forçar o reset de senha.')
                    return redirect('cadastrosGerenciamento')
                
                perfil_editado = get_object_or_404(Perfil, id=usuario_id)
                perfil_editado.force_password_reset = True
                perfil_editado.save()
                messages.success(request, f'Reset de senha forçado para {perfil_editado.nome}. O usuário deverá definir uma nova senha no próximo login.')
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
                messages.success(request, f'Usuário {perfil_editado.nome} {status} com sucesso!')
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
                    
                    messages.success(request, f'Senha de {perfil_editado.nome} alterada com sucesso!')
                
                perfil_editado.save()
                messages.success(request, f'Dados de {perfil_editado.nome} atualizados com sucesso!')
                
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