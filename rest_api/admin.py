from django.contrib import admin
from rest_api.models import ResearchReport, Author, UserProfile, WeChatUser
from django.contrib.admin import SimpleListFilter
import json
from touyantong.settings import TAGS
# Register your models here.


class ResearchOrganizationFilter(SimpleListFilter):
    title = '研究机构'
    parameter_name = 'research_organization'

    def lookups(self, request, model_admin):
        r = [(tag["abbreviation"], tag["title"]) for tag in TAGS]
        return r

    def queryset(self, request, queryset):
        qs = queryset
        if self.value():
            qs = queryset.filter(category=self.value())
        return qs


@admin.register(ResearchReport)
class ResearchReportAdmin(admin.ModelAdmin):
    list_filter = [ResearchOrganizationFilter, ]
    list_display = ('id', 'article_title', 'created_at', 'updated_at')
    search_fields = ['article_url', 'article_title']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['sec_id', 'analyst_name', 'comp_name', 'title']
    list_display = ('sec_id', 'analyst_name', 'comp_name', 'title', 'grant_date', 'expire_date')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribe_list')


@admin.register(WeChatUser)
class WeChatUserAdmin(admin.ModelAdmin):
    list_display = ('openid', 'nickname')

