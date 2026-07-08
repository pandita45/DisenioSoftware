from django.db import migrations


def backfill_campaign_vaccines(apps, schema_editor):
    Campana = apps.get_model('vacunacion', 'Campana')
    Vacuna = apps.get_model('vacunacion', 'Vacuna')

    mappings = [
        ('influenza', 'Influenza'),
        ('covid', 'COVID-19 Bivalente'),
        ('hepatitis', 'Hepatitis B'),
        ('tétanos', 'Tétanos-Difteria'),
        ('tetanos', 'Tétanos-Difteria'),
    ]

    for campana in Campana.objects.filter(vacuna__isnull=True):
        nombre = (campana.nombre or '').lower()
        vacuna = None
        for keyword, vacuna_nombre in mappings:
            if keyword in nombre:
                vacuna = Vacuna.objects.filter(nombre__iexact=vacuna_nombre).first()
                if vacuna:
                    break

        if vacuna:
            campana.vacuna = vacuna
            campana.save(update_fields=['vacuna'])


class Migration(migrations.Migration):
    dependencies = [
        ('vacunacion', '0002_campana_vacuna'),
    ]

    operations = [
        migrations.RunPython(backfill_campaign_vaccines, migrations.RunPython.noop),
    ]
