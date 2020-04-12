import sys
from classes import uploader
import csv
import glob
import json
import requests
import hashlib
import os
from hashlib import md5

INDEX = "curations"

HOST = 'search-umesao-pvihnpop66hr2dllhikpv23qz4.us-east-1.es.amazonaws.com'

PROFILE_NAME = "cj-app-user"
REGION = "us-east-1"

files = glob.glob("/Users/nakamura/git/d_umesao/umesao-yolo3/docs/iiif/curation/*/curation.json")
files = sorted(files)

all_bodies = []

for file in files:
    try:
        with open(file) as f:
            df = json.load(f)
            members = df["selections"][0]["members"]

            curation_uri = df["@id"]

            for i in range(len(members)):
                member = members[i]
                member_id = member["@id"]
                hash = md5(member_id.encode('utf-8')).hexdigest()

                body = {
                    "_type" : "_doc",
                    "_index" : INDEX,
                    "_id": hash,
                    
                    "_title": [member["label"]],
                    "_url": ["http://codh.rois.ac.jp/software/iiif-curation-viewer/demo/?curation="+curation_uri+"&pos="+str(i+1)],
                }

                if "thumbnail" in member:
                    body["_image"] = [member["thumbnail"]]

                metadata = member["metadata"]
                for obj in metadata:
                    label = obj["label"]
                    value = obj["value"]

                    if "label" == "タイトル":
                        body["_title"] = value
                        continue

                    if "西暦コード" in label and "?" in str(value):
                        continue

                    if label not in body:
                        body[label] = []
                    if value not in body[label]:
                        body[label].append(value)

                all_bodies.append(body)

    except Exception as e:
        print(e)

print(len(all_bodies))

uploader.Uploader.main(
    index=INDEX, 
    host=HOST, 
    region=REGION, 
    profile_name=PROFILE_NAME, 
    all_body=all_bodies)