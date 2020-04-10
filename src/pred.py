import sys
import argparse
from yolo import YOLO, detect_video
from PIL import Image
import glob
import json
import os
import requests
import shutil

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

yolo = YOLO()

dir = "/Users/nakamura/git/d_umesao/umesao_images/docs/iiif/item"

files = glob.glob(dir+"/*/manifest.json")

for i in range(len(files)):

    print(str(i+1)+"/"+str(len(files)))

    file = files[i]

    with open(file) as f:
        df = json.load(f)

    id = file.split("/item/")[1].replace("/manifest.json", "")

    manifest_uri = df["@id"]
    print(manifest_uri)

    sequences = df["sequences"]

    members = []

    odir = "../docs/iiif/curation/" + id
    os.makedirs(odir, exist_ok=True)

    opath = odir + "/curation.json"

    if True:
        if os.path.exists(opath):
            continue

    for i in range(len(sequences)):

        canvases = sequences[i]["canvases"]

        for j in range(len(canvases)):

            print(str(j)+"/"+str(len(canvases)))
            canvas = canvases[j]

            path = canvas["thumbnail"]["@id"]

            tmp_path = "tmp.jpg"

            if path.startswith('http') or path.startswith('gs:'):
                tmp = path.split("https://")
                path = "https://cj:!cj@"+tmp[1]
                download_img(path, tmp_path)

            ##############

            try:
                image = Image.open(tmp_path)
            except Exception as e:
                print(e)
                continue 
            th_w, th_h = image.size
            
            org_w = canvas["width"]

            # オリジナルサイズ
            r = org_w / th_w

            result = yolo.detect_image(image)
            print(result)

            ##############

            for obj in result:
                x = str(int(obj["x"] * r))
                y = str(int(obj["y"] * r))
                w = str(int(obj["w"] * r))
                h = str(int(obj["h"] * r))

                canvas_uri = canvas["@id"]
                member_uri = canvas_uri + "#xywh=" + x + "," + y + "," + w + "," + h
                chars = obj["label"]

                label = "YOLO v3"

                member = {
                    "@id": member_uri,
                    "@type": "sc:Canvas",
                    "label": chars,
                    "metadata": [
                        {
                            "label": "Method",
                            "value": label
                        },
                        {
                            "label": "Score",
                            "value": str(obj["score"])
                        }
                    ]
                }

                members.append(member)

    prefix = "https://nakamura196.github.io/umesao_yolo3"

    curation = {
        "@context": [
            "http://iiif.io/api/presentation/2/context.json",
            "http://codh.rois.ac.jp/iiif/curation/1/context.json"
        ],
        "@id": prefix + "/iiif/curation/"+id+"/curation.json",
        "@type": "cr:Curation",
        "label": "Character List",
        "selections": [
            {
                "@id": prefix + "/iiif/curation/"+id+"/range1",
                "@type": "sc:Range",
                "label": "Characters",
                "members": members,
                "within": {
                    "@id": manifest_uri,
                    "@type": "sc:Manifest",
                    "label": df["label"]
                }
            }
        ]
    }

    fw = open(opath, 'w')
    json.dump(curation, fw, ensure_ascii=False, indent=4,
        sort_keys=True, separators=(',', ': '))

yolo.close_session()


    
