#!/bin/bash
# Script de Deploy para PythonAnywhere
# Execute este script após clonar o repositório

echo "🚀 Iniciando deploy do Sistema Tetra..."

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto (onde está o manage.py)"
    exit 1
fi

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3.10 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Verificar se existe arquivo .env
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📋 Copie o arquivo .env.example para .env e configure as variáveis:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    echo ""
    echo "🔑 IMPORTANTE: Configure uma SECRET_KEY segura para produção!"
    echo "   Você pode gerar uma em: https://djecrety.ir/"
    exit 1
fi

# Aplicar migrações
echo "🗄️  Aplicando migrações do banco de dados..."
python manage.py migrate

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Deploy concluído com sucesso!"
echo ""
echo "📝 Próximos passos:"
echo "1. Configure o Web App no PythonAnywhere"
echo "2. Aponte o WSGI para: Tetra.wsgi"
echo "3. Configure o diretório de trabalho"
echo "4. Crie um superusuário: python manage.py createsuperuser"
echo ""
echo "🔗 Seu site estará disponível em: https://yourusername.pythonanywhere.com"