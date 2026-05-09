from django.db import migrations


def add_ksd_3rd_party(apps, schema_editor):
    POBCategory = apps.get_model('pob', 'POBCategory')
    POBCategory.objects.get_or_create(
        key='KSD_3RD_PARTY',
        defaults={'label': 'KSD 3rd Party', 'sort_order': 6, 'is_active': True}
    )
    # Shift CONTRACTOR and OTHER sort_order down by 1
    POBCategory.objects.filter(key='CONTRACTOR').update(sort_order=7)
    POBCategory.objects.filter(key='OTHER').update(sort_order=8)


def reverse_ksd_3rd_party(apps, schema_editor):
    apps.get_model('pob', 'POBCategory').objects.filter(key='KSD_3RD_PARTY').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pob', '0005_fix_category_maxlength'),
    ]

    operations = [
        migrations.RunPython(add_ksd_3rd_party, reverse_ksd_3rd_party),
    ]
