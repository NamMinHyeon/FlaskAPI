from flask import request, render_template
from flask_restx import Resource, Api, Namespace
from multiprocessing import Process, Queue, Lock
import multiprocessing
import os, json

# Flask(Micro Web Framework) : 미니멀리즘
#  → API Server → 스케쥴링을 통한 자원 유연성 확보

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
db_name = get_secret("DB_NAME") #HSTEPUP
db_name_SUB = get_secret("DB_NAME_SUB") #BOT
 
conn =  pymssql.connect(db_host , db_user, db_pass, db_name)
conn_BOT =  pymssql.connect(db_host , db_user, db_pass, db_name_SUB)
#〓〓〓〓〓〓〓〓〓〓〓〓DBMS Config〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓


Beacon = Namespace(
    name="Beacon",
    description="Beacon 호출 API",
)

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# @Beacon.before_first_request
# def before_first_request():
#     print("flask 실행 후 첫 요청 때만 실행")
#     # 즉 프린트문을 통해 어느 시점에서 첫요청이 일어나는지 확인
 
 
# @Beacon.before_request
# def before_request():
#     print("HTTP 요청이 들어올 때마다 실행")
#     # 즉 프린트문을 통해 어느 시점에서 첫요청이 일어나는지 확인 
#     # 라우팅 코드 직전에 실행
 
 
# @Beacon.after_request
# def after_request(response):
#     print("HTTP 요청 처리가 끝나고 브라우저에 응답하기 전에 실행")
#     return response
#     # 해당 요청이 발생하면 프린트문으로 확인하고, 응답 또한 보내줌.
#     # 라우팅 코드 직후에


# 1. 사용자 관련 API
# └ login       : 사용자 로그인
# └ register    : 사용자 등록
@Beacon.route('/login')
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
                "user_name"       : user_name_str,
                "user_id"         : user_id_str,
                "result"          : "02",
                "message"         : "success"
            }
        else:
            return {
                "user_name"       : user_name_str,
                "user_id"         : user_id_str,
                "result"          : "01",
                "message"         : "success",
                "user_name"       : result[0][0],
                "mail_addr"       : result[0][1],
                "building_code"   : result[0][2],
                "sum_point"       : result[0][3],
                "floor_up"        : result[0][4],
                "floor_down"      : result[0][5],
                "calorie"         : result[0][6]
            }

@Beacon.route('/register')
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
                "user_name"       : user_name_str,
                "user_id"         : user_id_str,
                "company_code"    : company_code_str,
                "building_code"   : building_code_str,
                "result"          : result[0][0],
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 중복
        elif result[0][0] == '99':
            return {
                "user_name"       : user_name_str,
                "user_id"         : user_id_str,
                "company_code"    : company_code_str,
                "building_code"   : building_code_str,
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 기타
        else:
            return {
                "user_name"       : user_name_str,
                "user_id"         : user_id_str,
                "company_code"    : company_code_str,
                "building_code"   : building_code_str,
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }



# 2. 비콘 관련 API
# └ beaconRegister   : 비콘 등록
# └ beaconSelect     : 비콘 정보 호출 (층수)
# └ beaconSelectAll  : 비콘 호출 전체
# └ beaconUpdate     : 비콘 '층' 정보 수정
# └ beaconCall       : 비콘 통신 이력 저장
@Beacon.route('/beaconRegister')
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

@Beacon.route('/beaconSelect')
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

@Beacon.route('/beaconSelectAll')
class GetBeaconAll(Resource):

    def post(self):
        """비콘 전체 호출 (성공: 01, Data 없음: 02, 실패: 99)"""

        # POST 방식 및 요청값 없음
        cursor = conn.cursor()
        cursor.callproc('GET_BEACON_INFO_ALL')

        result = [row for row in cursor]

        cursor.close()

        if  result[0][0] == '01' :
            return {
                "result"          : "01",
                "message"         : "success",
                "result_data"     : json.loads(str(result[0][1]).lower())
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

@Beacon.route('/beaconUpdate')
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

@Beacon.route('/beaconCall')
class PutBeaconHistory(Resource):

    def post(self): 
        """비콘 통신 이력 등록 (정상 등록: 01, 등록 실패: 99)"""

        # POST 방식으로 수신
        user_id = request.json.get('user_id')
        beacon_id = request.json.get('beacon_id')
        distance = request.json.get('distance')

        # DB단에서 구현
        # activity_code = request.json.get('activity_code')
        # point_code = request.json.get('point_code')
        # building_code = request.json.get('building_code')

        user_id_str = str(user_id)
        beacon_id_str = str(beacon_id)
        distance_str = str(distance)
        
        # DB단에서 구현
        # activity_code_str = str(activity_code)
        # point_code_str = str(point_code)
        # building_code_str = str(building_code)

        cursor = conn.cursor()

        params = (user_id_str, beacon_id_str, distance_str)
        cursor.callproc('SET_BEACON_HISTORY_INFO', params)

        result = [row for row in cursor]

        cursor.close()
        conn.commit()

        # 등록 성공
        if result[0][0] == '01' :
            return {
                "user_id"         : user_id_str,
                "beacon_id"       : beacon_id_str,
                "distance"        : distance_str,
                "result"          : result[0][0],
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower(),
                "max_floor"       : str(result[0][2]).lower(),
                "sum_point"       : str(result[0][3]).lower(),
                "activity_code"   : str(result[0][4]).lower()}
        # 등록 실패 - 기타
        else:
            return {
                "user_id"         : user_id_str,
                "beacon_id"       : beacon_id_str,
                "distance"        : distance_str,
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }


# 3. 포인트 관련 API
# └ pointSelect     : 포인트 조회
# └ pointSeasonRank : 포인트 시즌 랭킹 조회
# └ pointEnd        : 포인트 마감 처리
@Beacon.route('/pointSelect')
class GetPoint(Resource):

    def post(self):
        """포인트 조회 (성공: 01, Data 없음: 02, 실패: 99)"""

        # POST 방식으로 수신
        user_id = request.json.get('user_id')
        season_cd = request.json.get('season_cd')

        user_id_str = str(user_id)
        season_cd_str = str(season_cd)

        cursor = conn.cursor()

        params = (user_id_str, season_cd_str) 
        cursor.callproc('GET_POINT_INFO', params)

        result = [row for row in cursor]


        cursor.close()

        if  result[0][0] == '01' :
            return {
                "user_id"         : user_id_str,
                "season_cd"       : season_cd_str,
                "season_name"     : str(result[0][2]).lower(),
                "result"          : "01",
                "message"         : "SUCCESS",
                "result_data"     : json.loads(str(result[0][1]).lower())
            }
        elif result[0][0] == '02' :
            return {
                "user_id"         : user_id_str,
                "season_cd"       : season_cd_str,
                "season_name"     : str(result[0][2]).lower(),
                "result"          : "02",
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        else:
            return {
                "user_id"         : user_id_str,
                "season_cd"       : season_cd_str,
                "season_name"     : str(result[0][2]).lower(),
                "result"          : "99",
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }

@Beacon.route('/pointSeasonRank')
class GetPointRank(Resource):
    
    def post(self):
        """포인트 시즌 랭킹 조회 (성공: 01, Data 없음: 02, 실패: 99)"""

        # POST 방식으로 수신
        season_cd = request.json.get('season_cd')

        season_cd_str = str(season_cd)

        cursor = conn.cursor()

        params = (season_cd_str, )
        cursor.callproc('GET_POINT_SEASON_RANK', params)

        result = [row for row in cursor]

        cursor.close()

        if  result[0][0] == '01' :
            return {
                "season_cd"       : season_cd_str,
                "result"          : "01",
                "message"         : "SUCCESS",
                "result_data"     : json.loads(str(result[0][1]).lower())
            }
        elif result[0][0] == '02' :
            return {
                "season_cd"       : season_cd_str,
                "result"          : "02",
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        else:
            return {
                "season_cd"       : season_cd_str,
                "result"          : "99",
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }

@Beacon.route('/pointEnd') 
class SetPointEnd(Resource):

    def post(self):
        """포인트 마감 처리 (성공: 01, Data 없음: 02, 실패: 99)"""

        # POST 방식으로 수신
        user_id = request.json.get('user_id')
        beacon_id = request.json.get('beacon_id')

        user_id_str = str(user_id)
        beacon_id_str = str(beacon_id)

        cursor = conn.cursor()

        params = (user_id_str, beacon_id_str) 
        cursor.callproc('SET_POINT_END', params)

        result = [row for row in cursor]

        # cursor 정상적으로 종료 필요
        # Autocommit을 지원하지 않음
        # commit 전에 result에 결과값 맵핑 필수
        cursor.close()
        conn.commit()

        if  result[0][0] == '01' :
            return {
                "user_id"         : user_id_str,
                "beacon_id"       : beacon_id_str,
                "result"          : "01",
                "message"         : "SUCCESS",
                "min_tm"          : str(result[0][1]).lower(),
                "max_tm"          : str(result[0][2]).lower(),
                "floor_start"     : str(result[0][3]).lower(),
                "floor_end"       : str(result[0][4]).lower(),
                "avg_tm"          : str(result[0][5]).lower(),
                "sum_point"       : str(result[0][6]).lower(),
                "calorie"         : str(result[0][7]).lower(),
                "activity_tm"     : str(result[0][8]).lower(),
                "floor_diff_sum"  : str(result[0][9]).lower()
            }
        elif result[0][0] == '02' :
            return {
                "user_id"         : user_id_str,
                "beacon_id"       : beacon_id_str,
                "result"          : "02",
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        else:
            return {
                "user_id"         : user_id_str,
                "beacon_id"       : beacon_id_str,
                "result"          : "99",
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }


# 4. 활동(Activity) 관련 API
# └ activitySelect      : 활동이력 조회
# └ activitySelect2     : 활동이력 조회 2 (미완료)
@Beacon.route('/activitySelect')
class GetActivity(Resource):
    
    def post(self):
        """활동 이력 조회 (성공: 01, Data 없음: 02, 실패: 99)"""

        # POST 방식으로 수신
        user_id = request.json.get('user_id')
        type = request.json.get('type')
        season_cd = request.json.get('season_cd')

        user_id_str = str(user_id)
        type_str = str(type)
        season_cd_str = str(season_cd)

        cursor = conn.cursor()

        params = (user_id_str, type_str, season_cd_str)
        cursor.callproc('GET_USER_ACTIVITY_SEASON', params)

        result = [row for row in cursor]

        cursor.close()

        if  result[0][0] == '01' :
            return {
                "user_id"         : user_id_str,
                "type"            : type_str,
                "season_cd"       : season_cd_str,
                "result"          : "01",
                "message"         : "SUCCESS",
                "result_data"     : json.loads(str(result[0][1]).lower())
            }
        # elif result[0][0] == '02' :
        #     return {
        #         "user_id"         : user_id_str,
        #         "type"            : type_str,
        #         "season_cd"       : season_cd_str,
        #         "result"          : "02",
        #         "message"         : "success",
        #         "message_detail"  : str(result[0][1]).lower()
        #     }
        else:
            return {
                "user_id"         : user_id_str,
                "type"            : type_str,
                "season_cd"       : season_cd_str,
                "result"          : "99",
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }

@Beacon.route('/activitySelect2')
class GetActivity2(Resource):

    def post(self):
        """활동 이력 조회 (성공: 01, Data 없음: 02, 실패: 99)"""

        # POST 방식으로 수신
        user_id = request.json.get('user_id')
        season_cd = request.json.get('season_cd')

        user_id_str = str(user_id)
        season_cd_str = str(season_cd)

        cursor = conn.cursor()

        params = (user_id, season_cd)
        cursor.callproc('GET_USER_ACTIVITY_SEASON_2', params)

        result = [row for row in cursor]

        cursor.close()

        if  result[0][0] == '01' :
            return {
                "user_id"         : user_id_str,
                "season_cd"       : season_cd_str,
                "result"          : "01",
                "message"         : "SUCCESS",
                "season_code"     : str(result[0][1]).lower(),
                "result_data"     : json.loads(str(result[0][2]).lower())
            }
        elif result[0][0] == '02' :
            return {
                "user_id"         : user_id_str,
                "season_cd"       : season_cd_str,
                "result"          : "02",
                "message"         : "success",
                "message_detail"  : str(result[0][1]).lower()
            }
        else:
            return {
                "user_id"         : user_id_str,
                "season_cd"       : season_cd_str,
                "result"          : "99",
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }


# 5. 시즌(Season) 관련 API
# └ seasonSelect      : 시즌 정보 조회
@Beacon.route('/seasonSelect')
class GetSeason(Resource):

    def post(self):
        """시즌 전체 호출 (성공: 01, Data 없음: 02, 실패: 99)"""

        # POST 방식 및 요청값 없음
        cursor = conn.cursor()
        cursor.callproc('GET_SEASON_INFO_ALL')

        result = [row for row in cursor]

        cursor.close()

        if  result[0][0] == '01' :
            return {
                "result"          : "01",
                "message"         : "success",
                "result_data"     : json.loads(str(result[0][1]).lower())
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


# 99. BOT API
# └ answerCall  : 정답 호출 - 미사용 (HTML 표현 불가로 app.py로 이관 - 2022.02.05)
@Beacon.route('/answerCall/<seq_sub>')
class GetAnswer(Resource):

    def get(self, seq_sub):
        """정답 호출"""
        # http://localhost/Beacon/answerCall/5

        #BOT 스키마에 연결
        cursor = conn_BOT.cursor()

        params = (seq_sub)
        cursor.callproc('GET_CORRECT_ANSWER', params)

        result = [row for row in cursor]

        cursor.close()

        return result[0][0]
        # return render_template('answerCorrect.html', answer=result[0][0])
        # return '<HTML>TEST</HTML>'
