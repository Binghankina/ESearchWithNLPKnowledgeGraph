# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import re
from touyantong.settings import TAGS

HEADERS = ["本报告期", "股票简称", "项目", "上年度末", "本报告期末比上年度末增减", "年初至报告期期末金额", "报告期末普通股股东总数", "报告期末表决权恢复的优先股股东总数（如有）", "股东名称", "期初限售股数", "本期解除限售股数", "本期增加限售股数", "期末限售股数", "限售原因", "拟解除限售日期"]


def is_standard_table(soup):
    if soup.find("img"):
        return False
    return True


def merge_tag_p(soup):
    trs = soup.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        for td in tds:
            ps = td.find_all('p')
            value = ""
            for p in ps:
                value += p.text
                p.extract()
            value = value.strip()
            td.append(value)
    tbodys = soup.find_all('table')
    tbodys = [tbody for tbody in tbodys if is_standard_table(tbody)]
    return tbodys


def is_one_table(table, next_table):
    if len(table.find_all("tr")[-1].find_all("td")) != len(next_table.find_all("tr")[0].find_all("td")):
        return False
    for td in next_table.find_all("tr")[0].find_all("td"):
        if td.text in HEADERS:
            return False
    return True


def get_all_tr(tbody):
    r = ""
    for tr in tbody.find_all("tr"):
        r += tr.prettify()
    return r


def caption_vampire(soup):
    ignore_list = ["是", "否", "单位", "年"]
    previous_deep = 0
    while previous_deep < 5:
        soup = soup.find_previous("p")
        if not soup:
            break
        if not soup.text or [1 for ignore in ignore_list if ignore in soup.text]:
            previous_deep += 1
            continue
        r = re.sub(r"[\s+\.\!\/_,$%:^*(+\"\']+|[表图\d+——：！，。？、~@#￥%……&*（）]+", "", soup.text.replace(" ", ""))
        return r
    return "\n"


def merge_tables(tbodys):
    if not tbodys:
        return []
    list_tr = []
    len_trs = len(tbodys)
    if len_trs == 0:
        return []
    elif len_trs == 1:
        t_s = get_all_tr(tbodys[0])
        return [[t_s, caption_vampire(tbodys[0])]]

    for i in range(len_trs-1):
        if i == 0:
            list_tr.append(
                [get_all_tr(tbodys[i]), caption_vampire(tbodys[i])]
            )
        if is_one_table(tbodys[i], tbodys[i+1]):
            list_tr[-1][0] += get_all_tr(tbodys[i+1])
        else:
            list_tr.append(
                [get_all_tr(tbodys[i + 1]), caption_vampire(tbodys[i + 1])]
            )
    return list_tr


def filter_rr_tables(tbody):
    previous_deep = 0
    while previous_deep < 5:
        tbody = tbody.find_previous("p")
        if not tbody:
            return False
        if re.match(r"表\d：", tbody.text.replace(" ", "")):
            return True
        else:
            previous_deep += 1
            continue
    return False


def html2json(list_tr):
    if not list_tr:
        return {}
    index = 1
    result = {}
    for trs in list_tr:
        tr_list = []
        tr_list.append(trs[1])
        trs = BeautifulSoup(trs[0], "lxml").find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            td_list = []
            for td in tds:
                td_list.append({"value": td.text.replace("\n", ""), "colspan": td.get("colspan"), "rowspan": td.get("rowspan")})
            tr_list.append(td_list)
        result.update({"table_t%s" % index: tr_list})
        index += 1
    return result


def main(origin, category):
    soup = BeautifulSoup(origin, "lxml")
    try:
        type_id = [tag["type_id"] for tag in TAGS if tag["abbreviation"] == category][0]
    except IndexError:
        return {}
    # fr
    if type_id == 2:
        r = html2json(merge_tables(
            merge_tag_p(soup))
        )
    # rr
    elif type_id == 3:
        r = html2json(merge_tables(
            [v for v in merge_tag_p(soup) if filter_rr_tables(v)])
        )
    else:
        r = {}
    return r


if __name__ == '__main__':
    origin = open("/Users/zequnfeng/Downloads/bbb/bbb/content.htm", "r", encoding="utf-8")
    r = main(origin, "companyrr")
    print(r)
#
