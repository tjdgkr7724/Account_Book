from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("worklogs", "0002_payment_boolean")]

    operations = [
        migrations.RenameField(
            model_name="workinfo", old_name="is_paid", new_name="status"
        ),
    ]
