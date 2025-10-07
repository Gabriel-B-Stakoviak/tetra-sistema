# Generated manually for CarrosselImagem model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('prs', '0006_auto_20251007_0928'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarrosselImagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(help_text='Título da imagem (opcional)', max_length=200)),
                ('imagem', models.ImageField(help_text='Tamanho recomendado: 1200x400 pixels', upload_to='carrossel/')),
                ('descricao', models.TextField(blank=True, help_text='Descrição da imagem (opcional)')),
                ('ordem', models.PositiveIntegerField(default=1, help_text='Ordem de exibição (1-5)')),
                ('ativo', models.BooleanField(default=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('criado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Imagem do Carrossel',
                'verbose_name_plural': 'Imagens do Carrossel',
                'ordering': ['ordem', 'data_criacao'],
            },
        ),
    ]