# -*- coding:utf-8 -*-

import csv
from company_finance_data.models import Profit, Assets, Cash
import json
from django.core.management.base import BaseCommand
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def dict_process(self, r):
        f_r = {}
        for k, v in r.items():
            v = v.replace("\t", "")
            if k == "organization_id":
                v = int(v)
                f_r.update({k: v})
                continue
            try:
                if v:
                    v = float(v)
                else:
                    v = None
            except ValueError:
                pass
            f_r.update({k: v})
        return f_r

    def load_financ_data(self, csv_dir):
        csv_list = [v for v in os.listdir(csv_dir) if ".csv" in v]
        for csvf in csv_list:
            if "llb" in csvf:
                financ_obj = Cash
            elif "lrb" in csvf:
                financ_obj = Profit
            elif "fzb" in csvf:
                financ_obj = Assets
            else:
                financ_obj = None

            csvf = csv_dir + "/" + csvf
            if not financ_obj:
                continue
            with open(csvf, "r", newline='', encoding='gb2312') as f:
                f_csv = csv.reader(f, dialect='excel')
                field_names = [field.attname for field in financ_obj._meta.get_fields()][1:]
                is_title = True
                for row in f_csv:
                    if is_title:
                        is_title = False
                        continue
                    r = {}
                    row = [v.replace("\t", "") for v in row]
                    for k, v in zip(field_names, row):
                        r.update({k: v})
                    r = self.dict_process(r)
                    financ_obj.objects.get_or_create(**r)
                    self.stdout.write("Writed %s" % r["organization_id"])

    def add_arguments(self, parser):
        parser.add_argument('csv_dir')

    def handle(self, *args, **options):
        csv_dir = options['csv_dir']
        self.stdout.write("Begin at %s" % datetime.now())
        self.load_financ_data(csv_dir)
        self.stdout.write("Done at %s" % datetime.now())

