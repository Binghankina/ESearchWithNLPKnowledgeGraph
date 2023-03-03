# -*- coding:utf-8 -*-

import json
import logging
import time
import traceback as tb
from datetime import datetime, timedelta

import requests
from django.core.management.base import BaseCommand

from rest_api.models import ResearchReport
from rest_api.tools.table_process import pretty_table
from touyantong.settings import PDF_PARSER_HOST

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def pdf_batch_parser(self, begin, end, category, action):
        action = int(action)
        if action == 1:
            tags = json.loads(open(__file__.rsplit('/', 3)[0] + '/tags.json', 'r').read())
            category = [tag["abbreviation"] for tag in tags if tag["type_id"] == int(category)]
            items = ResearchReport.objects.filter(category__in=category, created_at__range=[begin, end]).exclude(
                attachment_url=None)
            for item in items:
                payload = {"pdf_url": item.attachment_url[0], "report_id": item.id}
                r = requests.post(PDF_PARSER_HOST,
                                  headers={'Content-Type': 'application/json'},
                                  json=payload,
                                  timeout=300)
                print(r.text)
                time.sleep(1)
        elif action == 2:
            tags = json.loads(open(__file__.rsplit('/', 3)[0] + '/tags.json', 'r').read())
            category = [tag["abbreviation"] for tag in tags if tag["type_id"] == int(category)]
            rr_objs = ResearchReport.objects.filter(category__in=category, created_at__range=[begin, end]).exclude(
                table_raw_data=None)

            for rr_obj in rr_objs:
                try:
                    rr_obj.attachment_content = pretty_table(rr_obj.table_raw_data, rr_obj.category)
                    rr_obj.save()
                except:
                    logger.error("[%s]" % rr_obj.id + tb.format_exc())
        else:
            print("The action is not supported")

    def add_arguments(self, parser):
        parser.add_argument(
            '-b',
            dest='begin',
            default=datetime.now() - timedelta(days=3),
            help="begin time"
        )
        parser.add_argument(
            '-e',
            dest='end',
            default=datetime.now(),
            help="end time"
        )
        parser.add_argument(
            '-c',
            dest='category',
            default=2,
            help="category"
        )
        parser.add_argument(
            '-a',
            dest='action',
            default=2,
            help="action"
        )
    def handle(self, *args, **options):
        self.stdout.write("Begin at %s" % datetime.now())
        self.pdf_batch_parser(options["begin"], options["end"], options["category"], options["action"])
        self.stdout.write("Done at %s" % datetime.now())
