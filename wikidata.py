import collections
import collections.abc

# Ensure compatibility for collections.MutableMapping
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

import sparql
import requests

session = requests.Session()
URL = 'https://www.wikidata.org/w/api.php'


def wbgetentities(name):
    res = session.post(URL, data={
        'action': 'wbsearchentities',
        'search': name,
        'language': 'ru',
        'format': 'json',
    })
    try:
        res_json = res.json()['search'][0]['id']
    except:
        res_json = None
    return res_json


def create_query(first_id):
    if first_id is None:
        return None
    q = ('''
    PREFIX entity: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT ?syno
    WHERE {
      ?O ?P ?id .
      OPTIONAL{?id skos:altLabel ?syno
          filter (lang(?syno) = 'ru')}
      VALUES ?id {entity:''' + first_id + '''}   
      SERVICE wikibase:label {bd:serviceParam wikibase:language "ru" .}}''')
    return q


def get_syns(string):
    Q_id = wbgetentities(string)
    if Q_id is None:
        print("No entity found for the string:", string)
        return
    synonyms = []
    query = create_query(Q_id)
    if query is None:
        print("No query could be created for the ID:", Q_id)
        return
    result = sparql.query('https://query.wikidata.org/sparql', query)
    for r in result:
        values = sparql.unpack_row(r)
        if values[0] not in synonyms:
            synonyms.append(values[0])
    print(synonyms)


get_syns('шнур питания')
