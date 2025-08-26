from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, null=True)),
                ('source', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('new', 'جديد'), ('contacted', 'تم التواصل'), ('qualified', 'مهتم'), ('converted', 'تم التحويل'), ('lost', 'مفقود')], default='new', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('expected_close_date', models.DateField()),
                ('is_won', models.BooleanField(default=False)),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.lead')),
            ],
        ),
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField()),
                ('by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.employee')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='crm.lead')),
            ],
        ),
    ]

