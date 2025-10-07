from django.db import models
from django.contrib.auth.models import User

# ================================================================================
class Perfil(models.Model):

    CARGO_OPCOES = [
        ('administrador', 'Administrador'),
        ('gerente', 'Gerente'),
        ('administrativo', 'Administrativo'),
        ('operador', 'Operador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    re = models.CharField(max_length=24, unique=True)
    nome = models.CharField(max_length=124)
    cargo = models.CharField(max_length=14, choices=CARGO_OPCOES, default='operador')
    ativo = models.BooleanField(default=False)  # Conta precisa ser ativada por gerente/admin
    force_password_reset = models.BooleanField(default=False)  # Força reset de senha no próximo login
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.get_cargo_display()}) - {'Ativo' if self.ativo else 'Inativo'}"
    
    def pode_ativar_usuarios(self):
        """Verifica se o usuário pode ativar outros usuários"""
        return self.cargo in ['administrador', 'gerente']
    
    def pode_alterar_cargos(self):
        """Verifica se o usuário pode alterar cargos de outros usuários"""
        return self.cargo in ['administrador', 'gerente']
# ================================================================================
class FechamentoTurno(models.Model):
    re = models.CharField(max_length=24)
    nome = models.CharField(max_length=124)
    turno = models.CharField(max_length=1)
    data_hora = models.DateTimeField(auto_now_add=True)
    fardo_virgem = models.IntegerField(default=0)
    fardo_laminado = models.IntegerField(default=0)
    total_fardo = models.IntegerField(default=0)
    reversao = models.IntegerField(default=0)
    observacao = models.TextField()
    
    def save(self, *args, **kwargs):
        self.total_fardo = (self.fardo_laminado or 0) + (self.fardo_virgem or 0)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nome} - Turno {self.turno} ({self.data_hora.strftime('%d/%m/%Y')})"

# ================================================================================ 
class DiarioBordo(models.Model):
    TURNO_CHOICES = [
        ('1', 'Turno 1'),
        ('2', 'Turno 2'),
        ('3', 'Turno 3'),
    ]
    
    re = models.CharField(max_length=24, null=True, blank=True)
    data = models.DateField(null=True, blank=True)
    turno = models.CharField(max_length=1, choices=TURNO_CHOICES, null=True, blank=True)
    maquina_rodando = models.IntegerField()
    maquina_disponivel = models.IntegerField()
    inicio = models.DateTimeField(null=True, blank=True)
    fim = models.DateTimeField(null=True, blank=True)
    
    # Campos de checkbox
    troca_tela = models.BooleanField(default=False)
    troca_faca = models.BooleanField(default=False)
    presenca_materiais_estranhos = models.BooleanField(default=False)
    material_insuficiente = models.BooleanField(default=False)
    autonoma = models.BooleanField(default=False)
    preventiva = models.BooleanField(default=False)
    manutencao_mecanica = models.BooleanField(default=False)
    manutencao_eletrica = models.BooleanField(default=False)
    quebra = models.BooleanField(default=False)
    laminadora_parada = models.BooleanField(default=False)
    outros = models.BooleanField(default=False)
    
    # Campo de texto para ocorrências
    ocorrencias_turno = models.TextField(blank=True)
    
    data_criacao = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return f"Diário de Bordo - RE: {self.re} - {self.data} - Turno {self.turno}"
    
    class Meta:
        ordering = ['-data', '-turno']
        verbose_name = "Diário de Bordo"
        verbose_name_plural = "Diários de Bordo"

class AguaCloro(models.Model):
    # Campos automáticos
    re = models.CharField(max_length=50, blank=True, default='')
    data_hora = models.DateTimeField(auto_now_add=True)
    turno = models.CharField(max_length=1, blank=True, default='')
    
    # Campos manuais
    cloro = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Cloro")
    turbidez = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Turbidez")
    observacao = models.TextField(blank=True, verbose_name="Observação")
    
    def __str__(self):
        return f"Água/Cloro - {self.data_hora.strftime('%d/%m/%Y %H:%M')} - Turno {self.turno}"
    
    class Meta:
        verbose_name = "Água/Cloro"
        verbose_name_plural = "Água/Cloro"

class FechamentoBag(models.Model):
    data = models.DateField(auto_now_add=True)
    quantidade = models.IntegerField(default=0)
    observacoes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Fechamento Bag - {self.data}"

# ================================================================================
class Inventario(models.Model):
    data = models.DateField(auto_now_add=True)
    produto = models.CharField(max_length=100)
    quantidade = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Inventário - {self.produto} ({self.data})"

class Carregamento(models.Model):
    data_hora = models.DateTimeField(auto_now_add=True)
    veiculo = models.CharField(max_length=50)
    quantidade = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Carregamento - {self.veiculo} ({self.data_hora.strftime('%d/%m/%Y')})"

class Plil(models.Model):
    data = models.DateField(auto_now_add=True)
    codigo = models.CharField(max_length=20)
    descricao = models.TextField()
    
    def __str__(self):
        return f"PLIL - {self.codigo}"

# ================================================================================
class Etiqueta(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    produto = models.CharField(max_length=100)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Etiqueta - {self.codigo}"

# ================================================================================
class RelatorioTurno(models.Model):
    data = models.DateField(auto_now_add=True)
    turno = models.CharField(max_length=1)
    conteudo = models.TextField()
    
    def __str__(self):
        return f"Relatório Turno - {self.data} - Turno {self.turno}"

class RelatorioExtrusoura(models.Model):
    data = models.DateField(auto_now_add=True)
    maquina = models.CharField(max_length=50)
    producao = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Relatório Extrusora - {self.maquina} ({self.data})"

class RelatorioInventario(models.Model):
    data = models.DateField(auto_now_add=True)
    total_itens = models.IntegerField(default=0)
    observacoes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Relatório Inventário - {self.data}"

class RelatorioCarregamento(models.Model):
    data = models.DateField(auto_now_add=True)
    total_carregamentos = models.IntegerField(default=0)
    observacoes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Relatório Carregamento - {self.data}"

class RelatorioPlil(models.Model):
    data = models.DateField(auto_now_add=True)
    total_plils = models.IntegerField(default=0)
    observacoes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Relatório PLIL - {self.data}"

class RelatorioEtiqueta(models.Model):
    data = models.DateField(auto_now_add=True)
    total_etiquetas = models.IntegerField(default=0)
    observacoes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Relatório Etiquetas - {self.data}"

class RelatorioGeral(models.Model):
    data = models.DateField(auto_now_add=True)
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    
    def __str__(self):
        return f"Relatório Geral - {self.titulo} ({self.data})"

class ConteudoPrincipal(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.titulo

# ================================================================================
class Cadastro(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nome} - {self.tipo}"

# ================================================================================
class CarrosselImagem(models.Model):
    titulo = models.CharField(max_length=200, help_text="Título da imagem (opcional)")
    imagem = models.ImageField(upload_to='carrossel/', help_text="Tamanho recomendado: 1200x400 pixels")
    descricao = models.TextField(blank=True, help_text="Descrição da imagem (opcional)")
    ordem = models.PositiveIntegerField(default=1, help_text="Ordem de exibição (1-5)")
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['ordem', 'data_criacao']
        verbose_name = "Imagem do Carrossel"
        verbose_name_plural = "Imagens do Carrossel"
    
    def __str__(self):
        return f"{self.titulo or 'Imagem'} - Ordem {self.ordem}"
    
    def save(self, *args, **kwargs):
        # Limita a ordem entre 1 e 5
        if self.ordem > 5:
            self.ordem = 5
        elif self.ordem < 1:
            self.ordem = 1
        super().save(*args, **kwargs)
