from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("worklogs", "0003_rename_is_paid_status")]

    operations = [
        migrations.RenameField(
            model_name="userinfo", old_name="pwd", new_name="password"
        ),
    ]
