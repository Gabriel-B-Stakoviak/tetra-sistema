from django import forms
from django.contrib.auth.models import User
from .models import Perfil, FechamentoTurno, DiarioBordo, AguaCloro

class RegistroForm(forms.ModelForm):
    username = forms.CharField(label="Usuário")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)

    class Meta:
        model = Perfil
        fields = ['re', 'nome']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        
        # Verifica se é a primeira conta (será administrador)
        is_first_user = not Perfil.objects.exists()
        
        perfil = Perfil(
            user=user,
            re=self.cleaned_data['re'],
            nome=self.cleaned_data['nome'],
            cargo='administrador' if is_first_user else 'operador',
            ativo=True if is_first_user else False  # Primeira conta já ativa
        )
        
        if commit:
            user.save()
            perfil.save()
        return perfil

class FechamentoTurnoForm(forms.ModelForm):
    class Meta:
        model = FechamentoTurno
        fields = ['fardo_virgem', 'fardo_laminado', 'reversao', 'observacao']
        widgets = {
            'fardo_virgem': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantidade de fardos virgem',
                'min': '0'
            }),
            'fardo_laminado': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantidade de fardos laminado',
                'min': '0'
            }),
            'reversao': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de reversões',
                'min': '0'
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva as ocorrências do turno...',
                'rows': 5
            })
        }
        labels = {
            'fardo_virgem': 'Fardos Virgem',
            'fardo_laminado': 'Fardos Laminado',
            'reversao': 'Número de Reversões',
            'observacao': 'Ocorrências do Turno'
        }

class DiarioBordoForm(forms.ModelForm):
    class Meta:
        model = DiarioBordo
        fields = [
            'maquina_rodando', 'maquina_disponivel', 'troca_tela', 'troca_faca', 
            'presenca_materiais_estranhos', 'material_insuficiente', 'autonoma', 
            'preventiva', 'manutencao_mecanica', 'manutencao_eletrica', 'quebra', 
            'laminadora_parada', 'outros', 'ocorrencias_turno'
        ]
        widgets = {
            'maquina_rodando': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da máquina rodando',
                'min': '0',
                'required': True
            }),
            'maquina_disponivel': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da máquina disponível',
                'min': '0',
                'required': True
            }),
            'troca_tela': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'troca_faca': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'presenca_materiais_estranhos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'material_insuficiente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'autonoma': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preventiva': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manutencao_mecanica': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manutencao_eletrica': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quebra': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'laminadora_parada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'outros': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ocorrencias_turno': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva as ocorrências do turno...',
                'rows': 4
            })
        }
        labels = {
            'maquina_rodando': 'Máquina Rodando',
            'maquina_disponivel': 'Máquina Disponível',
            'troca_tela': 'Troca de Tela',
            'troca_faca': 'Troca de Faca',
            'presenca_materiais_estranhos': 'Presença de Materiais Estranhos',
            'material_insuficiente': 'Material Insuficiente',
            'autonoma': 'Autônoma',
            'preventiva': 'Preventiva',
            'manutencao_mecanica': 'Manutenção Mecânica',
            'manutencao_eletrica': 'Manutenção Elétrica',
            'quebra': 'Quebra',
            'laminadora_parada': 'Laminadora Parada',
            'outros': 'Outros',
            'ocorrencias_turno': 'Ocorrências do Turno'
        }

class AguaCloroForm(forms.ModelForm):
    class Meta:
        model = AguaCloro
        fields = ['cloro', 'turbidez', 'observacao']
        widgets = {
            'cloro': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nível de cloro',
                'step': '0.01',
                'min': '0'
            }),
            'turbidez': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nível de turbidez',
                'step': '0.01',
                'min': '0'
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observações sobre a água da extrusora...',
                'rows': 4
            })
        }
        labels = {
            'cloro': 'Cloro',
            'turbidez': 'Turbidez',
            'observacao': 'Observação'
        }

class EditarPerfilForm(forms.ModelForm):
    """Formulário para edição de perfil por gerentes/administradores"""
    class Meta:
        model = Perfil
        fields = ['cargo', 'ativo']
        widgets = {
            'cargo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'cargo': 'Cargo',
            'ativo': 'Conta Ativa'
        }

    def __init__(self, *args, **kwargs):
        user_perfil = kwargs.pop('user_perfil', None)
        super().__init__(*args, **kwargs)
        
        # Apenas gerentes e administradores podem alterar cargos e status
        if user_perfil and user_perfil.cargo not in ['gerente', 'administrador']:
            self.fields['cargo'].disabled = True
            self.fields['ativo'].disabled = True

class ForcePasswordResetForm(forms.Form):
    """Formulário para forçar reset de senha no próximo login"""
    confirmar_reset = forms.BooleanField(
        label='Confirmo que desejo forçar o reset de senha',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='O usuário será obrigado a definir uma nova senha no próximo login'
    )
