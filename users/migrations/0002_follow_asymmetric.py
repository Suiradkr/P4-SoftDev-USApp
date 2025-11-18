from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='following',
            field=models.ManyToManyField(related_name='followers', symmetrical=False, to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
