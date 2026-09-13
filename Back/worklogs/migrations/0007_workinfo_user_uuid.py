import django.db.models.deletion
from django.db import migrations, models


def copy_owner_uuid(apps, schema_editor):
    alias = schema_editor.connection.alias
    users = apps.get_model("worklogs", "UserInfo").objects.using(alias)
    records = apps.get_model("worklogs", "WorkInfo").objects.using(alias)
    for user in users.iterator():
        records.filter(user_id=user.pk).update(uuid_owner_id=user.uuid)


def restore_owner_id(apps, schema_editor):
    alias = schema_editor.connection.alias
    users = apps.get_model("worklogs", "UserInfo").objects.using(alias)
    records = apps.get_model("worklogs", "WorkInfo").objects.using(alias)
    for user in users.iterator():
        records.filter(uuid_owner_id=user.uuid).update(user_id=user.pk)


class Migration(migrations.Migration):
    dependencies = [("worklogs", "0006_userinfo_uuid")]

    operations = [
        migrations.AlterField(
            model_name="workinfo", name="user",
            field=models.ForeignKey(to="worklogs.userinfo", null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="work_records", verbose_name="사용자"),
        ),
        migrations.AddField(
            model_name="workinfo", name="uuid_owner",
            field=models.ForeignKey(to="worklogs.userinfo", to_field="uuid",
                db_column="user_uuid", null=True, related_name="+",
                on_delete=django.db.models.deletion.PROTECT, verbose_name="사용자"),
        ),
        migrations.RunPython(copy_owner_uuid, restore_owner_id),
        migrations.RemoveField(model_name="workinfo", name="user"),
        migrations.RenameField(model_name="workinfo", old_name="uuid_owner", new_name="user"),
        migrations.AlterField(
            model_name="workinfo", name="user",
            field=models.ForeignKey(to="worklogs.userinfo", to_field="uuid",
                db_column="user_uuid", related_name="work_records",
                on_delete=django.db.models.deletion.PROTECT, verbose_name="사용자"),
        ),
    ]
