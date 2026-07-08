from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacunacion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campana',
            name='vacuna',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='campanas', to='vacunacion.vacuna'),
        ),
    ]
