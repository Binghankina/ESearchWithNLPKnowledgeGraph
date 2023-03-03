#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from collections import OrderedDict
from rest_api.tools.table_process import pretty_table

class Earnings(object):
    def __init__(self, **kargs):
        super(Earnings, self).__init__()
        self.__dict__.update(kargs)

        self.REVENUE_KWS = ['营业收入', '营收']
        self.NET_INCOME_KWS = [
            '净利润',
            '净亏损',
            '净利',
            '净亏']
        self.NET_INCOME_SHAREHOLDERS_KWS = [
            '归属于上市公司股东的净利润',
            '归属于母公司股东的净利润',
            '归属母公司股东的净利润',
            '归属上市公司股东的净利润']
        self.REVENUE_COST_KWS = ['营业成本', '营收成本']
        self.OPT_INCOME_KWS = [
            '归属于上市公司股东的扣除非经常性损益的净利润',
            '归属于上市公司股东的扣除非经常性损益后的净利润',
            '营业利润',
            '运营利润']
        self.GROSS_INCOME_KWS = ['利润总额']
        self.EPS_DILUTED_KWS = ['稀释每股收益']
        self.EPS_BASIC_KWS = ['基本每股收益']
        self.SHORT_TERM_DEBT_KWS = ['短期借款']
        self.OPT_CASHFLOW_KWS = ['经营活动产生的现金流量净额', '经营活动现金流']
        self.INVESTING_CASHFLOW_KWS = ['投资活动产生的现金流量净额', '投资活动现金流']
        self.FINANCING_CASHFLOW_KWS = ['筹资活动产生的现金流量净额', '筹资活动现金流']
        self.CASH_AND_EQUIVALENTS_KWS = ['期末现金及现金等价物余额', '现金及现金等价物余额']
        self.ASSETS_KWS = ['总资产']
        self.ASSETS_SHAREHOLDERS_KWS = ['归属于上市公司股东的净资产']
        self.OUTLOOK_EXPLANATION_KWS = ['业绩变动的原因说明']

    def GetReportSeason(self, str):
        if not(re.search(r'\d{4}\s*年\w+三季度报告', str) is None):
            return '三季'
        elif not(re.search(r'\d{4}\s*年\w+半年度报告', str) is None):
            return '半年'
        elif not(re.search(r'\d{4}\s*年年度报告', str) is None):
            return '全年'
        elif not(re.search(r'\d{4}\s*年\w+一季度报告', str) is None):
            return '一季'
        else:
            return ''

    def GetReportYear(self, str):
        return re.search(r'(\d{4})\s*年\w+报告', str).group(1)

    def GetCompanyCode(self, str):
        try:
            r = re.search(r'证券代码[:：]\s*(\d{6})\s+', str).group(1)
        except AttributeError:
            try:
                r = re.search(r'公司代码[:：]\s*(\d{6})\s+', str).group(1)
            except AttributeError:
                r = ''
        return r

    def GetCompanyName(self, str):
        try:
            r = re.search(r'证券简称[:：]\s*(\w+)\s+', str).group(1)
        except AttributeError:
            try:
                r = re.search(r'公司简称[:：]\s*(\w+)\s+', str).group(1)
            except AttributeError:
                r = ''
        return r

    # r = re.findall(r'[。，；”\s](\w+)原因\w*[：，。；“]', p)

    # merge all rows (list) in data['tables'] into one big list
    def JoinTable(self, table_dict):
        l = []
        for k, v in table_dict.items():
            l = l + v
        return l

    def LocateKeyword(self, table_dict, keyword):
        d = {
            'table_id': '',
            'row_num': '',
            'col_num': ''
        }
        for k, v in table_dict.items():
            for i in v:
                d['table_id'] = k
                row_count = 0
                for row in v:
                    col_count = 0
                    for word in row:
                        if keyword in word:
                            d['col_num'] = col_count
                            break
                        col_count += 1
                    if d['col_num'] != '':
                        d['row_num'] = row_count
                        break
                    row_count += 1
                if d['col_num'] != '' and d['row_num'] != '':
                    break
            if d['col_num'] != '' and d['row_num'] != '':
                break

        return d

    def LocateKeywordByList(self, table_dict, keyword_list):
        for kw in keyword_list:
            d = self.LocateKeyword(table_dict, kw)
            if d['row_num'] != '':
                break
        return d

    def LocateHeaders(self, table_dict, para_str):
        d = {}
        revenue_header = self.LocateKeyword(table_dict, '营业收入')
        assets_header = self.LocateKeyword(table_dict, '总资产')

        try:
            header_row = table_dict[revenue_header['table_id']
                                    ][revenue_header['row_num'] - 1]
        except KeyError:
            raise
        for i in range(0, len(header_row)):
            if header_row[i].strip() == '本报告期':
                d['current_revenue_col'] = i
            elif '本报告期比' in header_row[i]:
                d['current_revenue_yoy'] = i
            elif re.search(r'{}\s*年'.format(self.GetReportYear(para_str)), header_row[i].strip()) is not None:
                d['current_revenue_col'] = i
            elif '本年比上年' in header_row[i]:
                d['current_revenue_yoy'] = i

        try:
            header_row = table_dict[assets_header['table_id']
                                    ][assets_header['row_num'] - 1]
        except KeyError:
            raise
        for i in range(0, len(header_row)):
            if header_row[i].strip() == '本报告期末':
                d['current_assets_col'] = i
            elif '本报告期末比' in header_row[i]:
                d['current_assets_yoy'] = i
            elif re.search(r'{}\s*年末'.format(self.GetReportYear(para_str)), header_row[i].strip()) is not None:
                d['current_assets_col'] = i
            elif '本年末比上年' in header_row[i]:
                d['current_assets_yoy'] = i

        try:
            return {
                'rev_col': d['current_revenue_col'],
                'rev_yoy': d['current_revenue_yoy'],
                'ass_col': d['current_assets_col'],
                'ass_yoy': d['current_assets_yoy']
            }
        except KeyError:
            raise

    def ConvertNumber(self, str_num):
        num = re.sub(r'[,元人民币）\)]', '', str_num)
        num = re.sub(r'[（\(]', '-', num)
        try:
            num = float(num.strip())
        except Exception:
            print('[ERROR] could not convert number: {}'.format(num))
            return ''
        if num >= 100000000:
            return '{:.2f}亿元'.format(num / 100000000)
        elif num >= 10000:
            return '{:.0f}万元'.format(num / 10000)
        else:
            return '{}元'.format(num)

    def ConvertPercentage(self, str_num):
        num = re.sub(r'[,%）\)]', '', str_num)
        num = re.sub(r'[（\(]', '-', num)
        try:
            num = float(num.strip())
        except Exception:
            print('[ERROR] could not convert number: {}'.format(num))
            return ''
        if num >= 0:
            return '增长{}%'.format(num)
        else:
            return '减少{}%'.format(abs(num))

    def RetrieveEarningData(self, t, p):
        year = self.GetReportYear(p)
        quarter = self.GetReportSeason(p)
        # company = self.GetCompanyName(p)
        # stock = self.GetCompanyCode(p)
        company = ''
        stock = ''

        # Headers
        h = self.LocateHeaders(t, p)
        print('[INFO] Printing Located Headers: \n', h)
        # 营业收入
        rev_loc = self.LocateKeywordByList(t, self.REVENUE_KWS)
        revenue = t[rev_loc['table_id']][rev_loc['row_num']][h['rev_col']]
        revenue_yoy = t[rev_loc['table_id']][rev_loc['row_num']][h['rev_yoy']]
        # 归属上市公司股东净利润
        net_loc = self.LocateKeywordByList(t, self.NET_INCOME_KWS)
        net_income = t[net_loc['table_id']][net_loc['row_num']][h['rev_col']]
        net_income_yoy = t[net_loc['table_id']
                           ][net_loc['row_num']][h['rev_yoy']]
        # 运营利润
        opt_income_loc = self.LocateKeywordByList(t, self.OPT_INCOME_KWS)
        opt_income = t[opt_income_loc['table_id']
                       ][opt_income_loc['row_num']][h['rev_col']]
        opt_income_yoy = t[opt_income_loc['table_id']
                           ][opt_income_loc['row_num']][h['rev_yoy']]
        # 经营现金流
        opt_cashflow_loc = self.LocateKeywordByList(t, self.OPT_CASHFLOW_KWS)
        opt_cashflow = t[opt_cashflow_loc['table_id']
                         ][opt_cashflow_loc['row_num']][h['rev_col']]
        opt_cashflow_yoy = t[opt_cashflow_loc['table_id']
                             ][opt_cashflow_loc['row_num']][h['rev_yoy']]
        # 基本每股收益
        eps_basic_loc = self.LocateKeywordByList(t, self.EPS_BASIC_KWS)
        eps_basic = t[eps_basic_loc['table_id']
                      ][eps_basic_loc['row_num']][h['rev_col']]
        eps_basic_yoy = t[eps_basic_loc['table_id']
                          ][eps_basic_loc['row_num']][h['rev_yoy']]
        # 稀释每股收益
        eps_diluted_loc = self.LocateKeywordByList(t, self.EPS_DILUTED_KWS)
        eps_diluted = t[eps_diluted_loc['table_id']
                        ][eps_diluted_loc['row_num']][h['rev_col']]
        eps_diluted_yoy = t[eps_diluted_loc['table_id']
                            ][eps_diluted_loc['row_num']][h['rev_yoy']]
        # 总资产
        assets_loc = self.LocateKeywordByList(t, self.ASSETS_KWS)
        assets = t[assets_loc['table_id']][assets_loc['row_num']][h['ass_col']]
        assets_yoy = t[assets_loc['table_id']
                       ][assets_loc['row_num']][h['ass_yoy']]
        # 归属上市公司股东净资产
        assets_sh_loc = self.LocateKeywordByList(
            t, self.ASSETS_SHAREHOLDERS_KWS)
        assets_sh = t[assets_sh_loc['table_id']
                      ][assets_sh_loc['row_num']][h['ass_col']]
        assets_sh_yoy = t[assets_sh_loc['table_id']
                          ][assets_sh_loc['row_num']][h['ass_yoy']]

        earnings = {
            'year': year,
            'quarter': quarter,
            'company': company,
            'stock': stock,
            'revenue': self.ConvertNumber(revenue),
            'revenue_yoy': self.ConvertPercentage(revenue_yoy),
            'net_income': self.ConvertNumber(net_income),
            'net_income_yoy': self.ConvertPercentage(net_income_yoy),
            'opt_income': self.ConvertNumber(opt_income),
            'opt_income_yoy': self.ConvertPercentage(opt_income_yoy),
            'opt_cashflow': self.ConvertNumber(opt_cashflow),
            'opt_cashflow_yoy': self.ConvertPercentage(opt_cashflow_yoy),
            'eps_basic': self.ConvertNumber(eps_basic),
            'eps_basic_yoy': self.ConvertPercentage(eps_basic_yoy),
            'eps_diluted': self.ConvertNumber(eps_diluted),
            'eps_diluted_yoy': self.ConvertPercentage(eps_diluted_yoy),
            'assets': self.ConvertNumber(assets),
            'assets_yoy': self.ConvertPercentage(assets_yoy),
            'assets_sh': self.ConvertNumber(assets_sh),
            'assets_sh_yoy': self.ConvertPercentage(assets_sh_yoy)
        }

        return earnings

    def ParseOutlook(self, t, keyword_list):
        d = self.LocateKeywordByList(t, keyword_list)
        # print(d)
        if d['col_num'] == '':
            return ''

        lst = []
        for row in t[d['table_id']]:
            if row[d['col_num']] == '' or row[d['col_num']] in keyword_list:
                lst += row

        lst = [x for x in lst if not (x in keyword_list)]
        unique_list = list(OrderedDict((x, None) for x in lst))

        para = ''.join(unique_list)
        para = re.sub(r'本公司', '公司', para)
        para = re.sub(r' ', '', para)

        return para

    def GenerateNews(self, t, p, company, stock):
        d = self.RetrieveEarningData(t, p)

        temp = "{}（{}）发布{}年{}度报告。" + \
            "公司在本报告期实现营收{}，同比{}；" + \
            "归属于上市公司股东的净利润{}，同比{}；" + \
            "稀释后每股收益{}，同比{}。"
        temp = temp.format(
            company,
            stock,
            d['year'],
            d['quarter'],
            d['revenue'],
            d['revenue_yoy'],
            d['net_income'],
            d['net_income_yoy'],
            d['eps_diluted'],
            d['eps_diluted_yoy']
        )

        temp = temp + '\n\n'
        if d['opt_cashflow'] != '':
            temp = temp + \
                '公司在本报告期内通过经营活动产生的现金流量净额为{}，同比{}。'.format(
                    d['opt_cashflow'], d['opt_cashflow_yoy'])
        if d['assets'] != '':
            temp = temp + \
                '公司在本报告期末的总资产为{}，较上年度末{}。'.format(d['assets'], d['assets_yoy'])
            if d['assets_sh'] != '':
                temp = temp + \
                    '其中，归属上市公司股东的净资产为{}，较上年度末{}。'.format(
                        d['assets_sh'], d['assets_sh_yoy'])
        if d['quarter'] == '全年':
            temp.replace('本报告期', d['year'] + '年')

        outlook = self.ParseOutlook(t, self.OUTLOOK_EXPLANATION_KWS)
        if outlook != '':
            temp = temp + '\n\n此外，公司还表示：{}'.format(outlook)

        return temp + '\n'

    def __str__(self):
        return 'Earnings'

    __repr__ = __str__
