# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0017_userflag_emailed'),
    ]

    operations = [
        migrations.AddField(
            model_name='userflag',
            name='status',
            field=models.CharField(default=b'new', max_length=32, choices=[(b'new', b'New'), (b'first_warning', b'Warned Once'), (b'second_warning', b'Warned Twice'), (b'final_warning', b'Canceled')]),
        ),
    ]
