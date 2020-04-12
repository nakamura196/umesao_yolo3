import elasticsearch
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
from requests_aws4auth import AWS4Auth
import json
import glob

class Uploader:

    all_body = []

    @classmethod
    def main(self, index, host, all_body, region=None, profile_name=None):

        self.all_body = all_body

        if profile_name == None:
            es = Elasticsearch([host])
        else:

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
            
        res = elasticsearch.helpers.streaming_bulk(client=es, actions=all_body, chunk_size=1000, max_retries=5,
                                                    initial_backoff=2, max_backoff=600, request_timeout=3600)
        for ok, response in res:
            print(ok, response)

    def create_documents(self):
        for body in self.all_body:
            yield body

    @classmethod
    def generateAllBody(self, converted_dir, source, index):

        all_body = []

        files = glob.glob(converted_dir + "/"+source+"/*.json")
        files = sorted(files)

        for i in range(len(files)):
            file = files[i]

            # メイン
            if i % 1000 == 0:
                print(str(source)+"\t"+str(i+1)+"/"+str(len(files))+"\t"+file)

            try:
                with open(file) as f:
                    body = json.load(f)
                    body["_type"] = "_doc"
                    body["_index"] = index
                    all_body.append(body)
            except Exception as e:
                print(e)

        return all_body