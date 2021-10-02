from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from name_is_coming.settings import INDEX_NAME


def save_satellites(es: Elasticsearch, satellites):
    bulk(es, satellites, index=INDEX_NAME)


def get_satellites(es: Elasticsearch) -> dict:
    return es.search(index=INDEX_NAME, body={'query': {'match_all': {}}})
