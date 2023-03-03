import json
import logging
from logging.handlers import RotatingFileHandler
import requests
from touyantong.settings import LOGGING_LEVEL, PDF_PARSER_HOST


def get_logger():
    logger = logging.getLogger('root')
    FORMAT = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)s - " \
             "%(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    handler = RotatingFileHandler(
        'run.log', maxBytes=1e8, backupCount=10, encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(handler)
    logger.setLevel(LOGGING_LEVEL)
    return logger


logger = get_logger()


def jsonLoader(data, server, token):
    payload = json.dumps(data)
    r = requests.post(server,
                      headers={
                        'X-Api-Token': token,
                        'Content-Type': 'application/json'
                      },
                      data=payload,
                      timeout=25)
    logger.info("[CONTENT_PARSER] %s url: %s " % (str(r.status_code), data.get("url")))
    return r


def pdf_parser(attachment_url, hash):
    payload = {"pdf_url": attachment_url, "hash": hash}
    r = requests.post(PDF_PARSER_HOST,
                      headers={'Content-Type': 'application/json'},
                      json=payload,
                      timeout=300)
    logger.info("[PDF_PARSER] %s id: %s" % (str(r.status_code), hash))
