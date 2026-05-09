from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pob', '0004_pobcategory'),
    ]

    operations = [
        # POBPerson.category
        migrations.AlterField(
            model_name='pobperson',
            name='category',
            field=models.CharField(db_index=True, default='KSD_CREW', max_length=50),
        ),
        # POBEmployee.category
        migrations.AlterField(
            model_name='pobemployee',
            name='category',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
