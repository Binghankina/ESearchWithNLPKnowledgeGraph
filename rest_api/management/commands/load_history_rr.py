# -*- coding:utf-8 -*-

import json
import logging
from django.core.management.base import BaseCommand
from rest_api.models import ResearchReport, Author
import threading
from datetime import datetime
from rest_api.tools.table_process import pretty_table
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    j_p: '_id', 'publish_date', 'stocks_name', 'report_title', 'analyst', 'detail_id', 'research_name', 'level', 'target_increase', 'industry_division', 'concept', 'pdf_url', 'error_message', 'date_created', 'date_updated', 'article', 'title', 'content'
    j_t: '_id', 'analyst', 'article', 'concept', 'date_created', 'date_updated', 'detail_id', 'error_message', 'industry_division', 'level', 'pdf_url', 'publish_date', 'report_title', 'research_name', 'stocks_name', 'tables', 'target_increase', 'title'
    """
    def match_tables(self, t):
        t = json.loads(t)
        rr_obj = ResearchReport.objects.get(article_url=t["_id"])
        try:
            author = Author.objects.filter(analyst_name__in=t["analyst"].split(","))
            author = [v for v in author]
            rr_obj.authors.add(*author)
            rr_obj.save()
        except:
            pass
        # try:
        #     rr_obj.attachment_content = pretty_table(t.get("tables"), rr_obj.category)
        # except:
        #     rr_obj.table_raw_data = None

        rr_obj.table_raw_data = t.get("tables")
        rr_obj.created_at = t.get("publish_date")
        rr_obj.updated_at = t.get("publish_date")
        rr_obj.save()
        print(rr_obj.id)
        pass

    def base_message(self, p):
        d = {"article_url": p["_id"],
             "article_title": p.get("report_title"),
             "article_content": p.get("article"),
             "attachment_url": [p.get("pdf_url")],
             "stocks_name": p.get("stocks_name"),
             "attachment_type": 1,
             "attachment_words": p.get("content"),
             "category": "companyrr",
             }
        ResearchReport.objects.get_or_create(**d)
        pass

    def load_history_rr(self, j_p, j_t):
        j_p = open(j_p, "rU")
        j_t = open(j_t, "rU")
        # num = 1
        # for p in j_p:
        #     if num % 1000 == 0:
        #         print("load base message: (%s/%s)" % (num, "100000"))
        #     p = json.loads(p)
        #     threading.Thread(target=self.base_message(p)).start()
        #     num += 1

        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.map(self.match_tables, j_t)

    def add_arguments(self, parser):
        parser.add_argument("j_p")
        parser.add_argument("j_t")

    def handle(self, *args, **options):
        j_p = options["j_p"]
        j_t = options["j_t"]
        self.stdout.write("Begin at %s" % datetime.now())
        self.load_history_rr(j_p, j_t)
        self.stdout.write("Done at %s" % datetime.now())
