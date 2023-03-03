# -*- coding:utf-8 -*-

from django.core.management.base import BaseCommand
from rest_api.models import ResearchReport, Author, Estimate
from hashlib import sha256

import json
import logging
import pandas as pd
import numpy as np
import re
import traceback as tb


logger = logging.getLogger(__name__)


pattern = re.compile(r'\d{2}/?\d{2}E')
pattern1 = re.compile(r'\d{2}/?\d{2}[AE]')


keywords = dict(
    revenue_keywords=['营业收入', '营收'],
    net_income_keywords=['净利润', '净亏损', '净利', '净亏'],
    net_income_shareholders_keywords=[
        '归属于母公司股东的净利润', '归属母公司股东的净利润', '归属于上市公司股东的净利润', '归属上市公司股东的净利润'],
    revenue_cost_keywords=['营业成本', '营收成本'],
    operating_income_keywords=['营业利润', '运营利润'],
    total_income_keywords=['利润总额'],
    eps_diluted_keywords=['稀释每股收益', '稀释每股收益（元/股）',
                          '稀释每股收益(元/股)', '稀释每股收益 (元/股)'],
    eps_basic_keywords=['基本每股收益', '基本每股收益（元/股）',
                        '基本每股收益(元/股)', '基本每股收益 (元/股)'],
    short_term_debt_keywords=['短期借款'],
    operating_cashflow_keywords=['经营活动产生的现金流量净额', '经营活动现金流'],
    investing_cashflow_keywords=['投资活动产生的现金流量净额', '投资活动现金流'],
    financing_cashflow_keywords=['筹资活动产生的现金流量净额', '筹资活动现金流'],
    cash_and_equivalents_keywords=['期末现金及现金等价物余额', '现金及现金等价物余额'],
)


def get_header_row(df):
    for i in range(df.shape[0]):
        try:
            if np.any(df.iloc[i, :].str.contains(pattern1, regex=True)):
                return df.iloc[i, :].values.tolist()
        except:
            pass
    return df.iloc[0, :].values.tolist()


def to_single_column(df):
    columns = get_header_row(df)
    t_columns = []
    for c in columns:
        if pattern1.findall(c):
            t_columns.append(c)
    n_columns = 1
    if len(t_columns) % len(set(t_columns)) == 0:
        n_columns = int(len(t_columns) / len(set(t_columns)))
    new_dfs = []
    for i in range(n_columns):
        ndf = df.iloc[:,
                      int(i * len(columns) / n_columns):
                      int((i + 1) * len(columns) / n_columns)]
        ndf.columns = range(len(ndf.columns))
        new_dfs.append(ndf)
    ndf = pd.concat(new_dfs)
#     display(ndf)
    column_mapping = {c: columns.index(c) for c in t_columns}
    return ndf, column_mapping


def get_unit_multiplier(df):
    for i in range(df.shape[1]):
        for s in df.iloc[:, i]:
            if "百万" in str(s):
                return 1e6
            elif "万" in str(s):
                return 1e4
    return 1


def get_key_estimates(df):
    ret = {k[:-len('_keywords')]: None for k in keywords.keys()}
    df, column_mapping = to_single_column(df)

    rows = df.iloc[:, 0].values.tolist()
    for k in ret.keys():
        idx = None
        for keyword in keywords[k + '_keywords']:
            for i in range(len(rows)):
                if rows[i] and keyword in rows[i]:
                    idx = i
                    break
            if idx is not None:
                break
        if idx is not None:
            ret[k] = {c: df.iloc[idx, j] for c, j in column_mapping.items()}
    ret['unit_multiplier'] = get_unit_multiplier(df)
    return ret


def process_table(report, df, table_id):
    estimates = {}
    ret = get_key_estimates(df)
    multiplier = ret['unit_multiplier']
    del ret['unit_multiplier']
    logger.debug(ret)
    for k, v in ret.items():
        if not v:
            continue
        for p in v.keys():
            if p not in estimates.keys():
                estimates[p] = {'unit_multiplier': multiplier}
            value = v[p]
            if isinstance(value, str):
                value = value.strip().replace(',', '')
                if '%' in value:
                    value = value.replace('%', '')
                    value = float(value) / 100
            estimates[p][k] = value
    for p, v in estimates.items():
        Estimate.objects.update_or_create(
            report=report, table_id=table_id, period=p, defaults=v
        )


class Command(BaseCommand):
    help = 'Feed report data'

    def add_arguments(self, parser):
        parser.add_argument('txt_file')
        parser.add_argument('limit')

    def read_and_feed_from_txt_file(self, txt_file, limit=0):
        with open(txt_file) as fd:
            count = 0
            for line in fd.readlines():
                if limit and count >= limit:
                    break
                count += 1
                if not line.strip():
                    continue
                r = json.loads(line)
                authors = []
                for name in r['analyst'].split(','):
                    try:
                        author = Author.objects.get(
                            analyst_name=name,
                            comp_name__contains=r['research_name']
                        )
                        authors.append(author)
                    except:
                        logger.error('Analyst not found: %s@%s' % (
                            name, r['research_name'])
                        )
                        continue

                try:
                    hash = sha256(r['_id'].encode('utf-8')).hexdigest()
                    defaults = {}
                    defaults['article_url'] = r['_id']
                    defaults['article_title'] = r['report_title']
                    try:
                        defaults['article_content'] = r['article']
                    except:
                        defaults['article_content'] = ''
                    try:
                        defaults['attachment_url'] = [r['pdf_url']]
                    except:
                        defaults['attachment_url'] = []
                    defaults['attachment_type'] = 1
                    defaults['created_at'] = r['publish_date']
                    try:
                        defaults['attachment_words'] = r['content']
                    except:
                        defaults['attachment_words'] = ''
                    defaults['stocks_name'] = r['stocks_name']
                    report, created = ResearchReport.objects.update_or_create(
                        hash=hash,
                        defaults=defaults
                    )
                    for author in authors:
                        report.authors.add(author)
                    logger.info('Report added: %s\n' % report)
                    try:
                        if 'tables' not in r.keys():
                            continue
                        tables = r['tables']
                        for k, v in tables.items():
                            if isinstance(v[0], str):
                                v = v[1:]
                            df = pd.DataFrame(v)
                            for i in range(df.shape[0]):
                                if np.any(df.iloc[i, :].str.contains(
                                        pattern, regex=True)):
                                    try:
                                        process_table(report, df, k)
                                    except:
                                        logger.error(tb.format_exc())
                    except:
                        logger.error(tb.format_exc())
                except:
                    logger.error(tb.format_exc())

    def handle(self, *args, **options):
        txt_file = options['txt_file']
        limit = int(options['limit'])
        self.read_and_feed_from_txt_file(txt_file, limit)
