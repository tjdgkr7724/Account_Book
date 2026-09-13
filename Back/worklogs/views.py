import calendar
from datetime import date

from django.shortcuts import render
from django.utils import timezone


def calendar_view(request):
    today = timezone.localdate()
    try:
        selected = date.fromisoformat(request.GET.get("date", today.isoformat()))
        # Keep adjacent-month navigation inside Python's supported date range.
        if not 2 <= selected.year <= 9998:
            raise ValueError
    except (ValueError, TypeError):
        selected = today

    year, month = selected.year, selected.month
    previous = date(year - (month == 1), 12 if month == 1 else month - 1, 1)
    following = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
    weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(year, month)
    return render(request, "worklogs/calendar.html", {
        "today": today,
        "selected": selected,
        "previous": previous,
        "following": following,
        "weeks": weeks,
        "weekdays": ["일", "월", "화", "수", "목", "금", "토"],
    })
