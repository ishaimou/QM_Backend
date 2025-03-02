# Generated by Django 2.2.6 on 2020-10-02 17:10

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(max_length=50, unique=True, verbose_name='email address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Departement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Docks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_id', models.IntegerField(blank=True, null=True, verbose_name='Inspection ID')),
                ('which_dock', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Halt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('possible_cause', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='HaltEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='IncidentEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Origin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Port name')),
                ('docks', models.IntegerField(verbose_name='Number of docks')),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vessel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('photo', models.FileField(blank=True, max_length=255, null=True, upload_to='vessel/')),
                ('holds_nbr', models.IntegerField(blank=True, null=True, verbose_name='number of holds in this vessel')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_refused', models.BooleanField(default=True, verbose_name='User refused')),
                ('company_name', models.CharField(max_length=150)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('cin', models.CharField(blank=True, max_length=8, null=True)),
                ('tel', models.CharField(blank=True, max_length=24, null=True)),
                ('department', models.ManyToManyField(to='inspection.Departement')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductFamily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('product_type_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.ProductType')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('product_family_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.ProductFamily')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('product_category_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.ProductCategory')),
            ],
        ),
        migrations.CreateModel(
            name='Loading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nor_tendered_date', models.DateTimeField(blank=True, null=True)),
                ('loading_order_date', models.DateTimeField(blank=True, null=True)),
                ('loading_starting_date', models.DateTimeField(blank=True, null=True)),
                ('loading_end_date', models.DateTimeField(blank=True, null=True)),
                ('cargo_condition', models.CharField(blank=True, choices=[('GOOD', 'Clean Cargo'), ('BAD', 'Presence of a quality incident')], max_length=50, null=True)),
                ('air_temperature', models.CharField(blank=True, max_length=50, null=True)),
                ('humidity_percentage', models.CharField(blank=True, max_length=50, null=True)),
                ('uld_test_date', models.DateTimeField(blank=True, null=True)),
                ('initial_draugth_surv', models.DateTimeField(blank=True, null=True)),
                ('final_draugth_surv', models.DateTimeField(blank=True, null=True)),
                ('Quantity', models.IntegerField(blank=True, null=True)),
                ('loading_port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='port_name', to='inspection.Port')),
            ],
        ),
        migrations.CreateModel(
            name='IntermediateDraughtSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_inter_draugth_surv', models.DateTimeField()),
                ('end_inter_draugth_surv', models.DateTimeField()),
                ('loading_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.Loading')),
            ],
        ),
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_status', models.CharField(choices=[('INPROGRESS', 'INPROGRESS'), ('CLOSED', 'CLOSED'), ('ONHOLD', 'ONHOLD'), ('PENDED', 'PENDED')], default='INPROGRESS', max_length=50)),
                ('vessel_status', models.CharField(blank=True, max_length=50, null=True)),
                ('vessel_arrived', models.DateTimeField(null=True)),
                ('vessel_breathed', models.DateTimeField()),
                ('inspection_date', models.DateTimeField(blank=True, null=True)),
                ('inspection_date_end', models.DateTimeField(blank=True, null=True)),
                ('foreign_inspector', models.BooleanField(default=False)),
                ('holds_filled', models.IntegerField(null=True)),
                ('dock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.Docks')),
                ('loading_ref', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='inspection.Loading')),
                ('user_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('vessel_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.Vessel')),
            ],
        ),
        migrations.CreateModel(
            name='IncidentSpecs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qte_by_kgs', models.IntegerField(blank=True, null=True)),
                ('temperature', models.CharField(blank=True, max_length=50, null=True)),
                ('possible_cause', models.CharField(blank=True, max_length=50, null=True)),
                ('humidity_rate', models.CharField(blank=True, max_length=50, null=True)),
                ('photo', models.FileField(blank=True, null=True, upload_to='incident/')),
                ('incident_event_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.IncidentEvent')),
            ],
        ),
        migrations.CreateModel(
            name='IncidentDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('halt_or_incident', models.CharField(choices=[('Halt', 'Halt_incident'), ('Incident', 'Quanlity_incident')], max_length=50)),
                ('stopping_hour', models.DateTimeField()),
                ('resuming_hour', models.DateTimeField(blank=True, null=True)),
                ('related', models.CharField(choices=[('WEATHER', 'WEATHER'), ('PRODUCT', 'PRODUCT'), ('HALT', 'HALT')], max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('halt_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.Halt')),
                ('incident_spec_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.IncidentSpecs')),
                ('inspection_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.Inspection')),
            ],
        ),
        migrations.CreateModel(
            name='HourlyCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=4)),
                ('humidity', models.DecimalField(decimal_places=2, max_digits=5)),
                ('debit', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('ambient_temperature', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('date', models.DateTimeField()),
                ('inspection_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.Inspection')),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.Origin')),
            ],
        ),
        migrations.AddField(
            model_name='halt',
            name='halt_event_ref',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.HaltEvent'),
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=256, upload_to='')),
                ('client_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.Client')),
                ('hourlycheck_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.HourlyCheck')),
                ('incident_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.IncidentDetails')),
                ('inspection_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.Inspection')),
                ('product_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.Product')),
                ('survey_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.IntermediateDraughtSurvey')),
            ],
        ),
        migrations.CreateModel(
            name='ClientLoadingDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bl_figure_mt', models.IntegerField(blank=True, null=True)),
                ('bl_figure_mt_photo', models.FileField(blank=True, null=True, upload_to='bl/')),
                ('loaded', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('client_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.Client')),
                ('loading_ref', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.Loading')),
                ('origin_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.Origin')),
                ('product_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.Product')),
            ],
        ),
    ]
