# -*- coding:utf-8 -*-

from rest_api.models import ResearchReport
from rest_api.es import index_report
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        count = ResearchReport.objects.all().count()
        for i in range(count):
            try:
                rr_obj = ResearchReport.objects.get(id=i+1)
            except ResearchReport.DoesNotExist:
                continue
            self.stdout.write('Indexing %s ...\n' % rr_obj.article_title)
            index_report(rr_obj)
