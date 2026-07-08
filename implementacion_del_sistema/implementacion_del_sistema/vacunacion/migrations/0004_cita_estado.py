from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacunacion', '0003_backfill_campaign_vacunas'),
    ]

    operations = [
        migrations.AddField(
            model_name='cita',
            name='estado',
            field=models.CharField(choices=[('agendada', 'Agendada'), ('completada', 'Completada'), ('cancelada', 'Cancelada'), ('ausente', 'Ausente')], default='agendada', max_length=20),
        ),
    ]
