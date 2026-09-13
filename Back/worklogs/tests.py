from datetime import date

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class PaymentMigrationTests(TransactionTestCase):
    def test_existing_payment_states_survive_forward_and_reverse_migration(self):
        old = [("worklogs", "0001_initial")]
        new = [("worklogs", "0003_rename_is_paid_status")]
        executor = MigrationExecutor(connection)
        executor.migrate(old)
        try:
            apps = executor.loader.project_state(old).apps
            user = apps.get_model("worklogs", "UserInfo").objects.create(
                id="test", name="테스트", phone_number="010-0000-0000"
            )
            work = apps.get_model("worklogs", "WorkInfo")
            for status in ["paid", "unpaid"]:
                work.objects.create(
                    user=user, company_name=status, workplace="서울",
                    work_date=date(2026, 9, 14), industry="개발", amount=100000,
                    status=status,
                )
            executor = MigrationExecutor(connection)
            executor.migrate(new)
            work = executor.loader.project_state(new).apps.get_model("worklogs", "WorkInfo")
            self.assertIs(work.objects.get(company_name="paid").status, True)
            self.assertIs(work.objects.get(company_name="unpaid").status, False)
            self.assertIs(work._meta.get_field("status").get_default(), False)
            executor = MigrationExecutor(connection)
            executor.migrate(old)
            work = executor.loader.project_state(old).apps.get_model("worklogs", "WorkInfo")
            self.assertEqual(work.objects.get(company_name="paid").status, "paid")
            self.assertEqual(work.objects.get(company_name="unpaid").status, "unpaid")
        finally:
            MigrationExecutor(connection).migrate(new)
