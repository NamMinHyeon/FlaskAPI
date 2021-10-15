from flask import request
from flask_restx import Resource, Api, Namespace
from multiprocessing import Process, Queue, Lock
import multiprocessing

# Flask(Micro Web Framework) : 미니멀리즘
#  → API Server → 스케쥴링을 통한 자원 유연성 확보

#DBMS 연동부
import pymssql

Beacon = Namespace(
    name="Beacon",
    description="Beacon 호출 API",
)

# 1. Local
# server = '192.168.35.100'
# database = 'HSTEP'
# username = 'sa'
# password = 'Qwer!234'

# 2. AWS
server = 'hae.ctgaojyz5tpu.ap-northeast-2.rds.amazonaws.com'
database = 'HSTEPUP'
username = 'sa'
password = 'Qwer!234'

conn =  pymssql.connect(server , username, password, database)


# 1. 사용자 관련 API
# └ LOGIN       : 사용자 로그인
# └ REGISTER    : 사용자 등록
@Beacon.route('/LOGIN')
class GetUser(Resource):

    def post(self):
        """LOGIN 처리 (일반: 01, 최초: 02, 실패: 99)"""

        # POST 방식으로 수신
        user_name = request.json.get('user_name')
        user_id = request.json.get('user_id')

        user_name_str = str(user_name)
        user_id_str = str(user_id)

        cursor = conn.cursor()

        params = (user_name_str, user_id_str)
        cursor.callproc('GET_USER_INFO', params)

        result = [row for row in cursor]

        # 로그인 실패: 99 구현 필요
        if len(result) == 0 :
            return {
                "result"          : "02",
                "message"         : "success"
            }
        else:
            return {
                "result"          : "01",
                "message"         : "success",
                "user_name"       : result[0][0],
                "mail_addr"       : result[0][1],
                "building_code"   : result[0][2],
                "sum_point"       : result[0][3]
            }

@Beacon.route('/REGISTER')
class PutUser(Resource):

    def post(self):
        """회원 가입 (정상 등록: 01, 등록 실패: 99)"""

        # POST 방식으로 수신
        user_name = request.json.get('user_name')
        user_id = request.json.get('user_id')
        company_code = request.json.get('company_code')
        building_code = request.json.get('building_code')

        user_name_str = str(user_name)
        user_id_str = str(user_id)
        company_code_str = str(company_code)
        building_code_str = str(building_code)

        cursor = conn.cursor()

        params = (user_name_str, user_id_str, company_code_str, building_code_str)
        cursor.callproc('SET_USER_INFO', params)

        result = [row for row in cursor]

        # cursor 정상적으로 종료 필요
        # Autocommit을 지원하지 않음
        # commit 전에 result에 결과값 맵핑 필수
        cursor.close()
        conn.commit()

        # 등록 성공
        if result[0][0] == '01' :
            return {
                "result"          : result[0][0],
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 중복
        elif result[0][0] == '99':
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 기타
        else:
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }



# 2. 비콘 관련 API
# └ BEACON-REGISTER   : 비콘 등록
# └ BEACON-SELECT     : 비콘 호출
# └ BEACON-SELECT-ALL : 비콘 호출 전체
# └ BEACON-UPDATE     : 비콘 수정
# └ BEACON-HISTORY    : 비콘 통신 이력 저장
@Beacon.route('/BEACON-REGISTER')
class PutBeacon(Resource):

    def post(self):
        """비콘 등록 (정상 등록: 01, 등록 실패: 99)"""

        # POST 방식으로 수신
        beacon_id = request.json.get('beacon_id')
        major_id = request.json.get('major_id')
        minor_id = request.json.get('minor_id')

        beacon_id_str = str(beacon_id)
        major_id_str = str(major_id)
        minor_id_str = str(minor_id)

        cursor = conn.cursor()

        params = (beacon_id_str, major_id_str, minor_id_str)
        cursor.callproc('SET_BEACON_INFO', params)

        result = [row for row in cursor]

        # cursor 정상적으로 종료 필요
        # Autocommit을 지원하지 않음
        # commit 전에 result에 결과값 맵핑 필수
        cursor.close()
        conn.commit()

        # 등록 성공
        if result[0][0] == '01' :
            return {
                "result"          : result[0][0],
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 중복
        elif result[0][0] == '99':
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 기타
        else:
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str( result[0][1]).lower()
            }

@Beacon.route('/BEACON-SELECT')
class GetBeacon(Resource):

    def post(self):
        """비콘 호출 (1건: 01, 0건: 02, 실패: 99)"""

        # # POST 방식으로 수신
        beacon_id = request.json.get('beacon_id')
        beacon_id_str = str(beacon_id)

        cursor = conn.cursor()

        # Parameter 1개의 경우 아래처럼 셋팅
        params = (beacon_id_str, )
        cursor.callproc('GET_BEACON_INFO', params)

        result = [row for row in cursor]

        cursor.close()

        if  result[0][0] == '01' :
            return {
                "result"          : "01",
                "message"         : "SUCCESS",
                "beacon_id"       : result[0][1],
                "major_id"        : result[0][2],
                "minor_id"        : result[0][3],
                "building_code"   : result[0][4],
                "floor"           : result[0][5]
            }
        elif result[0][0] == '02' :
            return {
                "result"          : "02",
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        else:
            return {
                "result"          : "99",
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }

@Beacon.route('/BEACON-SELECT-ALL')
class GetBeaconAll(Resource):

    def post(self):
        """비콘 전체 호출 (성공: 01, Data 없음: 02, 실패: 99)"""

        # # POST 방식으로 수신
        beacon_id = request.json.get('beacon_id')
        beacon_id_str = str(beacon_id)

        cursor = conn.cursor()

        # Parameter 1개의 경우 아래처럼 셋팅
        params = (beacon_id_str, )
        cursor.callproc('GET_BEACON_INFO_ALL', params)

        result = [row for row in cursor]

        cursor.close()

        if  result[0][0] == '01' :
            return {
                "result"          : "01",
                "message"         : "success",
                "result_data"     : result
            }
        elif result[0][0] == '02' :
            return {
                "result"          : "02",
                "message"         : "success",
                "message_detail"  : str( result[0][1]).lower()
            }
        else:
            return {
                "result"          : "99",
                "message"         : "fail"
            }

@Beacon.route('/BEACON-UPDATE')
class UpdateBeacon(Resource):
    def post(self):
        """비콘 Floor 정보 업데이트 (성공: 01, Data 없음: 02, 실패: 99)"""

        # # POST 방식으로 수신
        beacon_id = request.json.get('beacon_id')
        floor = request.json.get('floor')

        beacon_id_str = str(beacon_id)
        floor_str = str(floor)

        cursor = conn.cursor()

        # Parameter 1개의 경우 아래처럼 셋팅
        params = (beacon_id_str, floor_str)
        cursor.callproc('UPDATE_BEACON_INFO', params)

        result = [row for row in cursor]

        cursor.close()
        conn.commit()

        if  result[0][0] == '01' :
            return {
                "result"          : "01",
                "message"         : "success"
            }
        elif result[0][0] == '02' :
            return {
                "result"          : "02",
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        else:
            return {
                "result"          : "99",
                "message"         : "fail"
            }

@Beacon.route('/BEACON-HISTORY')
class PutBeaconHistory(Resource):

    def post(self):
        """비콘 등록 (정상 등록: 01, 등록 실패: 99)"""

        # POST 방식으로 수신
        beacon_id = request.json.get('beacon_id')
        major_id = request.json.get('major_id')
        minor_id = request.json.get('minor_id')

        beacon_id_str = str(beacon_id)
        major_id_str = str(major_id)
        minor_id_str = str(minor_id)

        cursor = conn.cursor()

        params = (beacon_id_str, major_id_str, minor_id_str)
        cursor.callproc('SET_BEACON_INFO', params)

        result = [row for row in cursor]

        # cursor 정상적으로 종료 필요
        # Autocommit을 지원하지 않음
        # commit 전에 result에 결과값 맵핑 필수
        cursor.close()
        conn.commit()

        # 등록 성공
        if result[0][0] == '01' :
            return {
                "result"          : result[0][0],
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 중복
        elif result[0][0] == '99':
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 기타
        else:
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str( result[0][1]).lower()
            }
