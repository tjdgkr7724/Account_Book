import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.middleware.csrf import rotate_token
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_http_methods

from .forms import LoginForm, SignupForm
from .models import UserInfo


def session_user(request):
    user_uuid = request.session.get("worklogs_user_uuid")
    if user_uuid is None:
        return None
    try:
        user = UserInfo.objects.filter(uuid=user_uuid, birth_date__isnull=False).first()
    except (ValidationError, ValueError, TypeError):
        user = None
    if user is None:
        request.session.pop("worklogs_user_uuid", None)
    return user


def home_view(request):
    return redirect("calendar" if session_user(request) else "login")


@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    if session_user(request):
        return redirect("calendar")
    initial = {"id": request.session.pop("signup_id", "")} if request.method == "GET" else None
    form = LoginForm(request.POST if request.method == "POST" else None, initial=initial)
    if request.method == "POST" and form.is_valid():
        user = UserInfo.objects.filter(pk=form.cleaned_data["id"]).first()
        password_ok = user.check_password(form.cleaned_data["password"]) if user else False
        if user is None:
            make_password(form.cleaned_data["password"])
        if password_ok and user.birth_date and user.birth_date.strftime("%y%m%d") == form.cleaned_data["birth_date"]:
            request.session.cycle_key()
            request.session.pop("worklogs_user_id", None)
            request.session["worklogs_user_uuid"] = str(user.uuid)
            rotate_token(request)
            return redirect("calendar")
        form.add_error(None, "ID, 비밀번호 또는 생년월일이 일치하지 않습니다.")
    return render(request, "worklogs/auth.html", {"form": form, "signup": False})


@never_cache
@require_http_methods(["GET", "POST"])
def signup_view(request):
    if session_user(request):
        return redirect("calendar")
    form = SignupForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = UserInfo(**{key: form.cleaned_data[key] for key in ("id", "name", "phone_number", "birth_date")})
        user.set_password(form.cleaned_data["password"])
        try:
            with transaction.atomic():
                user.save(force_insert=True)
        except IntegrityError:
            form.add_error("id", "이미 사용 중인 ID입니다.")
        else:
            request.session["signup_id"] = user.pk
            messages.success(request, "회원가입이 완료되었습니다. 로그인해 주세요.")
            return redirect("login")
    return render(request, "worklogs/auth.html", {"form": form, "signup": True})


@require_POST
def logout_view(request):
    request.session.flush()
    return redirect("login")


@never_cache
def calendar_view(request):
    user = session_user(request)
    if user is None:
        return redirect("login")
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
        "work_records": user.work_records.filter(work_date=selected),
        "weekdays": ["일", "월", "화", "수", "목", "금", "토"],
    })


@never_cache
@require_http_methods(["GET"])
def work_records_view(request):
    user = session_user(request)
    if user is None:
        return JsonResponse({"error": "로그인이 필요합니다."}, status=401)
    # Ownership comes exclusively from the authenticated session, never query parameters.
    records = user.work_records.all()
    if "date" in request.GET:
        try:
            selected = date.fromisoformat(request.GET["date"])
        except (ValueError, TypeError):
            return JsonResponse({"error": "날짜 형식은 YYYY-MM-DD입니다."}, status=400)
        records = records.filter(work_date=selected)
    return JsonResponse({"user_uuid": str(user.uuid), "records": list(records.values(
        "id", "company_name", "workplace", "work_date", "industry", "amount",
        "status", "notes", "created_at", "updated_at",
    ))})
