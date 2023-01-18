import string
import numpy as np
from elasticsearch import Elasticsearch
import json
from googletrans import Translator
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk import word_tokenize
from nltk.corpus import stopwords
import io
import nltk
# nltk.download('stopwords')
# nltk.download('punkt')

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


def remove_stop_words(search_term):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(search_term)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
    # remove punctuation and possessive terms
    filtered_sentence = [w for w in filtered_sentence if not (w == "'s")]
    filtered_sentence = ' '.join(filtered_sentence).translate(str.maketrans('', '', string.punctuation))
    print("filtered sentence: ", filtered_sentence)
    return filtered_sentence


def check_similarity(documents):
    tfidfvectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidfvectorizer.fit_transform(documents)

    cs = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
    similarity_list = cs[0][1:]
    return similarity_list


def translate_to_english(value):
    translator = Translator()
    english_term = translator.translate(value, dest='en')
    return english_term.text


def intent_classifier(search_term):
    select_type = -1
    result_word = ''
    field_intent = ''


    keyword_metaphor_meaning = ["Meaning", "meaning_of_metaphor", "metaphor_meaning"]
    keyword_source = ["Source_domain", "source", "metaphor source_domain"]
    keyword_target = ["Target_domain", "target", "metaphor target_domain"]
    keyword_metaphor = ["Metaphor"]
    keyword_artist = ["Artist", "singer", "sing_by", "sung_by"]
    keyword_lyricist = ["Lyricist", "writer", "written_by"]

    keyword_fields = [keyword_metaphor_meaning, keyword_source, keyword_target, keyword_metaphor, keyword_artist,
                      keyword_lyricist]

    search_term = remove_stop_words(search_term)

    search_term_list = search_term.split()

    query_words = search_term_list.copy()
    for i in search_term_list:
        for keyword_list in keyword_fields:
            documents = [i]
            documents.extend(keyword_list)

            max_val = max(check_similarity(documents))
            if max_val > 0.9:
                select_type = 0
                field_intent = keyword_list[0]
                print("field intent: " + field_intent)
                query_words.remove(i)

    result_word = ' '.join(query_words)

    print("select_type: {}, result_word: {}, field_intent: {} ".format(select_type, result_word, field_intent))
    return select_type, result_word, field_intent


def search_query(search_term):
    english_term = translate_to_english(search_term)
    select_type, strip_term, field_intent = intent_classifier(english_term)

    if select_type == -1:
        list_songs, artists, lyricist, lyrics = search_text(search_term)
    else:
        if strip_term:
            list_songs, artists, lyricist, lyrics = search_text_multi_match(strip_term, select_type, field_intent)
        else:
            list_songs, artists, lyricist, lyrics = search_text_multi_match(search_term, select_type, field_intent)

    return list_songs, artists, lyricist, lyrics


def search_text_multi_match(search_term, select_type, field_intent):
    query_term = search_term
    if select_type == -1:
        english_term = translate_to_english(search_term)
    else:
        english_term = search_term

    f = io.open('song-corpus/songs_metadata.json',
                mode="r",
                encoding="utf-8")
    meta_data = json.loads(f.read())

    data=[]
    if field_intent=="Meaning":
        data = meta_data["meaning"]
    elif field_intent == "Source_domain":
        data = meta_data["source_domain"]
    elif field_intent == "Target_domain":
        data = meta_data["target_domain"]
    elif field_intent == "Metaphor":
        data = meta_data["metaphor"]
    elif field_intent == "Artist":
        data = meta_data["artist"]
    elif field_intent == "Lyricist":
        data = meta_data["lyricist"]

    documents_meanings = [english_term]
    documents_meanings.extend(data)

    similarity_list = check_similarity(documents_meanings)

    max_val = max(similarity_list)
    if max_val > 0.9:
        loc = np.where(similarity_list == max_val)
        i = loc[0][0]
        query_term = data[i]  # if name is found, search for that to avoid spelling errors

    print("Searched in index: ", query_term)
    # results = es.search(index='index-songs', doc_type='sinhala-songs', body={
    #     "size": 100,
    #     "query": {
    #         "multi_match": {
    #             "query": query_term,
    #             "type": "best_fields",
    #             "fields": [
    #                 "Title", "Title_en", "Artist", "Album", "Album_en", "Released year", "Lyricist",
    #                 "Lyrics", "Metaphor", "Metaphor_en", "Meaning", "Source", "Target"]
    #         }
    #     },
    # })
    results = es.search(index='index-songs', doc_type='sinhala-songs', body={
        "size": 100,
        "query": {
            "multi_match": {
                "query": query_term,
                "type": "best_fields",
                "fields": [ field_intent  ]
            }
        },
    })
    # results = es.search(index='index-songs', doc_type='sinhala-songs', body={
    #     "size": 100,
    #     "query": {
    #         "term": {
    #             field_intent:{
    #                 "value": query_term
    #             }
    #         }
    #     },
    # })
    print(query_term)
    list_songs, artists, lyricist, lyrics = post_processing_text(results)
    return list_songs, artists, lyricist, lyrics


def search_text(search_term):
    results = es.search(index='index-songs', doc_type='sinhala-songs', body={
        "size": 500,
        "query": {
            "multi_match": {
                "query": search_term,
                "type": "best_fields",
                "fields": [
                    "Title", "Title_en", "Artist", "Album", "Album_en", "Released year", "Lyricist",
                    "Lyrics", "Metaphor", "Metaphor_en", "Meaning", "Source", "Target"]

            }
        },
        "aggs": {
            "title": {
                "terms": {
                    "field": "Title.keyword",
                    "size": 15
                }
            },
            "album": {
                "terms": {
                    "field": "Album.keyword",
                    "size": 15
                }
            },
            "metaphor": {
                "terms": {
                    "field": "Metaphor.keyword",
                    "size": 15
                }
            },

        }
    })

    list_songs, artists, lyricist, lyrics = post_processing_text(results)
    return list_songs, artists, lyricist, lyrics


def post_processing_text(results):
    list_songs = []
    for i in range(len(results['hits']['hits'])):
        lyrics = json.dumps(results['hits']['hits'][i]['_source']["Lyrics"], ensure_ascii=False)
        lyrics = lyrics.replace('"', '')
        lyrics = lyrics.replace("'", '')
        lyrics = lyrics.replace('\\', '')
        lyrics = lyrics.replace('t', '')
        lyrics = lyrics.replace('\xa0', '')
        lyrics = lyrics.replace('n', ' ')
        lyrics = re.sub(r'(<br> )+', r'\1', lyrics)
        results['hits']['hits'][i]['_source']["Lyrics"] = lyrics
        list_songs.append(results['hits']['hits'][i]['_source'])
    # aggregations = results['aggregations']
    # lyricist = aggregations['Lyricist']['buckets']
    # artists = aggregations['Artist']['buckets']
    # lyrics = aggregations['Lyrics']['buckets']
    artists, lyricist, lyrics = [], [], []
    return list_songs, artists, lyricist, lyrics
