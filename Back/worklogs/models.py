from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class UserInfo(models.Model):
    id           = models.CharField("로그인 ID", max_length=150, primary_key=True)
    name         = models.CharField("이름", max_length=100)
    password     = models.CharField("비밀번호 해시", max_length=128, editable=False, default="!")
    phone_number = models.CharField("전화번호", max_length=30)
    birth_date   = models.DateField("생년월일", null=True, blank=True)

    class Meta:
        db_table     = "user_info"
        verbose_name = "사용자 정보"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name


class WorkInfo(models.Model):
    user = models.ForeignKey(
        UserInfo, verbose_name="사용자", on_delete=models.PROTECT, related_name="work_records"
    )
    company_name = models.CharField              ("업체명", max_length=200)
    workplace    = models.CharField              ("근무지", max_length=255)
    work_date    = models.DateField              ("날짜")
    industry     = models.CharField              ("업종", max_length=100)
    amount       = models.PositiveBigIntegerField("금액(원)")
    status       = models.BooleanField           ("입금 완료", default=False)
    notes        = models.TextField              ("비고", blank=True)
    created_at   = models.DateTimeField          ("입력 날짜", auto_now_add=True)
    updated_at   = models.DateTimeField          ("수정 날짜", auto_now=True)

    class Meta:
        db_table = "work_info"
        ordering = ["-work_date", "-pk"]

    @property
    def name(self):
        return self.user.name

    def __str__(self):
        return f"{self.name} / {self.work_date} / {self.company_name}"
