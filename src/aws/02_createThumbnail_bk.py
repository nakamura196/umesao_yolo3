import sys
from classes import uploader
import csv
import glob
import json
import requests
import hashlib
import os
from hashlib import md5

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

files = glob.glob("/Users/nakamura/git/d_umesao/umesao-yolo3/docs/iiif/curation/*/curation.json")
files = sorted(files)

for file in files:
    try:
        with open(file) as f:
            df = json.load(f)
            members = df["selections"][0]["members"]

            manifest = df["selections"][0]["within"]["@id"]

            id = manifest.split("/")[-2]

            canvas_id_thumb_map = {}

            with open("/Users/nakamura/git/d_umesao/umesao_images/docs/iiif/item/"+id+"/manifest.json") as f:
                df2 = json.load(f)
                canvases = df2["sequences"][0]["canvases"]

                for canvas in canvases:
                    canvas_id_thumb_map[canvas["@id"]] = canvas["thumbnail"]["@id"]

            curation_uri = df["@id"]

            for i in range(len(members)):
                member = members[i]
                member_id = member["@id"]
                hash = md5(member_id.encode('utf-8')).hexdigest()

                opath = "/Users/nakamura/git/thumbnail/umesao/curations/" + hash + ".jpg"

                if not os.path.exists(opath):

                    canvas_id = member_id.split("#")[0]
                    thumbnail = canvas_id_thumb_map[canvas_id]

                    xywh = ""
                    metadata = member["metadata"]

                    for obj in metadata:
                        label = obj["label"]
                        if label == "Thubmnail Region":
                            xywh = obj["value"]

                    if xywh != "":

                        th_path = "/Users/nakamura/git/thumbnail/umesao/image/" + thumbnail.split("/image/")[1]
                        
                        if not os.path.exists(th_path):
                            base_dir_pair = os.path.split(th_path)
                            os.makedirs(base_dir_pair[0], exist_ok=True)
                            
                            tmp = thumbnail.split("https://")
                            path = "https://cj:!cj@"+tmp[1]
                            
                            # print(path, th_path)
                            # download_img(path, th_path)
                            # print("----------")
                        else:
                            print(th_path)

                        # print(thumbnail+"#xywh="+xywh)


    except Exception as e:
        print(e)