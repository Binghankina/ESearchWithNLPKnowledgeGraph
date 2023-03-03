import elasticsearch
import logging
from django.conf import settings

logger = logging.getLogger('default')


ES_INDEX = 'reports'
ES_DOCTYPE = 'research'
es_client = elasticsearch.Elasticsearch([{'host': settings.ES_HOST}])


def create_index():
    if es_client.indices.exists(ES_INDEX):
        return

    es_client.indices.create(
        index=ES_INDEX,
        body={
            "mappings": {
                ES_DOCTYPE: {
                    "_source": {
                        "enabled": True
                    },
                    "properties": {
                        "article_title": {
                            "type": "text",
                            "analyzer": "ik_smart",
                            "search_analyzer": "ik_smart",
                            "term_vector": "yes"
                        },
                        "article_content": {
                            "type": "text",
                            "analyzer": "ik_smart",
                            "search_analyzer": "ik_smart",
                            "term_vector": "yes"
                        },
                        "attachment_words": {
                            "type": "text",
                            "analyzer": "ik_smart",
                            "search_analyzer": "ik_smart",
                            "term_vector": "yes"
                        },
                        "stocks_name": {
                            "type": "keyword",
                            "index": "not_analyzed"
                        },
                        "authors": {
                            "type": "keyword",
                            "index": "not_analyzed"
                        },
                        "publish_date": {
                            "type": "date",
                            "format": "strict_date_optional_time||epoch_millis"
                        }
                    }
                }
            }}
    )
    logger.info('Elasticsearch index created')


def index_report(rr):
    # Just in case index was not created
    create_index()
    authors = []
    for a in rr.authors.all():
        authors.append(a.analyst_name)
    body = {
        "article_title": rr.article_title,
        "article_content": rr.article_content,
        "attachment_words": rr.attachment_words,
        "stocks_name": rr.stocks_name,
        "authors": authors,
        "created_at": rr.created_at
    }
    es_client.index(index=ES_INDEX, doc_type=ES_DOCTYPE, body=body, id=rr.pk)


if __name__ == '__main__':
    create_index()
