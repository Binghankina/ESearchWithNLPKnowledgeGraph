from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from rest_api.models import WeChatUser

from hashlib import sha256
import traceback
import logging
import requests
import random
import string
import json

from .app_settings import create_token
from .models import TokenModel
from .utils import jwt_encode


logger = logging.getLogger('default')


def _get_token(user):
    token = None
    if getattr(settings, 'REST_USE_JWT', False):
        token = jwt_encode(user)
    else:
        token = create_token(TokenModel, user, None)
    return token


@csrf_exempt
@require_http_methods(['POST'])
def wechat_qr(request):
    # https://open.weixin.qq.com/connect/qrconnect?appid=wxf293d1783b203f43&redirect_uri=http://www.touyantong.com/complete/weixin/&state=8et1vPLPiW1HkxS6M53bKyqJTlg1svqb&response_type=code&scope=snsapi_login
    r = {'error': None, 'url': None}
    if request.user.is_authenticated():
        r['token'] = _get_token(request.user)
        r['error'] = 'Error: already logged in'
        return JsonResponse(r, status=400)
    sid = ''
    try:
        body = json.loads(request.body.decode('utf-8'))
        sid = body['sid']
    except:
        r['error'] = 'Error: parameter. Use Json!'
        return JsonResponse(r, status=400)

    if not sid:
        r['error'] = 'Error: sid'
        return JsonResponse(r, status=400)

    s = '%s%s' % (sid, settings.SOCIAL_AUTH_WEIXIN_RANDOM_STR)
    state = sha256(s.encode('utf-8')).hexdigest()

    redirect_uri = 'http://www.touyantong.com/login/wechat'
    d = {
        'appid': settings.SOCIAL_AUTH_WEIXIN_KEY,
        'redirect_uri': redirect_uri,
        'state': state,
        'response_type': 'code',
        'scope': 'snsapi_login'
    }
    r['url'] = 'https://open.weixin.qq.com/connect/qrconnect?' + urlencode(d)
    return JsonResponse(r, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class WechatLogin(View):
    '''
    See more: http://www.jianshu.com/p/e3c6fe7b2f9b
    '''

    def post(self, request):
        r = {'error': None, 'status': None, 'token': None}
        if request.user.is_authenticated():
            r['status'] = 'Already authenticated'
            return JsonResponse(r)

        sid = ''
        try:
            body = json.loads(request.body.decode('utf-8'))
            sid = body['sid']
        except:
            r['error'] = 'Error: parameter. Use Json!'
            return JsonResponse(r, status=400)

        if not sid:
            r['error'] = 'Error: sid'
            return JsonResponse(r, status=400)

        # 第一步获取code跟state

        logger.info(body)
        try:
            code = body['code']
            state = body['state']
            s = '%s%s' % (sid, settings.SOCIAL_AUTH_WEIXIN_RANDOM_STR)
            state_true =  sha256(s.encode('utf-8')).hexdigest()
            if state != state_true:
                r['error'] = 'Error: wrong sid'
                return JsonResponse(r, status=400)
        except:
            logger.error("获取code和stat参数错误：\n%s" % traceback.format_exc())
            r['error'] = 'Error: code/state'
            return JsonResponse(r, status=400)

        # 2.通过code换取网页授权access_token
        try:
            url = u'https://api.weixin.qq.com/sns/oauth2/access_token'
            params = {
                'appid': settings.SOCIAL_AUTH_WEIXIN_KEY,
                'secret': settings.SOCIAL_AUTH_WEIXIN_SECRET,
                'code': code,
                'grant_type': 'authorization_code'
            }
            res = requests.get(url, params=params).json()
            logger.debug(res)
        except:
            logger.error("获取access_token参数错误：\n%s" %
                         str(traceback.format_exc()))
            r['error'] = 'Error: access_token'
            return JsonResponse(r, status=400)

        # 3.如果access_token超时，那就刷新
        # 注意,这里我没有写这个刷新功能,不影响使用,如果想写的话,可以自己去看文档

        # 4.拉取用户信息
        try:
            user_info_url = u'https://api.weixin.qq.com/sns/userinfo'
            params = {
                'access_token': res["access_token"],
                'openid': res["openid"],
            }
            res = requests.get(user_info_url, params=params).json()
            res['nickname'] = res['nickname'].encode(
                'iso8859-1').decode('utf-8')
            logger.debug(res)
            try:
                wechat_user = WeChatUser.objects.get(openid=res['openid'])
            except WeChatUser.DoesNotExist:
                del res['privilege']
                pw = ''.join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(15)
                )
                user, _ = User.objects.get_or_create(
                    username=res['openid'],
                    defaults={"password": pw}
                )
                res['user'] = user
                wechat_user = WeChatUser.objects.create(**res)
            # Authenticate user here
            login(request, wechat_user.user)
            r['status'] = 'Authenticated'
        except:
            logger.info("拉取用户信息错误：\n%s" % str(traceback.format_exc()))
            r['error'] = 'Error: userinfo'
            return JsonResponse(r, status=400)


        r['token'] = _get_token(wechat_user.user)
        return JsonResponse(r)
