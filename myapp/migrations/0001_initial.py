# Generated by Django 5.0.6 on 2024-06-14 04:53

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('sex', models.CharField(choices=[('Unknown', 'Unknown'), ('Male', 'Male'), ('Female', 'Female')], default='Unknown', max_length=10)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('level', models.IntegerField(default=0)),
                ('score', models.FloatField(default=0.0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
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
            name='Mission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('describle', models.TextField(blank=True, null=True)),
                ('mission_type', models.CharField(choices=[('Goal', 'Goal'), ('Project', 'Project'), ('Task', 'Task'), ('Subtask', 'Subtask')], default='Task', max_length=10)),
                ('mission_period', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Annual', 'Annual'), ('Normal', 'Normal'), ('Angel', 'Angel'), ('Penalty', 'Penalty')], default='Normal', max_length=10)),
                ('mission_priority', models.IntegerField(choices=[(1, 'Not urgent and not important'), (2, 'Urgent but not important'), (3, 'Not urgent but important'), (4, 'Urgent and important')], default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('is_failed', models.BooleanField(default=False)),
                ('is_canceled', models.BooleanField(default=False)),
                ('innitiated_date', models.DateField(auto_now_add=True)),
                ('deadline', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('reward_1', models.CharField(blank=True, max_length=30, null=True)),
                ('reward_2', models.CharField(blank=True, max_length=30, null=True)),
                ('reward_3', models.CharField(blank=True, max_length=30, null=True)),
                ('is_marked', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(max_length=20, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('executor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='missions', to=settings.AUTH_USER_MODEL)),
                ('parent_mission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.mission')),
            ],
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('is_completed', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='myapp.mission')),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confident', models.FloatField(default=10.0)),
                ('decisive', models.FloatField(default=10.0)),
                ('discipline', models.FloatField(default=10.0)),
                ('difficulty_overcoming', models.FloatField(default=10.0)),
                ('resourceful', models.FloatField(default=10.0)),
                ('smart', models.FloatField(default=10.0)),
                ('memorize', models.FloatField(default=10.0)),
                ('deductive', models.FloatField(default=10.0)),
                ('reaction', models.FloatField(default=10.0)),
                ('general_knowledge', models.FloatField(default=10.0)),
                ('planning', models.FloatField(default=10.0)),
                ('power', models.FloatField(default=10.0)),
                ('endurance', models.FloatField(default=10.0)),
                ('agile', models.FloatField(default=10.0)),
                ('resistance', models.FloatField(default=10.0)),
                ('skillful', models.FloatField(default=10.0)),
                ('good_looking', models.FloatField(default=10.0)),
                ('income', models.FloatField(default=10.0)),
                ('asset', models.FloatField(default=10.0)),
                ('financial_management', models.FloatField(default=10.0)),
                ('conversation', models.FloatField(default=10.0)),
                ('friendly', models.FloatField(default=10.0)),
                ('connection', models.FloatField(default=10.0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Special_skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.FloatField(default=10.0)),
                ('registration_date', models.DateField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='mission',
            name='special_skill_reward',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.special_skill'),
        ),
    ]
