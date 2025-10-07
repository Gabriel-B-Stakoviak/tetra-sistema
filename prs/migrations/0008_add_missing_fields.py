# Generated manually to fix missing fields

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('prs', '0007_carrosselimagem'),
    ]

    operations = [
        # Add fields to aguacloro
        migrations.AddField(
            model_name='aguacloro',
            name='data_hora',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='aguacloro',
            name='nivel_cloro',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='aguacloro',
            name='ph_agua',
            field=models.DecimalField(decimal_places=2, default=7.0, max_digits=4),
        ),
        
        # Add fields to cadastro
        migrations.AddField(
            model_name='cadastro',
            name='nome',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cadastro',
            name='tipo',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cadastro',
            name='data_criacao',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cadastro',
            name='ativo',
            field=models.BooleanField(default=True),
        ),
        
        # Add fields to diariobordo
        migrations.AddField(
            model_name='diariobordo',
            name='data',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='diariobordo',
            name='turno',
            field=models.CharField(default='1', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='diariobordo',
            name='observacoes',
            field=models.TextField(blank=True),
        ),
        
        # Add fields to etiqueta
        migrations.AddField(
            model_name='etiqueta',
            name='codigo',
            field=models.CharField(default='', max_length=50, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='etiqueta',
            name='produto',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='etiqueta',
            name='data_criacao',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        
        # Add fields to fechamentobag
        migrations.AddField(
            model_name='fechamentobag',
            name='data',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fechamentobag',
            name='quantidade',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='fechamentobag',
            name='observacoes',
            field=models.TextField(blank=True),
        ),
        
        # Add fields to inventario
        migrations.AddField(
            model_name='inventario',
            name='data',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventario',
            name='produto',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventario',
            name='quantidade',
            field=models.IntegerField(default=0),
        ),
        
        # Add fields to plil
        migrations.AddField(
            model_name='plil',
            name='data',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plil',
            name='codigo',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plil',
            name='descricao',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        
        # Create new models with correct names
        migrations.CreateModel(
            name='Carregamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_hora', models.DateTimeField(auto_now_add=True)),
                ('veiculo', models.CharField(max_length=50)),
                ('quantidade', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ConteudoPrincipal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('conteudo', models.TextField()),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('ativo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelatorioCarregamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(auto_now_add=True)),
                ('total_carregamentos', models.IntegerField(default=0)),
                ('observacoes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelatorioEtiqueta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(auto_now_add=True)),
                ('total_etiquetas', models.IntegerField(default=0)),
                ('observacoes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelatorioExtrusoura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(auto_now_add=True)),
                ('maquina', models.CharField(max_length=50)),
                ('producao', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RelatorioGeral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(auto_now_add=True)),
                ('titulo', models.CharField(max_length=200)),
                ('conteudo', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='RelatorioInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(auto_now_add=True)),
                ('total_itens', models.IntegerField(default=0)),
                ('observacoes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelatorioPlil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(auto_now_add=True)),
                ('total_plils', models.IntegerField(default=0)),
                ('observacoes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelatorioTurno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(auto_now_add=True)),
                ('turno', models.CharField(max_length=1)),
                ('conteudo', models.TextField()),
            ],
        ),
        
        # Delete old models with incorrect names
        migrations.DeleteModel(
            name='conteudo_principal',
        ),
        migrations.DeleteModel(
            name='relatorio_carregamento',
        ),
        migrations.DeleteModel(
            name='relatorio_etiqueta',
        ),
        migrations.DeleteModel(
            name='relatorio_extrusoura',
        ),
        migrations.DeleteModel(
            name='relatorio_geral',
        ),
        migrations.DeleteModel(
            name='relatorio_inventario',
        ),
        migrations.DeleteModel(
            name='relatorio_plil',
        ),
        migrations.DeleteModel(
            name='relatorio_turno',
        ),
        
        # Alter field on fechamentoturno to remove auto_now_add
        migrations.AlterField(
            model_name='fechamentoturno',
            name='data_hora',
            field=models.DateTimeField(),
        ),
    ]