from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0005_alter_post_options_post_canonical_url_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={
                'ordering': ('-datetime_created',),
                'verbose_name': 'نوشته',
                'verbose_name_plural': 'نوشته ها',
            },
        ),
    ]
