#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tetra.settings')
django.setup()

from prs.models import CarregamentoDashboard, Empresa, User
from django.utils import timezone

def criar_dados_teste():
    print("Criando dados de teste para carregamentos...")
    
    # Criar ou obter usuário admin
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@teste.com',
            password='admin123'
        )
        print("Usuário admin criado")
    
    # Criar empresas de teste
    empresas_nomes = ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa D']
    empresas = []
    
    for nome in empresas_nomes:
        empresa, created = Empresa.objects.get_or_create(
            nome=nome,
            defaults={
                'cnpj': f'12.345.678/0001-{len(empresas):02d}',
                'contato': f'Contato {nome}',
                'telefone': f'(11) 9999-{1000 + len(empresas):04d}',
                'criado_por': admin_user
            }
        )
        empresas.append(empresa)
        if created:
            print(f"Empresa {nome} criada")
    
    # Criar carregamentos de teste
    materiais = ['Material A', 'Material B', 'Material C', 'Material D', 'Material E']
    status_opcoes = ['pendente', 'concluido']
    
    # Criar carregamentos dos últimos 30 dias
    for i in range(50):  # 50 carregamentos de teste
        data_criacao = timezone.now() - timedelta(days=i % 30, hours=i % 24)
        
        carregamento = CarregamentoDashboard.objects.create(
            empresa=empresas[i % len(empresas)],
            material=materiais[i % len(materiais)],
            status=status_opcoes[i % 2],
            data_criacao=data_criacao,
            criado_por=admin_user
        )
        
        # Se for concluído, adicionar data de conclusão
        if carregamento.status == 'concluido':
            carregamento.data_conclusao = data_criacao + timedelta(hours=2)
            carregamento.concluido_por = admin_user
            carregamento.save()
    
    print(f"Criados 50 carregamentos de teste")
    
    # Mostrar estatísticas
    total = CarregamentoDashboard.objects.count()
    concluidos = CarregamentoDashboard.objects.filter(status='concluido').count()
    pendentes = CarregamentoDashboard.objects.filter(status='pendente').count()
    
    print(f"\nEstatísticas:")
    print(f"Total de carregamentos: {total}")
    print(f"Concluídos: {concluidos}")
    print(f"Pendentes: {pendentes}")
    print(f"Empresas: {Empresa.objects.count()}")

if __name__ == '__main__':
    criar_dados_teste()