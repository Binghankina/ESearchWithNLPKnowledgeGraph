# -*- coding:utf-8 -*-

from rest_api.models import Author
from django.core.management.base import BaseCommand
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def is_set_uuid(self, all_info):
        sign = [1 for info in all_info if info.uuid]
        if sign:
            return True
        else:
            return False

    def set_author_uuid(self):
        all_auth_name = [
            analyst_name["analyst_name"] for analyst_name in Author.objects.values("analyst_name").distinct()]
        for auth_name in all_auth_name:
            all_info = Author.objects.filter(analyst_name=auth_name)
            if self.is_set_uuid(all_info):
                unique_code = [info.uuid for info in all_info if info.uuid][0]
                all_info.update(uuid=unique_code)
            else:
                unique_code = uuid.uuid4()
                all_info.update(uuid=unique_code)

    def handle(self, *args, **options):
        self.stdout.write("Begin at %s" % datetime.now())
        self.set_author_uuid()
        self.stdout.write("Done at %s" % datetime.now())
