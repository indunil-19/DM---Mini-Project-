from elasticsearch import Elasticsearch, helpers
import json


es = Elasticsearch([{'host': 'localhost', 'port':9200}])

def data_upload():
    with open('song-corpus/songs_final.json') as f:
        data = json.loads(f.read())
    helpers.bulk(es, data, index='index-songs', doc_type='sinhala-songs')


if __name__ == "__main__":
    data_upload()
    # es.indices.delete(index='index-songs', ignore=[400, 404])


