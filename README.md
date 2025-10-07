# Sistema Tetra - Diário de Bordo

Sistema Django para gerenciamento de diário de bordo e cadastros.

## 🔒 Configuração Segura para Deploy

### 1. Configurações de Ambiente

Este projeto usa variáveis de ambiente para proteger informações sensíveis:

1. Copie o arquivo `.env.example` para `.env`
2. Preencha as variáveis com os valores corretos
3. **NUNCA** commite o arquivo `.env` no Git

### 2. Deploy no PythonAnywhere

#### Pré-requisitos:
- Conta no PythonAnywhere
- Repositório GitHub configurado

#### Passos para Deploy:

1. **No PythonAnywhere:**
   ```bash
   git clone https://github.com/seuusuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. **Criar ambiente virtual:**
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente:**
   - Crie o arquivo `.env` no servidor
   - Configure as variáveis conforme `.env.example`
   - **IMPORTANTE:** Use uma SECRET_KEY diferente para produção

5. **Configurar banco de dados:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   python manage.py createsuperuser
   ```

6. **Configurar Web App no PythonAnywhere:**
   - Source code: `/home/yourusername/seu-repositorio`
   - Working directory: `/home/yourusername/seu-repositorio`
   - WSGI file: editar para apontar para `Tetra.wsgi`

### 3. Segurança

✅ **Implementado:**
- Variáveis de ambiente para dados sensíveis
- `.gitignore` configurado
- Configurações de segurança para produção
- Proteção contra XSS, CSRF, etc.

⚠️ **Importante:**
- Sempre use HTTPS em produção
- Mantenha a SECRET_KEY segura
- Configure backup do banco de dados
- Monitore logs de segurança

### 4. Estrutura do Projeto

```
Tetra/
├── .env.example          # Template de configurações
├── .gitignore           # Arquivos ignorados pelo Git
├── requirements.txt     # Dependências Python
├── manage.py           # Comando Django
├── Tetra/              # Configurações principais
│   ├── settings.py     # Configurações (com variáveis de ambiente)
│   └── ...
├── prs/                # App principal
└── template-global/    # Templates globais
```

### 5. Comandos Úteis

```bash
# Desenvolvimento local
python manage.py runserver

# Aplicar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic

# Criar superusuário
python manage.py createsuperuser
```

## 📞 Suporte

Para dúvidas sobre deploy ou configuração, consulte a documentação do Django e PythonAnywhere.