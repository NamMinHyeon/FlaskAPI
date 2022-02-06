# 사용방법
import schedule
import time
import os, json

#〓〓〓〓〓〓〓〓〓〓〓〓DBMS Config〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓  
import pymssql

BASE_DIR = "./"
secret_file = os.path.join(BASE_DIR, 'secrets.json')

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
 
def job():
    cursor = conn.cursor()
    cursor.callproc('GET_RANDOM_SENTENCE')

    result = [row for row in cursor]

    cursor.close()

    print("I'm working...")
 

# 10초에 한번씩 실행
schedule.every(10).seconds.do(job)
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