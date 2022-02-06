from typing import Text
import requests
import json

import schedule
import time
import os, json

#〓〓〓〓〓〓〓〓〓〓〓〓DBMS Config〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓  
import pymssql

BASE_DIR = "./"
secret_file = os.path.join(BASE_DIR, 'secrets.json')

# Step 1. DB 연결구간
with open(secret_file) as f:
    secrets = json.loads(f.read())
 
def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        err_msg = f"set the {setting} enviroment variable"
        raise print(err_msg)
        

db_host = get_secret("DB_HOST")
db_user = get_secret("DB_USER")
db_pass = get_secret("DB_PASS")
db_port = get_secret("DB_PORT")
db_name = get_secret("DB_NAME_SUB") #BOT
 
conn =  pymssql.connect(db_host , db_user, db_pass, db_name)

# Step 2. Kakao 친구 목록 호출 구간
# kakao_server_key.py 에서 발급한 키값을 하단 Json에 저장하고 불러오기
with open(r"C:\Users\nmh88\Desktop\PythonWorkspace\FlaskApi\Kakao\kakao_code.json","r") as fp:
    tokens = json.load(fp)

friend_url = "https://kapi.kakao.com/v1/api/talk/friends"

headers={"Authorization" : "Bearer " + tokens["access_token"]}

result = json.loads(requests.get(friend_url, headers=headers).text)

friends_list = result.get("elements")
friend_id = friends_list[0].get("uuid")
print("Friend ID : " + friend_id)
 
send_url= "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"

data={
    'receiver_uuids': '["{}"]'.format(friend_id),
    "template_object": json.dumps({
        "object_type": "text",
        "text": "Start",
        "link": {
            "web_url":"www.daum.net",
            "web_url":"www.naver.com"
        },
        "button_title": "바로 확인"
        })
    }

response = requests.post(send_url, headers=headers, data=data)
print(response)
response.status_code


def job():

    cursor = conn.cursor()

    cursor.callproc('GET_RANDOM_SENTENCE')

    resultData = [row for row in cursor]

    cursor.close()

    print("Random Data : " + resultData[0][0] + ", " + str(resultData[0][1]))

    dataReal={
    'receiver_uuids': '["{}"]'.format(friend_id),
    "template_object": json.dumps({
        "object_type": "text",
        "text": resultData[0][0],
        "link": {
            "web_url":"www.daum.net",
            "mobile_web_url":"www.naver.com"
        },
        "button_title": "정답 확인"
        })
    }

    response = requests.post(send_url, headers=headers, data=dataReal)
    response.status_code

    print("Send Success!!!")





# 10초에 한번씩 실행
schedule.every(2).seconds.do(job)
# 10분에 한번씩 실행
# schedule.every(10).minutes.do(job)
# 매 시간 실행
# schedule.every().hour.do(job)
# 매일 10:30 에 실행
# schedule.every().day.at("10:30").do(job)
# 매주 월요일 실행
# schedule.every().monday.do(job)
# 매주 수요일 13:15 에 실행
# schedule.every().wednesday.at("13:15").do(job)
 

while True:
    schedule.run_pending()
    time.sleep(1)




















# data={
#     'receiver_uuids': '["{}"]'.format(friend_id),
#     "template_object": json.dumps({
#         "object_type":"text",
#         "text":"성공입니다!",
#         "link":{
#             "web_url":"www.daum.net",
#             "web_url":"www.naver.com"
#         },
#         "button_title": "바로 확인"
#     })
# }


# List 형식
# template = {
#     "object_type" : "list",
#     "header_title" : "DeadLock Detected!",
#     "header_link" : {
#         "web_url" : "www.naver.com",
#         "mobile_web_url" : "www.naver.com"
#     },
#     "contents" : [
#         {
#             "title" : "1. SYSTEM ",
#             "description" : ": MES 시스템",
#             "image_url" : "",
#             "image_width" : 10, "image_height" : 10,
#             "link" : {
#                 "web_url" : "www.hyundai-autoever.com",
#                 "mobile_web_url" : "www.hyundai-autoever.com"
#             }
#         },
#         {
#             "title" : "2. IP",
#             "description" : ": 127.0.0.1",
#             "image_url" : "",
#             "image_width" : 50, "image_height" : 50,
#             "link" : {
#                 "web_url" : "www.hyundai-autoever.com",
#                 "mobile_web_url" : "www.hyundai-autoever.com"
#             }
#         },
#         {
#             "title" : "3. DB & Table",
#             "description" : ": MES.dbo.TEST",
#             "image_url" : "https://www.hyundai.co.kr/images/affiliates/others/img-autoever-logo.gif",
#             "image_width" : 50, "image_height" : 50,
#             "link" : {
#                 "web_url" : "www.hyundai-autoever.com",
#                 "mobile_web_url" : "www.hyundai-autoever.com"
#             }
#         }
        
#     ],
#     "buttons" : [
#         {
#             "title" : "웹으로 이동",
#             "link" : {
#                 "web_url" : "www.naver.com",
#                 "mobile_web_url" : "www.naver.com"
#             }
#         }
#     ]
# }

# Feed 형식
# template = {
#         "object_type": "feed",
#         "content": {
#             "title": "DeadLock Detected!",
#             "description": "Deadlock 발생 상세 정보 안내 서비스",
#             "image_url": "https://www.hyundai.co.kr/images/affiliates/others/img-autoever-logo.gif",
#             "image_width": 640,
#             "image_height": 640,
#             "link": {
#             "web_url": "https://www.hyundai.co.kr/",
#             "mobile_web_url": "https://www.hyundai.co.kr/",
#             "android_execution_params": "contentId=100",
#             "ios_execution_params": "contentId=100"
#             }
#         },
#         "social": {
#             "like_count": 100,
#             "comment_count": 200,
#             "shared_count": 300,
#             "view_count": 400,
#             "subscriber_count": 500
#         },
#         "buttons": [
#             {
#             "title": "웹으로 이동",
#             "link": {
#                 "web_url": "http://www.daum.net",
#                 "mobile_web_url": "http://m.daum.net"
#             }
#             },
#             {
#             "title": "앱으로 이동",
#             "link": {
#                 "android_execution_params": "contentId=100",
#                 "ios_execution_params": "contentId=100"
#             }
#             }
#         ]
# }

# template = {
#     "object_type" : "list",
#     "header_title" : "Let's Pratice!",
#     "header_link" : {
#         "web_url" : "www.naver.com",
#         "mobile_web_url" : "www.naver.com"
#     },
#     "contents" : [
#         {
#             "title" : "AAA",
#             "description" : ": MES 시스템",
#             "image_url" : "",
#             "image_width" : 10, "image_height" : 10,
#             "link" : {
#                 "web_url" : "www.hyundai-autoever.com",
#                 "mobile_web_url" : "www.hyundai-autoever.com"
#             }
#         },
#         {
#             "title" : "BBB",
#             "description" : ": 127.0.0.1",
#             "image_url" : "",
#             "image_width" : 50, "image_height" : 50,
#             "link" : {
#                 "web_url" : "www.hyundai-autoever.com",
#                 "mobile_web_url" : "www.hyundai-autoever.com"
#             }
#         },
#         {
#             "title" : "CCC",
#             "description" : ": MES.dbo.TEST",
#             "image_url" : "https://www.hyundai.co.kr/images/affiliates/others/img-autoever-logo.gif",
#             "image_width" : 50, "image_height" : 50,
#             "link" : {
#                 "web_url" : "www.hyundai-autoever.com",
#                 "mobile_web_url" : "www.hyundai-autoever.com"
#             }
#         }
#     ],
#     "buttons" : [
#         {
#             "title" : "웹으로 이동",
#             "link" : {
#                 "web_url" : "www.naver.com",
#                 "mobile_web_url" : "www.naver.com"
#             }
#         }
#     ]
# }



# data = {
#     'receiver_uuids': '["{}"]'.format(friend_id),
#     'template_object' : json.dumps(template)
# }