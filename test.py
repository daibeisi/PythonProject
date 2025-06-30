import os
import json

import requests
import hashlib
from urllib.parse import urlencode

create_api = 'https://pan.baidu.com/rest/2.0/xpan/file?'
precreate_api = 'https://pan.baidu.com/rest/2.0/xpan/file?'
upload_api = 'https://c3.pcs.baidu.com/rest/2.0/pcs/superfile2?'
# upload_api = 'https://d.pcs.baidu.com/rest/2.0/pcs/superfile2?'

file_path = 'C:\\Users\\admin\\Downloads\\voc_label.zip'
access_token = "121.b0710914a65e092f27316039c343c5a8.YloH4YHWfFab5TwfhLz4J0K_UG1FclsKcdf85be.KB96IA"
remote_path = "/Coovally/voc_label.zip"

size = os.path.getsize(file_path)
block_list = []
with open(file_path, 'rb') as f:
    data = f.read()
    file_md5 = hashlib.md5(data).hexdigest()
    block_list.append(file_md5)
    f.close()
block_list = json.dumps(block_list)
api = precreate_api + "method=precreate&access_token=" + access_token
payload = {
    'path': remote_path,
    'size': size,
    'rtype': 3,
    'isdir': 0,
    'autoinit': 1,
    'block_list': block_list
}
response = requests.request("POST", api, headers={}, data=payload, files=[])
# 解析json
print(response.content)
json_resp = json.loads(response.content)

data = {}
files = [
    ('file', open(file_path, 'rb'))
]
params = {
    'method': 'upload',
    'access_token': access_token,
    'path': remote_path,
    'type': 'tmpfile',
    'uploadid': json_resp['uploadid'],
    'partseq': 0
}
api = upload_api + urlencode(params)
res = requests.request('post', api, data=data, files=files)
print(res.content)

params = {
    'method': 'create',
    'access_token': access_token
}
api = create_api + urlencode(params)
data = {
    'path': remote_path,
    'size': size,
    'is_dir': 0,
    'uploadid': json_resp['uploadid'],
    'block_list': block_list,
    'rtype': 3
}
response = requests.post(api, data=data)
print(response.content)