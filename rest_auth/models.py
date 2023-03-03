from django.conf import settings
from rest_framework.authtoken.models import Token as DefaultTokenModel

from .utils import import_callable


TokenModel = import_callable(
    getattr(settings, 'REST_AUTH_TOKEN_MODEL', DefaultTokenModel))
