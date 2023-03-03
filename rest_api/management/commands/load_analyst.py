# -*- coding:utf-8 -*-

import json
from rest_api.models import Author
from django.core.management.base import BaseCommand
import logging
from datetime import datetime
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def load_analyst(self, jsonf):
        items = open(jsonf, 'r').read().strip().split('\n')
        items = [json.loads(json.dumps(item, ensure_ascii=False)) for item in items]
        count = len(items)
        num = 1
        for item in items:
            if num % 500 == 0:
                print("(%s/%s)" % (num, count))
            num += 1
            try:
                item = json.loads(item)
            except:
                continue
            positions = list(item.keys())
            positions.remove('basic_info')
            positions.sort()

            for position in positions:
                if item[position].get("CER_NUM"):
                    data = {
                        "sec_id": item[position].get("CER_NUM"),
                        "analyst_name": item["basic_info"].get("RPI_NAME"),
                        "comp_name": item[position].get("AOI_NAME"),
                        "title": item[position].get("PTI_NAME"),
                        "grant_date": item[position].get("OBTAIN_DATE"),
                        "status": item[position].get("CERTC_NAME"),
                        "gender": item["basic_info"].get("SCO_NAME"),
                        "education": item["basic_info"].get("ECO_NAME"),
                        "photo_path": item["basic_info"].get("RPI_PHOTO_PATH")
                    }
                    if positions[-1] == position:
                        data.update({"expire_date": item["basic_info"].get("ARRIVE_DATE")})
                    try:
                        Author.objects.get_or_create(**data)
                    except IntegrityError:
                        pass

    def add_arguments(self, parser):
        parser.add_argument('json_file')

    def handle(self, *args, **options):
        jsonf = options['json_file']
        self.stdout.write("Begin at %s" % datetime.now())
        self.load_analyst(jsonf)
        self.stdout.write("Done at %s" % datetime.now())
