import requests

# https://kauth.kakao.com/oauth/authorize?client_id=1154f10a10d49893b5b64a07f7197eb5&redirect_uri=https://example.com/oauth&response_type=code&scope=talk_message,friends


# Step 1. 위에서 설정한 주소를 통해 authorize_code 코드 받아온 뒤 하단에 셋팅

url = 'https://kauth.kakao.com/oauth/token'
rest_api_key = '1154f10a10d49893b5b64a07f7197eb5'
redirect_uri = 'https://example.com/oauth'
authorize_code = 'awx7s9jjccY62c7Iu79G1CT-RFrMCtou_44cJVBjketGCyIqr1G6rBPc0ZZNavu0u7gAawo9c04AAAF-ytubcg'

data = {
    'grant_type':'authorization_code',
    'client_id':rest_api_key,
    'redirect_uri':redirect_uri,
    'code': authorize_code,
    }

response = requests.post(url, data=data)
tokens = response.json()
print(tokens)

# Step 2. kakao_server_key.py 실행하여 발급된 Key 값을 json 파일에 저장
import json

# C:\Users\nmh88\Desktop\PythonWorkspace\Key
with open(r"C:\Users\nmh88\Desktop\PythonWorkspace\FlaskApi\Kakao\kakao_code.json","w") as fp:
    json.dump(tokens, fp)