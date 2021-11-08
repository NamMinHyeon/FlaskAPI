from logging import handlers
import logging
import datetime
from pytz import timezone

# DEBUG > INFO > WARNING > ERROR > Critical
# DEBUG - 상세한 정보
# INFO - 일반적인 정보
# WARNING - 예상치 못하거나 가까운 미래에 발생할 문제
# ERROR - 에러 로그. 심각한 문제
# CRITICAL - 프로그램 자체가 실행되지 않을 수 있음

#log settings
# %(asctimes)s : 로그 기록 시간
# %(message)s : 입력 로그

LogFormatter = logging.Formatter('%(message)s')

#handler settings
LogHandler = handlers.TimedRotatingFileHandler(filename='logs/beacon.log', when='midnight', interval=1, encoding='utf-8', utc = 'kst')
LogHandler.setFormatter(LogFormatter)
# Example) beacon.log.20211231
LogHandler.suffix = "%Y%m%d%"

Logger = logging.getLogger()
# 출력 레벨 저장
Logger.setLevel(logging.INFO)
Logger.addHandler(LogHandler)

# logging.basicConfig(filename = "logs/beacon.log", level = logging.DEBUG)

   
def logInput(request, message):
    # request.environ.get('HTTP_X_REAL_IP', request.remote_addr)   
    # request.environ['REMOTE_ADDR']
    # request.remote_addr
    log_date = get_log_date()
    log_message = "{0} ┃ {1} ┃ {2} ┃ {3} ┃ {4}".format(log_date, message,  request.environ.get('HTTP_X_REAL_IP', request.remote_addr),  request.path, str(request.json))    
    Logger.info(log_message)

def logOutput(response, message):
    log_date = get_log_date()
    log_message = "{0} ┃ {1} ┃ {2}".format(log_date, message, str(response))
    Logger.info(log_message)

def error_log(request, error_code, error_message):
    log_date = get_log_date()
    log_message = "{0} ┃ {1} ┃ {2} ┃ {3}".format(log_date, str(request), error_code, error_message)
    Logger.info(log_message)

def get_log_date():
    dt = datetime.datetime.now(timezone("Asia/Seoul"))
    log_date = (dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    return log_date



# def logIn(remote_ip, url, params, message):
#     # log_date = get_log_date()
#     # log_message = "{0} / {1} / {2} / {3} / {4}".format(log_date, message, remote_ip, url, str(params))
#     log_message = "{0} / {1} / {2} / {3} / {4}".format(message, remote_ip, url, str(params)) 
#     Logger.info(log_message)

# def logOut(response, message):
#     log_date = get_log_date()
#     log_message = "{0} / {1} / {2} ".format(log_date, message, str(response))
#     # Logger.info(log_message)