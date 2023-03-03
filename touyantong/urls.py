"""touyantong URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_api.views import rr_urls, rr_details
from rest_api.views import update_subscribe, get_report_detail, favorites
from rest_api.views import rr_initialization, get_subscribe, get_favorites, rr_pdf
from rest_api.views import get_author, get_author_report
from rest_api.views import simple_search, advanced_search
from rest_auth import wechat
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    url(r'^$', schema_view),
    url(r'^admin/', admin.site.urls),
    url(r'^login/wechat_qr$', wechat.wechat_qr),
    url(r'^login/wechat$', wechat.WechatLogin.as_view()),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^api/token-auth', obtain_jwt_token),
    url(r'^api/token-refresh', refresh_jwt_token),
    # research report API
    url(r'^api/research_report/rr_urls', rr_urls, name='rr_urls'),
    url(r'^api/research_report/rr_details', rr_details, name='rr_details'),
    url(r'^api/research_report/rr_initialization/subscribes=(?P<subscribes_list>.+)/(?P<page>\d+)/$',
        rr_initialization, name='rr_initialization'),
    url(r'^api/research_report/get_report_detail/(?P<report_id>\d+)/$', get_report_detail, name='get_report_detail'),
    url(r'^api/research_report/rr_pdf', rr_pdf, name='rr_pdf'),
    url(r'^api/research_report/simple_search', simple_search, name='simple_search'),
    url(r'^api/research_report/advanced_search', advanced_search, name='advanced_search'),
    # user API
    url(r'^api/user/get_subscribe', get_subscribe, name='get_subscribe'),
    url(r'^api/user/update_subscribe', update_subscribe, name='update_subscribe'),
    url(r'^api/user/favorites', favorites, name='user_favorites'),
    url(r'^api/user/get_favorites', get_favorites, name='get_favorites'),
    # author API
    url(r'^api/author/(?P<uuid>[0-9a-f-]+)/$', get_author, name='get_author'),
    url(r'^api/author/(?P<uuid>[0-9a-f-]+)/rr/$', get_author_report, name='get_author_report')
]
