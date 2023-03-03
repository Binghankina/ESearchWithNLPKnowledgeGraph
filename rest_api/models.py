from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.auth.models import User


class ResearchReport(models.Model):
    article_url = models.URLField(default="", blank=True, null=True)
    article_title = models.CharField(
        max_length=200, default="", blank=True, null=True)
    article_content = models.TextField(default="", blank=True, null=True)
    attachment_url = ArrayField(models.URLField(), blank=True)
    attachment_type = models.IntegerField()
    attachment_content = JSONField(default=None, blank=True, null=True)
    table_raw_data = models.TextField(default="", blank=True, null=True)
    attachment_words = models.TextField(default="", blank=True, null=True)
    attachment_images = ArrayField(JSONField(default=None, blank=True, null=True),
                                   blank=True, null=True, default=[])
    authors = models.ManyToManyField('Author', blank=True)
    pages = models.IntegerField(default=0, blank=True, null=True)
    category = models.CharField(
        max_length=50, default="", blank=True, null=True)
    stocks_name = models.CharField(
        max_length=50, default="", blank=True, null=True)
    hash = models.CharField(max_length=256, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % str(self.id)


class Author(models.Model):
    sec_id = models.CharField(primary_key=True, max_length=100)
    analyst_name = models.CharField(
        default="", null=True, blank=True, max_length=100)
    comp_name = models.CharField(
        default="", null=True, blank=True, max_length=100)
    title = models.CharField(default="", null=True, blank=True, max_length=100)
    grant_date = models.DateField(null=True, blank=True)
    expire_date = models.DateField(null=True, blank=True)
    status = models.CharField(default="", null=True,
                              blank=True, max_length=100)
    gender = models.CharField(default="", null=True,
                              blank=True, max_length=100)
    education = models.CharField(
        default="", null=True, blank=True, max_length=100)
    photo_path = models.URLField(default="", null=True, blank=True)
    uuid = models.CharField(null=True, max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.analyst_name, self.sec_id)


class Estimate(models.Model):
    report = models.ForeignKey(ResearchReport, related_name='estimates')
    table_id = models.CharField(max_length=20)
    period = models.CharField(max_length=10)
    revenue = models.FloatField(null=True)
    net_income = models.FloatField(null=True)
    net_income_shareholders = models.FloatField(null=True)
    revenue_cost = models.FloatField(null=True)
    operating_income = models.FloatField(null=True)
    total_income = models.FloatField(null=True)
    eps_diluted = models.FloatField(null=True)
    eps_basic = models.FloatField(null=True)
    short_term_debt = models.FloatField(null=True)
    operating_cashflow = models.FloatField(null=True)
    investing_cashflow = models.FloatField(null=True)
    financing_cashflow = models.FloatField(null=True)
    cash_and_equivalents = models.FloatField(null=True)
    unit_multiplier = models.FloatField(null=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribe_list = ArrayField(
        models.CharField(max_length=50, default=""),
        default=[])
    favorites_list = ArrayField(
        models.IntegerField(default=0),
        default=[])


class WeChatUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openid = models.CharField(max_length=50, primary_key=True)
    unionid = models.CharField(max_length=50, default='', null=True)
    nickname = models.CharField(max_length=50, default='', null=True)
    sex = models.IntegerField(default=1)
    language = models.CharField(max_length=200, default='en')
    city = models.CharField(max_length=200, default='')
    province = models.CharField(max_length=200, default='')
    country = models.CharField(max_length=200, default='')
    headimgurl = models.TextField(default='')

