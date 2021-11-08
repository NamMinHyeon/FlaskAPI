import logging
import datetime
from pytz import timezone

# https://jangseongwoo.github.io/logging/flask_logging/ 참고

# DEBUG > INFO > WARNING > ERROR > Critical
# DEBUG - 상세한 정보
# INFO - 일반적인 정보
# WARNING - 예상치 못하거나 가까운 미래에 발생할 문제
# ERROR - 에러 로그. 심각한 문제
# CRITICAL - 프로그램 자체가 실행되지 않을 수 있음

logging.basicConfig(filename = "logs/beacon.log", level = logging.DEBUG)

def logIn(remote_ip, url, params, message):
    log_date = get_log_date()
    log_message = "{0} / {1} / {2} / {3} / {4}".format(log_date, message, remote_ip, url, str(params))
    logging.info(log_message)

def logOut(response, message):
    log_date = get_log_date()
    log_message = "{0} / {1} / {2} ".format(log_date, message, str(response))
    logging.info(log_message)

def error_log(request, error_code, error_message):
    log_date = get_log_date()
    log_message = "{0} / {1} / {2} / {3}".format(log_date, str(request), error_code, error_message)
    logging.info(log_message)

def get_log_date():
    dt = datetime.datetime.now(timezone("Asia/Seoul"))
    log_date = dt.strftime("%Y%m%d_%H:%M:%S")
    return log_date