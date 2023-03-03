from django.contrib import admin
from company_finance_data.models import Assets, Cash, Profit
# Register your models here.

@admin.register(Assets)
class ResearchReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_id', 'organization_name', 'report_year', 'merge_type')
    ordering = ('-report_year',)


@admin.register(Cash)
class ResearchReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_id', 'organization_name', 'report_year', 'merge_type')
    ordering = ('-report_year',)


@admin.register(Profit)
class ResearchReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_id', 'organization_name', 'report_year', 'merge_type')
    ordering = ('-report_year',)
