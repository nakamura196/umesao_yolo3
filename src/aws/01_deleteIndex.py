import elasticsearch
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

INDEX = "curations"

host = 'search-umesao-pvihnpop66hr2dllhikpv23qz4.us-east-1.es.amazonaws.com'

profile_name = "cj-app-user"
region = "us-east-1"

session = boto3.Session(profile_name=profile_name)
credentials = session.get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                   region, 'es', session_token=credentials.token)

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

if es.indices.exists(index=INDEX):
    es.indices.delete(INDEX)
es.indices.create(index=INDEX)