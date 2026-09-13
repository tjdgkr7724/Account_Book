from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from .models import UserInfo


class LoginForm(forms.Form):
    id = forms.CharField(label="로그인 ID", max_length=150, widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}))
    password = forms.CharField(label="비밀번호", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))
    birth_date = forms.RegexField(
        label="생년월일", regex=r"\A[0-9]{6}\Z", strip=False,
        help_text="생년월일 6자리를 입력하세요. 예: 1901-01-01 → 010101",
        error_messages={"invalid": "생년월일은 숫자 6자리로 입력해 주세요."},
        widget=forms.TextInput(attrs={"inputmode": "numeric", "maxlength": "6", "pattern": "[0-9]{6}", "placeholder": "예: 010101", "autocomplete": "off"}),
    )


class SignupForm(LoginForm):
    birth_date = forms.DateField(label="생년월일", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["birth_date"].widget.attrs["max"] = timezone.localdate().isoformat()

    def clean_birth_date(self):
        value = self.cleaned_data["birth_date"]
        if value > timezone.localdate():
            raise forms.ValidationError("생년월일은 미래 날짜일 수 없습니다.")
        return value


    name = forms.CharField(label="이름", max_length=100, widget=forms.TextInput(attrs={"autocomplete": "name"}))
    phone_number = forms.CharField(label="전화번호", max_length=30, widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}))
    password = forms.CharField(label="비밀번호", strip=False, help_text="8자 이상으로, 흔한 비밀번호나 숫자로만 된 비밀번호는 사용할 수 없습니다.", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password_confirm = forms.CharField(label="비밀번호 확인", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    field_order = ["id", "name", "phone_number", "birth_date", "password", "password_confirm"]

    def clean_id(self):
        value = self.cleaned_data["id"]
        if UserInfo.objects.filter(pk=value).exists():
            raise forms.ValidationError("이미 사용 중인 ID입니다.")
        return value

    def clean(self):
        data = super().clean()
        password = data.get("password")
        if password:
            user = User(username=data.get("id", ""), first_name=data.get("name", ""))
            try:
                validate_password(password, user=user)
            except forms.ValidationError as error:
                self.add_error("password", error)
        if password and data.get("password_confirm") and password != data["password_confirm"]:
            self.add_error("password_confirm", "비밀번호가 일치하지 않습니다.")
        return data
