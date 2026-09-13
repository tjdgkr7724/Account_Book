from django.db import migrations, models


def copy_payment_status(apps, schema_editor):
    work = apps.get_model("worklogs", "WorkInfo")
    work.objects.using(schema_editor.connection.alias).filter(status="paid").update(is_paid=True)


def restore_payment_status(apps, schema_editor):
    work = apps.get_model("worklogs", "WorkInfo")
    records = work.objects.using(schema_editor.connection.alias)
    records.filter(is_paid=True).update(status="paid")
    records.filter(is_paid=False).update(status="unpaid")


class Migration(migrations.Migration):
    dependencies = [("worklogs", "0001_initial")]

    operations = [
        migrations.RemoveConstraint(
            model_name="workinfo", name="work_info_valid_payment_status"
        ),
        migrations.AddField(
            model_name="workinfo", name="is_paid",
            field=models.BooleanField(default=False, verbose_name="입금 완료"),
        ),
        migrations.RunPython(copy_payment_status, restore_payment_status),
        migrations.RemoveField(model_name="workinfo", name="status"),
    ]
