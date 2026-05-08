from django.db import migrations, models


DEFAULT_CATEGORIES = [
    ('VEDANTA_PERSON',  'Vedanta Person',      1),
    ('VEDANTA_VISITOR', 'Vedanta Visitor',     2),
    ('VEDANTA_SERVICE', 'Vedanta Services',    3),
    ('VEDANTA_DRIVER',  'Vedanta Driver',      4),
    ('KSD_CREW',        'KSD Drilling Crew',   5),
    ('CONTRACTOR',      'Contractor / Vendor', 6),
    ('OTHER',           'Other',               7),
]


def seed_categories(apps, schema_editor):
    POBCategory = apps.get_model('pob', 'POBCategory')
    for key, label, order in DEFAULT_CATEGORIES:
        POBCategory.objects.get_or_create(key=key, defaults={'label': label, 'sort_order': order})


def unseed_categories(apps, schema_editor):
    pass  # nothing to reverse


class Migration(migrations.Migration):

    dependencies = [
        ('pob', '0003_pobemployee'),
    ]

    operations = [
        migrations.CreateModel(
            name='POBCategory',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key',        models.CharField(help_text='Internal key stored on POBPerson.category', max_length=50, unique=True)),
                ('label',      models.CharField(max_length=100)),
                ('sort_order', models.IntegerField(default=0)),
                ('is_active',  models.BooleanField(default=True)),
            ],
            options={'ordering': ['sort_order', 'label']},
        ),
        migrations.RunPython(seed_categories, unseed_categories),
    ]
