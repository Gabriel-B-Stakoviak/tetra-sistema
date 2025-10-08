# Deploy no PythonAnywhere - Guia Completo

## Pré-requisitos
- Conta no PythonAnywhere
- Projeto no GitHub
- Python 3.8+ no PythonAnywhere

## Passo 1: Clonar o repositório
```bash
cd ~
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO/Tetra
```

## Passo 2: Criar ambiente virtual
```bash
python3.10 -m venv venv
source venv/bin/activate
```

## Passo 3: Instalar dependências
```bash
pip install -r requirements.txt
```

## Passo 4: Configurar variáveis de ambiente
```bash
cp .env.example .env
nano .env
```

Edite o arquivo .env com suas configurações:
```
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=seuusername.pythonanywhere.com
```

## Passo 5: Configurar banco de dados
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Passo 6: Configurar Web App no PythonAnywhere

1. Vá para a aba "Web" no dashboard do PythonAnywhere
2. Clique em "Add a new web app"
3. Escolha "Manual configuration"
4. Selecione Python 3.10

### Configurar WSGI file:
Edite o arquivo `/var/www/seuusername_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

# Adicionar o caminho do projeto
path = '/home/seuusername/SEU_REPOSITORIO/Tetra'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'Tetra.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Configurar Virtual Environment:
- Virtualenv: `/home/seuusername/SEU_REPOSITORIO/Tetra/venv`

### Configurar Static Files:
- URL: `/static/`
- Directory: `/home/seuusername/SEU_REPOSITORIO/Tetra/staticfiles`

### Configurar Media Files:
- URL: `/media/`
- Directory: `/home/seuusername/SEU_REPOSITORIO/Tetra/media`

## Passo 7: Recarregar a aplicação
Clique no botão "Reload" na aba Web do PythonAnywhere.

## Observações Importantes

### SQLite no PythonAnywhere
- O SQLite funciona perfeitamente no PythonAnywhere
- O arquivo `db.sqlite3` será criado automaticamente
- Faça backup regular do banco de dados
- Para backup: `cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3`

### Atualizações futuras
```bash
cd ~/SEU_REPOSITORIO/Tetra
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Depois clique em "Reload" na aba Web.

### Logs e Debug
- Logs de erro: Aba "Web" > "Error log"
- Logs de acesso: Aba "Web" > "Access log"
- Console: Aba "Consoles" para executar comandos

## Comandos úteis

### Backup do banco
```bash
cd ~/SEU_REPOSITORIO/Tetra
cp db.sqlite3 ~/backups/db_$(date +%Y%m%d_%H%M%S).sqlite3
```

### Restaurar backup
```bash
cd ~/SEU_REPOSITORIO/Tetra
cp ~/backups/db_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3
```

### Ver logs em tempo real
```bash
tail -f /var/log/seuusername.pythonanywhere.com.error.log
```