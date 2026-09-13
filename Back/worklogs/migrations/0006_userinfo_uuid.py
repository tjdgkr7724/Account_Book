import uuid

from django.db import migrations, models


def populate_uuids(apps, schema_editor):
    users = apps.get_model("worklogs", "UserInfo").objects.using(schema_editor.connection.alias)
    for user in users.filter(uuid__isnull=True).iterator():
        users.filter(pk=user.pk).update(uuid=uuid.uuid4())


class Migration(migrations.Migration):
    dependencies = [("worklogs", "0005_userinfo_birth_date")]

    operations = [
        migrations.AddField(
            model_name="userinfo", name="uuid",
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.RunPython(populate_uuids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="userinfo", name="uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]
