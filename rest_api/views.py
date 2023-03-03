# -*- coding:utf-8 -*-

import calendar
import json
import threading
import traceback as tb
from collections import OrderedDict
from datetime import datetime, timedelta

from channels import Group
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from rest_api.models import ResearchReport, Author
from rest_api.models import UserProfile
from rest_api.es import es_client, ES_INDEX, ES_DOCTYPE
from rest_api.tools import extract_images, extract_tables
from touyantong.settings import TOKEN_ARTICLE_ANALYZER, SERVER_ARTICLE_ANALYZER, ENDPOINT_ARTICLE_ANALYZER, TAGS
from touyantong.settings import BASE_DIR
from touyantong.utilities import logger, jsonLoader, pdf_parser
from word_embedding.word_2_vec import load_embedding, serve_touyantong
import hashlib
import logging
import os
import copy


final_embeddings, reverse_dictionary = load_embedding(
    os.path.join(BASE_DIR, 'word_embedding', 'embedding', 'embedding'),
    os.path.join(BASE_DIR, 'word_embedding', 'embedding', 'dictionary')
)

logger = logging.getLogger('default')


def cleaning_content(content):
    origin_content = content
    if not content:
        return content
    replace_string_list = ["【研究报告内容摘要】", ]
    split_string = "阅读附件全文请下载"
    for replace_string in replace_string_list:
        content = content.replace(replace_string, "")
    r = content.split(split_string)[0]
    if not r:
        return origin_content
    return r


def analyze_article(url):
    data = {"url": url}
    server = SERVER_ARTICLE_ANALYZER + ENDPOINT_ARTICLE_ANALYZER
    token = TOKEN_ARTICLE_ANALYZER
    res = jsonLoader(data, server, token)
    logger.info("[CONTENT_PARSER] %s url: %s" % (res.status_code, url))


def format_rr_info(category, data):
    if not category or not data:
        return "null"
    try:
        type_id = [tag["type_id"] for tag in TAGS if tag["abbreviation"] == category][0]
        category_title = [tag["title"] for tag in TAGS if tag["abbreviation"] == category][0]
        title = data["article_title"]
    except IndexError:
        return "null"

    if type_id == 2:
        if "深" in category_title:
            organization = "深圳证券交易所"
        elif "沪" in category_title:
            organization = "上海证券交易所"
        else:
            organization = "null"
    elif type_id == 3:
        try:
            organization = title.split("--")[0]
            title = title.split("--")[1]
            title = title.split("【")[0]
        except IndexError:
            organization = "null"
    else:
        organization = "null"

    data.update({"organization": organization, "article_title": title, "category": category_title})
    return data


def ws_group(category, data):
    try:
        data = format_rr_info(category, data)
        Group(category).send({'text': json.dumps(data, ensure_ascii=False)})
    except:
        logger.error(tb.format_exc())


class ResearchReportURLAPI(APIView):
    """
    该类用于接受爬虫更新数据
    """
    # authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (AllowAny, )
    http_method_names = ['post']

    def post(self, request):
        try:
            req = request.data
            info = req.get("info")
            req = {
                "article_title": info.get("article_title") if info else "",
                "article_content": info.get("article_content") if info else "",
                "article_url": req.get("article_url"),
                "attachment_url": req.get("attachment_url"),
                "attachment_type": req.get("attachment_type"),
                "category": info.get("category") if info else ""
            }
            r = ResearchReport.objects.get_or_create(**req)
            if not r[1]:
                return Response('Invalid parameters or existed', status=status.HTTP_400_BAD_REQUEST)
            # add author
            if info.get("name") and info.get("name") != "NO_MATCH":
                author = Author.objects.filter(analyst_name__in=info.get("name")).exclude(expire_date=None)
                # uniqueness check
                if len(author) == len(info.get("name")):
                    author = Author.objects.filter(analyst_name__in=info.get("name"))
                    author = [v for v in author]
                    rr_obj = ResearchReport.objects.get(id=r[0].id)
                    rr_obj.authors.add(*author)
                    rr_obj.save()
                pass
            # content parser
            if req.get("article_url"):
                threading.Thread(target=analyze_article(req["article_url"])).start()
            elif not req.get("article_url"):
                try:
                    category_title = [tag["title"] for tag in TAGS if tag["abbreviation"] == info.get("category")][0]
                except IndexError:
                    category_title = ""
                data = {"article_content": info.get("article_content") if info else "",
                        "article_url": req.get("article_url"),
                        "report_id": r[0].id,
                        "authors": [],
                        "enable_favorites": False,
                        "category": category_title,
                        "article_title": info.get("article_title") if info else "",
                        "attachment_url": req.get("attachment_url"),
                        "create_time": str(calendar.timegm(datetime.now().timetuple())) + "000"
                        }
                ws_group(info.get("category"), data)
            # pdf parser
            if req["attachment_type"] == 1 and req["attachment_url"]:
                m = hashlib.sha256()
                m.update(bytes(req["attachment_url"][0], encoding="utf-8"))
                hash_v = m.hexdigest()
                ResearchReport.objects.filter(id=r[0].id).update(hash=hash_v)
                threading.Thread(target=pdf_parser(req["attachment_url"][0], hash_v)).start()

            return Response('OK. Request is received and processed.', status=status.HTTP_200_OK)
        except:
            logger.error(tb.format_exc())
            return Response('Invalid parameters', status=status.HTTP_400_BAD_REQUEST)


rr_urls = ResearchReportURLAPI.as_view()


class ResearchReportDetailsAPI(APIView):
    """
    该类用于更新ResearchReport表中剩余信息，并发送WebSocket请求
    """
    # authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (AllowAny, )
    http_method_names = ['post']

    def post(self, request):
        try:
            req = request.data
            # Sanity Check:
            mandatory_fields = ["url", "title", "body"]
            for mf in mandatory_fields:
                if not mf in req:
                    return Response('Invalid parameters, mandatory field(s) is missing.',
                                    status=status.HTTP_400_BAD_REQUEST)
            try:
                category = req['url'].split('/')[2].split('.')[1]
            except IndexError:
                category = 'unknow'
            work_category = [tag["abbreviation"] for tag in TAGS if tag["type_id"] == 1]
            if category not in work_category:
                rr_obj = ResearchReport.objects.filter(article_url=req["url"]).exclude(category=u"").first()
                category = rr_obj.category
            ResearchReport.objects.filter(article_url=req["url"], category="").update(
                article_title=req["title"], article_content=req["body"], category=category)

            ResearchReport.objects.filter(article_url=req["url"]).exclude(category=u"").update(
                article_title=req["title"], article_content=req["body"])
            rr_obj = ResearchReport.objects.get(article_url=req["url"])
            data = {"article_content": cleaning_content(req["body"]),
                    "article_url": req["url"],
                    "report_id": rr_obj.id,
                    "authors": [],
                    "enable_favorites": False,
                    "category": rr_obj.category,
                    "article_title": req["title"],
                    "attachment_url": rr_obj.attachment_url,
                    "create_time": str(calendar.timegm(rr_obj.created_at.timetuple())) + "000"
                    }
            # sent message to ws group
            ws_group(category, data)
            return Response('Ok', status=status.HTTP_200_OK)
        except:
            logger.error(tb.format_exc())
            return Response('Invalid parameters', status=status.HTTP_400_BAD_REQUEST)


rr_details = ResearchReportDetailsAPI.as_view()


class ResearchReportPDFAPI(APIView):
    """
    描述：接受pdf解析结果api
    request：{"url": "", "tables": {}, "images": {}}
    response: "Ok" or "Invalid parameters"
    """
    permission_classes = (AllowAny, )
    http_method_names = ['post']

    def post(self, request):
        req = request.data
        try:
            rr_obj = ResearchReport.objects.get(hash=req["filename"])
            if req["content"]:
                rr_obj.table_raw_data = req["content"]
                rr_obj.attachment_images = extract_images.main(req["content"], rr_obj.category, rr_obj.hash)
                rr_obj.attachment_content = extract_tables.main(req["content"], rr_obj.category)
            else:
                rr_obj.table_raw_data = req["index"]
            rr_obj.save()
            logger.info("[RR_PDF] Ok id: <%s>" % req["filename"])
            return Response('Ok', status=status.HTTP_200_OK)
        except:
            logger.error("[RR_PDF] FAIL " + tb.format_exc())
            return Response('Invalid parameters', status=status.HTTP_400_BAD_REQUEST)


rr_pdf = ResearchReportPDFAPI.as_view()


class UpdateSubscribeAPI(APIView):
    """
    描述：该类用于更细用户订阅标签，参数为订阅标签id，多个请用','分隔
    request：{'list_subscribe': '1,2,3'}
    response: 'Invalid parameters', 'OK, Already create user profile' or 'OK, Already update user profile'
    """
    authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['post']

    def post(self, request, **kwargs):
        list_subscribe = []
        try:
            list_subscribe_id = request.data.get('list_subscribe').split(',')
        except ValueError:
            print(tb.format_exc())
            return Response('Invalid parameters', status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            print(tb.format_exc())
            return Response('Invalid parameters', status=status.HTTP_400_BAD_REQUEST)
        user_profile_obj = UserProfile.objects.get(user__id=self.request.user.id)
        if not list_subscribe_id[0]:
            list_subscribe = []
        else:
            for subscribe_id in list_subscribe_id:
                list_subscribe += [tag['abbreviation'] for tag in TAGS if tag['id'] == int(subscribe_id)]
        user_profile_obj.subscribe_list = list_subscribe
        user_profile_obj.save()
        return Response('OK, Already update user profile', status=status.HTTP_200_OK)


update_subscribe = UpdateSubscribeAPI.as_view()


class GetReportDetailAPI(APIView):
    """
    描述：该类用于获取研报详情，参数为研报id，response为一个json
    request：/api/research_report/get_report_detail/1/
    response：
        {
            'article_url': '研报url',
            'article_title': '研报标题',
            'article_content': '研报正文',
            'attachment_url': '附件url',
            'attachment_content': '附件内容',
            'authors': [
                {
                    "sec_id": "A0330200010004",
                    "analyst_name": "侯英民"
                },
                {
                    "sec_id": "S0820112040006",
                    "analyst_name": "刘孙亮"
                }
            ]
        }
    """
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get']

    def get(self, request, **kwargs):
        user_profile = UserProfile.objects.get(user_id=self.request.user.id)
        favorites = user_profile.favorites_list
        report_id = self.kwargs.get('report_id')
        report_obj = ResearchReport.objects.get(id=report_id)
        authors = []
        try:
            authors_names = list(set([v.analyst_name for v in report_obj.authors.all()]))
            for authors_name in authors_names:
                authors.append({"analyst_name": authors_name,
                                "uuid": [v.uuid for v in report_obj.authors.filter(
                                    analyst_name=authors_name) if v.uuid][0]})
        except IndexError:
            authors = []

        try:
            category_title = [tag['title'] for tag in TAGS if tag['abbreviation'] == report_obj.category][0]
        except IndexError:
            category_title = ""
        data = {
            'article_url': report_obj.article_url,
            'article_title': report_obj.article_title,
            'article_content': cleaning_content(report_obj.article_content),
            'attachment_url': report_obj.attachment_url,
            'attachment_content': report_obj.attachment_content,
            'create_time': str(calendar.timegm(report_obj.created_at.timetuple())) + '000',
            'category': category_title,
            'authors': authors,
            'images': report_obj.attachment_images,
            'pages': report_obj.pages,
            'enable_favorites': True if int(report_id) in favorites else False,
        }
        data = format_rr_info(report_obj.category, data)
        return Response(data=data, status=status.HTTP_200_OK)


get_report_detail = GetReportDetailAPI.as_view()


class FavoritesAPI(APIView):
    """
    描述：该类用于更新或删除用户收藏研报列表,参数为研报id
    request：{'favorites_list', '1', 'action': 'add'} or {'favorites_list', '1', 'action': 'delete'}
    response: 'Invalid parameters' or 'Ok'
    """
    authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        try:
            favorites_list = request.data['favorites_list']
            action = request.data['action']
        except KeyError:
            return Response('Invalid parameters', status=status.HTTP_400_BAD_REQUEST)

        if action not in ['delete', 'add']:
            return Response('Invalid parameters, Action must be delete or add', status=status.HTTP_400_BAD_REQUEST)

        try:
            favorites_list = [int(favorites) for favorites in favorites_list.split(',')]
        except TypeError:
            return Response('Invalid parameters', status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response('Invalid parameters', status=status.HTTP_400_BAD_REQUEST)

        profile_obj = UserProfile.objects.get(user_id=self.request.user.id)

        # 删除favorites
        if action == 'delete' and profile_obj:
            tmp_favorites_list = profile_obj.favorites_list
            favorites_id_list = favorites_list
            if not favorites_id_list[0]:
                return Response('Invalid parameters, Empty favorites list', status=status.HTTP_400_BAD_REQUEST)
            for favorites_id in favorites_id_list:
                try:
                    tmp_favorites_list.remove(favorites_id)
                except ValueError:
                    continue

            profile_obj.favorites_list = tmp_favorites_list
            profile_obj.save()
            return Response('OK, Deleted', status=status.HTTP_200_OK)

        # 动作为删除且不存在用户画像时return error
        if action == 'delete' and not profile_obj:
            return Response('Error, Please add favorites id before delete', status=status.HTTP_400_BAD_REQUEST)

        user_favorites_list = profile_obj.favorites_list

        # 20个为favorites list的上限
        for favorites in favorites_list:
            if len(user_favorites_list) >= 20:
                user_favorites_list.pop(0)
                user_favorites_list.append(favorites)
            else:
                user_favorites_list.append(favorites)

        profile_obj.favorites_list = user_favorites_list
        profile_obj.save()
        return Response('Ok, Added', status=status.HTTP_200_OK)


favorites = FavoritesAPI.as_view()


class RRInitializationAPI(APIView):
    """
    描述：该API用于在用户打开页面时获取研报，参数为订阅标签ID，多个的话用','分隔，如若为空则返回空数组
    request：api/research_report/rr_initialization/subscribes=0,1,2
    response：
        [{
        "report_id": 839,
        "article_url": "https://www.newyorkfed.org/research/staff_reports/sr823.html",
        "article_content": "During banking crises, regulators often relax their normal requirements and refrain from closing financially troubled banks. I estimate the real effects of such regulatory forbearance by comparing differences in state-level economic outcomes by the amount of forbearance extended during the U.S. savings and loan crisis. To instrument for forbearance, I use historical variation in deposit insurance—and hence supervision—of similar financial intermediaries (thrifts) and exploit fixed differences between regional supervisors of the same regulator. The evidence suggests a policy-induced increase in high-risk loans during the official forbearance period (1982-89), followed by a broader bust in house prices and real GDP.",
        "article_title": "Does Going Easy on Distressed Banks Help Economic Growth?",
        "create_time": "2017-09-26T05:08:26.111164Z",
        "category": "国际清算银行"
        "authors": [
            {
                "sec_id": "A0330200010004",
                "analyst_name": "侯英民"
            },
            {
                "sec_id": "S0820112040006",
                "analyst_name": "刘孙亮"
            }
        ]
        ""
        },{
        "report_id": 840,
        "article_url": "https://www.newyorkfed.org/research/staff_reports/sr824.html",
        "article_content": "During banking crises, regulators often relax their normal requirements and refrain from closing financially troubled banks. I estimate the real effects of such regulatory forbearance by comparing differences in state-level economic outcomes by the amount of forbearance extended during the U.S. savings and loan crisis. To instrument for forbearance, I use historical variation in deposit insurance—and hence supervision—of similar financial intermediaries (thrifts) and exploit fixed differences between regional supervisors of the same regulator. The evidence suggests a policy-induced increase in high-risk loans during the official forbearance period (1982-89), followed by a broader bust in house prices and real GDP.",
        "article_title": "Does Going Easy on Distressed Banks Help Economic Growth?",
        "create_time": "2017-09-26T05:08:26.111164Z",
        "category": "国际清算银行"
        "authors": [
            {
                "sec_id": "A0330200010004",
                "analyst_name": "侯英民"
            },
            {
                "sec_id": "S0820112040006",
                "analyst_name": "刘孙亮"
            }
        ]},......,]
    """
    authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get']

    def is_subscribe(self, subscribe_id_list, favorites_list, page):
        r = []
        subscribe_list = []
        for subscribe_id in subscribe_id_list:
            subscribe_list += [tag['abbreviation'] for tag in TAGS if tag['id'] == int(subscribe_id)]
        try:
            # 获取列表页query set
            # begin = datetime.now() - timedelta(days=10)
            # end = datetime.now()
            # rr_list = ResearchReport.objects.filter(category__in=subscribe_list, created_at__range=[begin, end]).exclude(
            #     article_title="").exclude(article_content="").exclude(article_title=None).exclude(
            #     article_content=None).order_by('-created_at')
            rr_list = ResearchReport.objects.filter(category__in=subscribe_list).exclude(
                article_title="").exclude(article_content="").exclude(article_title=None).exclude(
                article_content=None).order_by('-created_at')
            research_report_list = rr_list[(page - 1) * 10: page * 10]
            count = rr_list.count()
        except ResearchReport.DoesNotExist:
            return []
        for research_report in research_report_list:
            authors = []
            try:
                authors_names = list(set([v.analyst_name for v in research_report.authors.all()]))
                for authors_name in authors_names:
                    authors.append({"analyst_name": authors_name,
                                    "uuid": [v.uuid for v in research_report.authors.filter(
                                        analyst_name=authors_name) if v.uuid][0]})
            except IndexError:
                authors = []
            try:
                category_title = [tag['title'] for tag in TAGS if tag['abbreviation'] == research_report.category][0]
            except IndexError:
                category_title = ""
            content = cleaning_content(research_report.article_content)
            content = content if content else "None"
            data = {'report_id': research_report.id,
                    'article_url': research_report.article_url,
                    'article_title': research_report.article_title,
                    'article_content': content[:500],
                    'attachment_url': research_report.attachment_url,
                    'create_time': str(calendar.timegm(research_report.created_at.timetuple())) + '000',
                    'category': category_title,
                    'enable_favorites': True if int(research_report.id) in favorites_list else False,
                    'pages': research_report.pages,
                    'authors': authors,
                    }
            data = format_rr_info(research_report.category, data)
            r.append(data)
        r = {"result": sorted(r, key=lambda k: k['create_time'])[::-1], "count": count}
        return r

    def get(self, request, *args, **kwargs):
        try:
            subscribe_list = '' if self.kwargs.get('subscribes_list') == '/' else self.kwargs.get('subscribes_list')
            page = int(self.kwargs.get("page"))
            if page <= 0:
                return Response("Invalid parameters", status=status.HTTP_400_BAD_REQUEST)
            user_profile = UserProfile.objects.get(user__id=self.request.user.id)
            favorites_list = user_profile.favorites_list
            try:
                subscribe_id_list = subscribe_list.split(',')
            except KeyError:
                return Response('Invalid parameters', status=status.HTTP_400_BAD_REQUEST)

            if subscribe_id_list[0] == '':
                return Response(data=[], status=status.HTTP_200_OK)

            r = self.is_subscribe(subscribe_id_list, favorites_list, page)
            return Response(data=r, status=status.HTTP_200_OK)
        except:
            logger.error(tb.format_exc())
            return Response("Invalid parameters", status=status.HTTP_400_BAD_REQUEST)


rr_initialization = RRInitializationAPI.as_view()


class GetSubscribeAPI(APIView):
    """
    描述：该类用于获取用户订阅信息
    response：[{"checked":false,"id":0,"title":"纽约联邦储备银"},{"checked":true,"id":1,"title":"日本银行"}........]
    """
    authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get']

    def get(self, request, **kwargs):
        r = []
        user_profile = UserProfile.objects.get(user_id=self.request.user.id)
        subscribe_list = user_profile.subscribe_list

        for tag in TAGS:
            if tag['abbreviation'] in subscribe_list:
                tag.update({'checked': True})
            else:
                tag.update({'checked': False})

        type_ids = list(set([(tag["type_id"], tag["type"]) for tag in TAGS]))
        for type_id in type_ids:
            type_dict = {"type_id": type_id[0], "type": type_id[1], "value": []}
            for tag in TAGS:
                if tag["type_id"] == type_id[0]:
                    type_dict["value"].append(tag)
            r.append(type_dict)

        for d in r:
            if False not in [v["checked"] for v in d["value"]]:
                d.update({"checked": True})
            else:
                d.update({"checked": False})

        return Response(data=r, status=status.HTTP_200_OK)


get_subscribe = GetSubscribeAPI.as_view()


class GetFavoritesAPI(APIView):
    """
    描述：该API用于获取用户喜好列表，如果用户没有like任何文章则返回空数组
    response：[1,2,3] or []
    """
    authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        user_obj = User.objects.get(id=self.request.user.id)
        user_profile = UserProfile.objects.get(user=user_obj)
        favorites_list = user_profile.favorites_list
        result = []
        for favorites in favorites_list:
            rr_obj = ResearchReport.objects.get(id=favorites)
            result.append({'title': rr_obj.article_title, 'id': favorites})
        return Response(data=result, status=status.HTTP_200_OK)


get_favorites = GetFavoritesAPI.as_view()


class GetAuthorAPI(APIView):
    """
    描述：该API用于获取分析师详细信息
    """
    authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            uuid = self.kwargs['uuid']
        except KeyError:
            return Response("Invalid parameters", status=status.HTTP_400_BAD_REQUEST)
        try:
            try:
                auth_obj_list = Author.objects.filter(uuid=uuid)
            except Author.DoesNotExist:
                return Response("Invalid parameters", status=status.HTTP_400_BAD_REQUEST)
            data = []
            for auth_obj in auth_obj_list:
                data.append({
                    "sec_id": auth_obj.sec_id,
                    "analyst_name": auth_obj.analyst_name,
                    "comp_name": auth_obj.comp_name,
                    "title": auth_obj.title,
                    "grant_date": auth_obj.grant_date,
                    "expire_date": auth_obj.expire_date,
                    "status": auth_obj.status,
                    "gender": auth_obj.gender,
                    "education": auth_obj.education,
                    "photo_path": auth_obj.photo_path,
                    "uuid": auth_obj.uuid,
                })
            data = sorted(data, key=lambda k: k['grant_date'])
            return Response(data, status=status.HTTP_200_OK)
        except:
            logger.error(tb.format_exc())
            return Response("Invalid parameters", status=status.HTTP_400_BAD_REQUEST)


get_author = GetAuthorAPI.as_view()


class GetAuthorReportAPI(APIView):
    """
    描述：用于获取某个分析师所撰写的全部内容
    """
    authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            uuid = self.kwargs['uuid']
            try:
                query = {v.split("=")[0]: v.split("=")[1] for v in request.GET.urlencode().split("&")}
                pages = int(query["page"])
            except:
                pages = 1
            user_profile = UserProfile.objects.get(user__id=self.request.user.id)
            favorites_list = user_profile.favorites_list
            rr_data = []

            rr_list = ResearchReport.objects.filter(authors__uuid=uuid).distinct()
            count = rr_list.count()
            if pages <= 0:
                return Response("Invalid parameters", status=status.HTTP_400_BAD_REQUEST)
            rr_cut_list = rr_list[(pages-1) * 10: pages * 10]

            for rr_cut in rr_cut_list:
                category_title = [tag['title'] for tag in TAGS if tag['abbreviation'] == rr_cut.category][0]
                authors = []
                authors_names = list(set([v.analyst_name for v in rr_cut.authors.all()]))
                for authors_name in authors_names:
                    authors.append({"analyst_name": authors_name,
                                    "uuid": [v.uuid for v in rr_cut.authors.filter(
                                        analyst_name=authors_name) if v.uuid][0]})
                d = {'report_id': rr_cut.id,
                     'article_url': rr_cut.article_url,'article_title': rr_cut.article_title,
                     'article_content': cleaning_content(rr_cut.article_content)[:500],
                     'attachment_url': rr_cut.attachment_url,
                     'create_time': str(calendar.timegm(rr_cut.created_at.timetuple())) + '000',
                     'category': category_title,
                     'enable_favorites': True if int(rr_cut.id) in favorites_list else False,
                     'pages': rr_cut.pages,
                     'authors': authors}
                d = format_rr_info(rr_cut.category, d)
                rr_data.append(d)
            r = {"count": count, "result": rr_data}
            return Response(data=r, status=status.HTTP_200_OK)
        except:
            logger.error(tb.format_exc())
            return Response("Invalid parameters", status=status.HTTP_400_BAD_REQUEST)


get_author_report = GetAuthorReportAPI.as_view()


class SimpleSearchAPI(APIView):
    """
    该类用于Elasticsearch检索

    Example:
    curl -X POST -H 'Content-Type: application/json' \
    -d '{"query_string": "业绩预报 汇川技术 邵晶鑫", "page": 0}' \
    http://localhost:8000/api/research_report/simple_search
    """
    # authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (AllowAny, )
    http_method_names = ['post']

    QUERY_TEMPLATE = {
        "size": 10,
        "query": {
            "bool": {
                "minimum_should_match" : 2,
                "should": [
                    {
                       "function_score": {
                          "gauss": {
                              "created_at": {
                                    "origin": "now",
                                    "scale": "365d",
                                    "decay" : 0.5
                              }
                          }
                      }
                    }
                ]
            }
        },
        "highlight" : {
            "pre_tags" : ["<em>"],
            "post_tags" : ["</em>"],
            "fields" : {}
        },
        "aggregations": {
            "company": {
                "terms": {
                    "field": "stocks_name"
                }
            },
            "author": {
                "terms": {
                    "field": "authors"
                }
            }
        }
    }

    def build_query(self, query_string, page=0):
        query_template = copy.deepcopy(self.QUERY_TEMPLATE)
        if page:
            query_template['from'] = query_template['size'] * int(page)
        field_weights = {
            "article_title": 2,
            "authors": 50,
            "stocks_name": 50,
            "article_content": 1,
            "attachment_words": 1
        }
        for kw in query_string.split(' '):
            kw = kw.strip()
            for k, v in field_weights.items():
                query_template['query']['bool']['should'].append({
                    "match": {
                        k: {
                            "query": kw,
                            "boost": v
                        }
                    }
                })
                query_template['highlight']['fields'][k] = {}
            similar_words = None
            try:
                similar_words = serve_touyantong(kw, final_embeddings, reverse_dictionary)
            except:
                pass
            if similar_words:
                logger.debug('Similar words:')
                logger.debug(similar_words)
                word, sim = similar_words[0][0], similar_words[1][0]
                if sim < 0.8:
                    continue
                for k, v in field_weights.items():
                    query_template['query']['bool']['should'].append({
                        "match": {
                            k: {
                                "query": word,
                                "boost": v * sim
                            }
                        }
                    })
        logger.debug(query_template)
        return query_template

    def post(self, request):
        try:
            req = request.data
            query_string = req.get("query_string")
            page = int(req.get("page", 0))
            if query_string:
                ret = es_client.search(
                    index=ES_INDEX,
                    doc_type=ES_DOCTYPE,
                    body=self.build_query(query_string, page),
                    request_cache=False
                )

                return Response(ret, status=status.HTTP_200_OK)
            else:
                raise Exception('query_string not specified.')
        except:
            logger.error(tb.format_exc())
            return Response(
                'Invalid parameters', status=status.HTTP_400_BAD_REQUEST)


simple_search = SimpleSearchAPI.as_view()

class AdvancedSearchAPI(APIView):
    """
    该类用于Elasticsearch检索

    Example:
    curl -X POST -H 'Content-Type: application/json' \
    -d '{"query_string": "业绩预报", "author": "邵晶鑫", "company": "汇川技术", "page": 0}' \
    http://localhost:8000/api/research_report/advanced_search
    """
    # authentication_class = (JSONWebTokenAuthentication, )
    permission_classes = (AllowAny, )
    http_method_names = ['post']

    QUERY_TEMPLATE = {
        "size": 10,
        "query": {
            "bool": {
                "minimum_should_match" : 2,
                "should": [
                    {
                       "function_score": {
                          "gauss": {
                              "created_at": {
                                    "origin": "now",
                                    "scale": "365d",
                                    "decay" : 0.5
                              }
                          }
                      }
                    }
                ]
            }
        },
        "highlight" : {
            "pre_tags" : ["<em>"],
            "post_tags" : ["</em>"],
            "fields" : {}
        },
        "aggregations": {
            "company": {
                "terms": {
                    "field": "stocks_name"
                }
            },
            "author": {
                "terms": {
                    "field": "authors"
                }
            }
        }
    }

    def build_query(self, query_dict):
        query_template = copy.deepcopy(self.QUERY_TEMPLATE)
        if query_dict['page']:
            query_template['from'] = query_template['size'] * int(query_dict['page'])
        if query_dict['author']:
            query_template['query']['bool']['should'].append({
                "match": {
                    "authors": {
                        "query": query_dict['author'],
                        "boost": 10
                    }
                }
            })
            query_template['highlight']['fields']['authors'] = {}
        if query_dict['company']:
            query_template['query']['bool']['should'].append({
                "match": {
                    "stocks_name": {
                        "query": query_dict['company'],
                        "boost": 10
                    }
                }
            })
            query_template['highlight']['fields']['stocks_name'] = {}
        field_weights = {
            "article_title": 2,
            # "authors": 10,
            # "stocks_name": 10,
            "article_content": 1,
            "attachment_words": 1
        }
        kw = query_dict['query_string']
        for k, v in field_weights.items():
            query_template['query']['bool']['should'].append({
                "match": {
                    k: {
                        "query": kw,
                        "boost": v
                    }
                }
            })
            query_template['highlight']['fields'][k] = {}
        similar_words = None
        try:
            similar_words = serve_touyantong(kw, final_embeddings, reverse_dictionary)
        except:
            pass
        if similar_words:
            logger.debug('Similar words:')
            logger.debug(similar_words)
            word, sim = similar_words[0][0], similar_words[1][0]
            for k, v in field_weights.items():
                query_template['query']['bool']['should'].append({
                    "match": {
                        k: {
                            "query": word,
                            "boost": v * sim
                        }
                    }
                })
        logger.debug(query_template)
        return query_template

    def post(self, request):
        try:
            req = request.data
            query_dict = {
                "query_string": req.get("query_string"),
                "author": req.get("author"),
                "company": req.get("company"),
                "page": req.get("page", 0)
            }

            ret = es_client.search(
                index=ES_INDEX,
                doc_type=ES_DOCTYPE,
                body=self.build_query(query_dict)
            )
            return Response(ret, status=status.HTTP_200_OK)
        except:
            logger.error(tb.format_exc())
            return Response(
                'Invalid parameters', status=status.HTTP_400_BAD_REQUEST)

advanced_search = AdvancedSearchAPI.as_view()
