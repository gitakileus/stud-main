# Generated by Django 3.2.7 on 2022-03-17 05:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domains', '0004_auto_20220317_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videos',
            name='domain',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_domainls', to='domains.domains'),
        ),
        migrations.AlterField(
            model_name='videos',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_videos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='DomainLeads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain_name', models.CharField(blank=True, max_length=50)),
                ('domain_extension', models.CharField(blank=True, max_length=20)),
                ('business_status', models.SmallIntegerField(blank=True, choices=[(1, 'Buy Now'), (2, 'Price Upon Request'), (3, 'Enquire'), (4, 'Get Price')], null=True)),
                ('buyer_price', models.IntegerField(blank=True, default=0)),
                ('seller_price', models.IntegerField(blank=True, default=0)),
                ('min_offer', models.IntegerField(blank=True, default=0)),
                ('visits', models.IntegerField(blank=True, default=0)),
                ('video_pitch_leads', models.IntegerField(blank=True, default=0)),
                ('startup_breeders', models.CharField(blank=True, max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('trade_option', models.CharField(blank=True, max_length=20)),
                ('domain', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='domainleads_domain', to='domains.domains')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domainleads_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'domainleads',
            },
        ),
    ]
