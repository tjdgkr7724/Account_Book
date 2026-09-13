from datetime import date
from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse


class CalendarTests(SimpleTestCase):
    @patch("worklogs.views.timezone.localdate", return_value=date(2026, 9, 14))
    def test_initial_page_selects_today_without_login(self, _today):
        response = self.client.get(reverse("calendar"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected"], date(2026, 9, 14))
        self.assertContains(response, "업무 달력")

    def test_leap_month_and_sunday_first_grid(self):
        response = self.client.get(reverse("calendar"), {"date": "2024-02-29"})
        weeks = response.context["weeks"]
        self.assertEqual(weeks[0][0].weekday(), 6)
        self.assertTrue(all(len(week) == 7 for week in weeks))
        self.assertIn(date(2024, 2, 29), [day for week in weeks for day in week])

    def test_year_navigation(self):
        response = self.client.get(reverse("calendar"), {"date": "2026-01-31"})
        self.assertEqual(response.context["previous"], date(2025, 12, 1))
        response = self.client.get(reverse("calendar"), {"date": "2026-12-31"})
        self.assertEqual(response.context["following"], date(2027, 1, 1))

    @patch("worklogs.views.timezone.localdate", return_value=date(2026, 9, 14))
    def test_invalid_dates_fall_back_to_today(self, _today):
        for value in ["wrong", "2026-02-30", "0001-01-01", "9999-12-31", ""]:
            with self.subTest(value=value):
                response = self.client.get(reverse("calendar"), {"date": value})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["selected"], date(2026, 9, 14))
