import json
import numpy as np
from collections import OrderedDict

account_headers = ['总资产（元）',
                   '归属于上市公司股东的净资产（元）',
                   '营业收入（元）',
                   '归属于上市公司股东的净利润（元）',
                   '归属于上市公司股东的扣除非经常性损益的净利润（元）',
                   '经营活动产生的现金流量净额（元）',
                   '基本每股收益（元/股）',
                   '稀释每股收益（元/股）',
                   '加权平均净资产收益率',
                   '非经常性损益项目和金额',
                   '本报告期']
finance_headers = ['非流动资产处置损益',
                   '计入当期损益的政府补助',
                   '计入当期损益的政府补助',
                   '除同公司正常经营业务相关'
                   '交易性金融负债产生的公允价值变动损益'
                   '除上述各项之外的其他营业外收入和支出',
                   '少数股东权益影响额',
                   '减：所得税影响额']
shareholder_headers = ['股东总数',
                     '持有有限售条件的股份数量',
                     '质押或冻结',
                     '境内自然人',
                     '境内非国有法人',
                     '境内国有法人'  ]

shareholder_unlimited_headers = ['上述股东关联关系或一致',
                                 '持有无限售条件股份数量',
                                 '持有无限售条件普通股股份数量',
                                 '人民币普通股']
detail_account_headers = ['应收票据','应收账款','经纪公司','预付款项','应收利息','长期应收款','应付利息','应交税费','长期借款',
                          '拆入资金净增加额','投资支付的现金','投资活动现金流入小计','投资支付的现金','投资活动现金流出小计',''
                          '收回投资收到的现金', '取得投资收益收到的现金','投资活动现金流入小计','吸收投资收到的现金','发行债券收到的现金',
                          '现金及现金等价物净增加额','期初现金及现金等价物余额','划分为持有待售的负债','支付的其他与','收到的税费返还']
forecast_table_headers = ['归属于上市公司股东的净利润变动幅度', '归属于上市公司股东的净利润变动区间', '']


keywords_to_remove = [" / ", "负责人", "编制单位", "报告正文","报告全文"]

mark_list = ["", "ph_l", "ph_u"]
special_string_for_reformat_row = ["稀释每股收益"]
special_string_for_reformat_column = ["人民币普通股","境内自然人","国有法人","质押","冻结"]

def table_string_check(headers, table, n):
    counter = 0
    table_str = ""
    for row in table:
        row_str = "".join(row)
        table_str += row_str.replace(" ","")
    for header in headers:
        if header in table_str:
            counter += 1
    if counter >= n:
        return True
    else:
        return False




def determine_table(table, category):
    table_name = ""
    if category == 1:
        if table_string_check(account_headers, table, 2):
            table_name = "主要会计数据"
        elif table_string_check(finance_headers, table, 1):
            table_name = "主要财务指标"
        elif table_string_check(shareholder_headers, table, 1):
            table_name = "前10名股东持股情况"
        elif table_string_check(shareholder_unlimited_headers, table, 1):
            table_name = "前10名无限售条件股东持股情况"
        elif table_string_check(detail_account_headers, table, 3):
            table_name = "详细财务数据、会计数据及财务指标"
        elif table_string_check(forecast_table_headers, table, 2):
            table_name = "经营业绩展望"


    elif category == 2:
        if table_string_check(account_headers, table, 2):
            table_name =""
        elif table_string_check(account_headers, table, 2):
            table_name = "公司概况"
        elif table_string_check(account_headers, table, 2):
            table_name = "详细财务数据预测"
        elif table_string_check(account_headers, table, 2):
            table_name = "报告评级分析"
        elif table_string_check(account_headers, table, 2):
            table_name = "主要财务数据预测"
    elif category == 3:
        if table_string_check(account_headers, table, 2):
            table_name ="drop"
    return table_name


def print_table(table):
    print("==============================")
    for e in table:
        print(e)
    print("==============================")

def check_special_string(l):
    for s_l in special_string_for_reformat_row:
        for e in l:
            if s_l in e:
                return True


def table_transpose(table):
    table_array = np.array(table)
    return table_array.T.tolist()


def table_row_strip(table):
    return_table =[]
    row_len = len(table)
    if row_len > 0:
        for i, l in enumerate(table):
            temp_list = []
            remove = 0
            for j, e in enumerate(l):
                if "ph_l" in e  or "ph_u" in e:
                    temp_list.append("")
                else:
                    temp_list.append(e)
            for keyword  in keywords_to_remove:
                if keyword in "".join(temp_list):
                    remove = 1
            if "".join(temp_list) != "" and remove == 0:
                return_table.append(l)
        return return_table
    else:
        return table


def table_column_strip(table):
    transpose_list = table_transpose(table)
    transpose_list_striped = table_row_strip(transpose_list)
    return table_transpose(transpose_list_striped)


def table_reformat_row(table):
    row_len = len(table)
    if row_len > 0:
        return_table = []
        for i, l in enumerate(table):
            temp_list = []
            if not check_special_string(l):
                for j, e in enumerate(l):
                    if j == 0 or e != l[j - 1] or e == "":
                        temp_list.append(e)
                    else:
                        temp_list.append("ph_l")
            else:
                for j, e in enumerate(l):
                    if j == 0 or e != l[j - 1] or e == "":
                        if e != "":
                            temp_list.append(e+"<protect>")
                        else:
                            temp_list.append(e)
                    else:
                        temp_list.append("ph_l")
            return_table.append(temp_list)
        return return_table
    else:
        return table


def table_reformat_column(table):
    column_len = len(table)
    if column_len > 0:
        return_table = []
        for i, l in enumerate(table):
            temp_list = []
            for j, e in enumerate(l):
                if j == 0 or e != l[j - 1] or e == "" or e in special_string_for_reformat_column:
                    temp_list.append(e)
                else:
                    temp_list.append("ph_u")
            return_table.append(temp_list)
        return return_table
    else:
        return table


def table_reformat(table):
    formated_table_row = table_reformat_row(table)
    t_transpose = table_transpose(formated_table_row)
    formated_table_transpose = table_reformat_column(t_transpose)
    formated_table = table_transpose(formated_table_transpose)
    return formated_table


def list_clean_column(l):
    return_l = []
    for e in l:
        if e == "ph_l":
            return_l.append("")
        else:
            return_l.append(e)
    return return_l


def list_clean_row(l):
    return_l = []
    for e in l:
        if "ph_l" in e or "ph_u" in e or "<protect>" in e:
            e = e.replace("ph_l", "")
            e = e.replace("ph_u", "")
            e = e.replace("<protect>", "")
        return_l.append(e)
    return return_l


def table_clean(table):
    return_table = []
    row_len = len(table)
    if row_len > 0:
        for i, l in enumerate(table):
            if i > 0:
                temp_list = []
                for j, e in enumerate(l):
                    if "ph_l" in e or "ph_u" in e or "<protect>" in e or "<symmetry>" in e:
                        e = e.replace("ph_l", "")
                        e = e.replace("ph_u", "")
                        e = e.replace("<protect>", "")
                        e = e.replace("<symmetry>", "")
                        temp_list.append(e)
                    else:
                        temp_list.append(e)
                return_table.append(temp_list)
            else:
                return_table.append(l)
        return return_table
    else:
        return table


def columns_merge(table):
    column_len = len(table)
    merge = 0
    if column_len > 0:
        return_table = []
        prev_list = []
        for i, l in enumerate(table):
            if i > 0 and merge == 0:
                if "ph_l" in l:
                    for j, e in enumerate(l):
                        if (l[j] not in mark_list) and (prev_list[j] not in mark_list):
                            merge = 0
                            break
                        else:
                            merge = 1
                if merge == 0:
                    return_table.append(prev_list)
                else:
                    prev_list_cleaned = list_clean_column(prev_list)
                    l_cleaned = list_clean_column(l)
                    return_table.append([x + y for x, y in zip(prev_list_cleaned, l_cleaned)])
                if i+1 == column_len and merge == 0:
                    return_table.append(l)
            elif merge == 1:
                if i+1 == column_len:
                    return_table.append(l)
                else:
                    merge = 0
            prev_list = l
        return return_table
    else:
        return table


def rows_merge(table, column):
    row_len = len(table)
    if row_len > 0:
        return_table = []
        for i, l in enumerate(table):
            temp_list = []
            if "ph_u" in l[column]:
                prev_list_cleaned = list_clean_row(return_table[-1])
                l_cleaned = list_clean_row(l)
                for x, y in zip(prev_list_cleaned, l_cleaned):
                    if x == y:
                        temp_list.append(x)
                    else:
                        temp_list.append(x + y)
                return_table[-1] = temp_list
            else:
                return_table.append(l)
        return return_table
    else:
        return table


def merge_tables(data):
    row_length_list = [0]
    table_list = []
    merged_data = OrderedDict()
    table=[]
    for t_k, t_v in data.items():
        row_length = len(t_v[0])
        if row_length != row_length_list[-1]:
            table_list.append(table)
            table = t_v
        else:
            table = table + t_v
        if len(row_length_list) == len(data) :
            table_list.append(table)
        row_length_list.append(row_length)
    for t_i in range(1, len(table_list)):
        merged_data["table_t" + str(t_i)] = table_list[t_i]
    return merged_data


def _itersplit(l, splitter, keep):
    current = []
    for row in l:
        row_str = "".join(row)
        if splitter in row_str.replace(" ",""):
            yield current
            if keep:
                current = []
                current.append(row)
            else:
                current = []
        else:
            current.append(row)
    yield current


def tablesplit(l, splitter, keep):
    return [subl for subl in _itersplit(l, splitter, keep) if subl]


def split_tables(data, keyword, keep_keyword):
    splited_list = []
    return_data = OrderedDict()
    for t_k, t_v in data.items():
        tables = tablesplit(t_v, keyword, keep_keyword)
        splited_list.extend(tables)
    for t_i in range(0, len(splited_list)):
        return_data["table_t" + str(t_i+1)] = splited_list[t_i]
    return return_data


def f_s_e(l):
    counter = 0
    for e in l:
        if e not in mark_list:
            counter += 1
    if counter == 1:
        return True
    else:
        return False


def symmetry_merge(table):
    return_table = []
    if len(table) > 3:
        for i, l in enumerate(table):
            if i < len(table)-2:
                if f_s_e(l) and (not f_s_e(table[i+1])) and (f_s_e(table[i+2])):
                    for j, e in enumerate(table[i+1]):
                        table[i + 1][j] = e+"<symmetry>"
                    for j, e in enumerate(table[i+2]):
                        table[i + 2][j] = e+"<symmetry>"
                #elif (i < len(table)-3) and f_s_e(l) and (not f_s_e(table[i+1])) and (not f_s_e(table[i+2])) and f_s_e(table[i+3]):
                #    print("find pattern 2")
                #    for j, e in enumerate(table[i+1]):
                #        table[i + 1][j] = e+"<symmetry>"
                #    for j, e in enumerate(table[i+2]):
                #        table[i + 2][j] = e+"<symmetry>"
                #    for j, e in enumerate(table[i+3]):
                #        table[i + 3][j] = e+"<symmetry>"
        for i, l in enumerate(table):
            temp_list = []
            if "<symmetry>" in "".join(l):
                for x, y in zip(return_table[-1], l):
                    if x == y:
                        temp_list.append(x)
                    else:
                        temp_list.append(x + y)
                return_table[-1] = temp_list
            else:
                return_table.append(l)
        return return_table
    else:
        return table


def finance_report_process(data):
    sorted_data = OrderedDict()
    final_data = OrderedDict()
    tables = []
    #为表格排序
    for key_num in range(1, len(data)+1):
        sorted_data["table_t"+str(key_num)] = data["table_t"+str(key_num)]
    # 将解析在一起的表格分开
    splited_data = split_tables(sorted_data, "√适用□不适用", 0)
    splited_data = split_tables(splited_data, "单位：元", 0)
    splited_data = split_tables(splited_data, "单位：股", 0)
    splited_data = split_tables(splited_data, "股东持股情况", 1)
    splited_data = split_tables(splited_data, "股东总数", 1)

    account_table = ["主要会计数据"]
    finance_table = ["主要财务指标"]
    stockholder_table = ["前10名股东持股情况"]
    stockholder_unlimited_table = ["前10名无限售条件"]
    detail_account_table = ["详细财务数据、会计数据及财务指标"]
    expect_table = ["经营业绩展望"]
    for t_k, t_v in splited_data.items():
        t_v = table_reformat(t_v)
        t_v = table_row_strip(t_v)
        t_v = table_column_strip(t_v)
        t_v = table_transpose(columns_merge(table_transpose(t_v)))
        table_name = determine_table(t_v, 1)
        #print(table_name)
        if table_name == "主要会计数据":
            account_table += t_v
        elif table_name == "主要财务指标":
            finance_table += t_v
        elif table_name == "前10名股东持股情况":
            stockholder_table += t_v
        elif table_name == "前10名无限售条件股东持股情况":
            stockholder_unlimited_table += t_v
        elif table_name == "详细财务数据、会计数据及财务指标":
            detail_account_table += t_v
        elif table_name == "经营业绩展望":
            expect_table += t_v
    if len(account_table) > 1:
        tables.append(account_table)
    if len(finance_table) > 1:
        tables.append(finance_table)
    if len(stockholder_table) > 1:
        tables.append(stockholder_table)
    if len(stockholder_unlimited_table) > 1:
        tables.append(stockholder_unlimited_table)
    if len(detail_account_table) > 1:
        tables.append(detail_account_table)
    if len(expect_table) > 1:
        tables.append(expect_table)

    for i in range(1, len(tables)+1):
        final_data["table_t"+str(i)] = tables[i-1]

    for t_k, t_v in final_data.items():
        if "经营业绩展望" in t_v:
            pass
        elif "前10名无限售条件股东持股情况" in t_v:
            t_v = symmetry_merge(t_v)
            t_v = table_clean(t_v)
        elif "前10名股东持股情况" in t_v:
            t_v = rows_merge(t_v, 1)
            t_v = symmetry_merge(t_v)
            t_v = table_clean(t_v)
        else:
            t_v = rows_merge(t_v, 1)
            t_v = rows_merge(t_v, 0)
            t_v = symmetry_merge(t_v)
            t_v = table_clean(t_v)
        if len(t_v) > 2:
            final_data[t_k] = t_v
    return final_data


def research_report_company_process(data):
    sorted_data = OrderedDict()
    final_data = OrderedDict()
    #为表格排序
    for key_num in range(1, len(data)+1):
        sorted_data["table_t"+str(key_num)] = data["table_t"+str(key_num)]
    # 对表格的每个单元做进一步处理 并进行 列合并
    # 为表格添加名字 并进行 行合并
    splited_data = split_tables(sorted_data, "数据来源", 0)
    key_num = 1
    for t_k, t_v in splited_data.items():
        table_name = determine_table(t_v, 2)
        t_v = table_reformat(t_v)
        t_v = table_row_strip(t_v)
        t_v = table_column_strip(t_v)
        t_v = table_transpose(columns_merge(table_transpose(t_v)))
        final_data["table_t" + str(key_num)] = t_v
        t_v.insert(0, "unamed")
        key_num += 1
    return final_data


def research_report_industry_process(data):
    sorted_data = OrderedDict()
    final_data = OrderedDict()
    #为表格排序
    for key_num in range(1, len(data)+1):
        sorted_data["table_t"+str(key_num)] = data["table_t"+str(key_num)]
    # 对表格的每个单元做进一步处理 并进行 列合并
    splited_data = split_tables(sorted_data, "数据来源", 0)
    # 为表格添加名字 并进行 行合并
    key_num = 1
    for t_k, t_v in splited_data.items():
        table_name = determine_table(t_v, 3)
        t_v = table_reformat(t_v)
        t_v = table_row_strip(t_v)
        t_v = table_column_strip(t_v)
        t_v = table_transpose(columns_merge(table_transpose(t_v)))
        final_data["table_t" + str(key_num)] = t_v
        t_v.insert(0, "unamed")
        key_num += 1
    return final_data


def pretty_table(data, category):
    if "bb" in category:
        return finance_report_process(data)
    elif "companyrr" in category:
        return research_report_company_process(data)
    elif "industryrr" in category:
        return research_report_industry_process(data)
    elif "conceptrr" in category:
        return research_report_industry_process(data)
    elif "macrorr" in category:
        return research_report_industry_process(data)
    else:
        return data


