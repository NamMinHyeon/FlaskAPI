from xml.etree.ElementTree import XML
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
# └ userUpdate  : 사용자 정보 변경 (이미지값)
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
                "calorie"         : result[0][6],
                "company_code"    : result[0][7],
                "imgString"       : result[0][8]
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
        Base64_profile = request.json.get('imgString')

        user_name_str = str(user_name)
        user_id_str = str(user_id)
        company_code_str = str(company_code)
        building_code_str = str(building_code)
        Base64_profile_str = str(Base64_profile)

        cursor = conn.cursor()

        params = (user_name_str, user_id_str, company_code_str, building_code_str, Base64_profile)
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


@Beacon.route('/userUpdate')
class userUpdate(Resource):

    def post(self):
        """사용자 정보 변경 (정상 : 01, 정보없음 : 02, 실패: 99)"""

        # POST 방식으로 수신
        company_code = request.json.get('company_code')
        user_id = request.json.get('user_id')
        user_name = request.json.get('user_name')
        building_code = request.json.get('building_code')
        mail_addr = request.json.get('mail_addr')
        Base64_profile_Img = request.json.get('Base64_profile_Img')

        company_code_str = str(company_code)
        user_id_str = str(user_id)
        user_name_str = str(user_name)
        building_code_str = str(building_code)
        mail_addr_str = str(mail_addr)
        Base64_profile_Img_str = str(Base64_profile_Img)

        cursor = conn.cursor()

        params = (company_code_str, user_id_str, user_name_str, building_code_str, mail_addr_str, Base64_profile_Img_str)
        cursor.callproc('UPDATE_USER_INFO', params)

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
                "message"         : "success",
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


# 6. USER 관련 API
# └ regUserGoal          : 사용자 목표 입력 API
# └ selectUserGoal       : 사용자 목표 조회 API
@Beacon.route('/regUserGoal')
class regUserGoal(Resource):

    def post(self):
        """사용자 목표 입력 (성공 : 01, 중복 : 02, 실패: 99)"""

        # POST 방식으로 수신
        user_id = request.json.get('user_id')
        vehicle_code = request.json.get('vehicle_code')

        user_id_str = str(user_id)
        vehicle_code_str = str(vehicle_code)

        cursor = conn.cursor()

        params = (user_id_str, vehicle_code_str)
        cursor.callproc('SET_USER_GOAL_INFO', params)

        result = [row for row in cursor]

        # cursor 정상적으로 종료 필요
        # Autocommit을 지원하지 않음
        # commit 전에 result에 결과값 맵핑 필수
        cursor.close()
        conn.commit()

        # 등록 성공
        if result[0][0] == '01' :
            return {
                "result"            : result[0][0],
                "message"           : "success",
                "user_id"           : user_id_str.lower(),
                "vehicle_code"      : vehicle_code_str.lower(),
                "start_dt"          : json.loads(str(result[0][1]).lower())[0]["start_dt"],
                "end_dt"            : json.loads(str(result[0][1]).lower())[0]["end_dt"],
                "cur_step_count"    : json.loads(str(result[0][1]).lower())[0]["cur_step_count"],
                "goal_step_count"   : json.loads(str(result[0][1]).lower())[0]["goal_step_count"],
                "progress_rate"     : json.loads(str(result[0][1]).lower())[0]["progress_rate"],
                "end_yn"            : json.loads(str(result[0][1]).lower())[0]["end_yn"]                
            }
        # 등록 실패 - 중복
        elif result[0][0] == '02':
            return {
                "result"            : result[0][0],
                "message"           : "success",
                "user_id"           : user_id_str.lower(),
                "vehicle_code"      : vehicle_code_str.lower(),
                "start_dt"          : json.loads(str(result[0][1]).lower())[0]["start_dt"],
                "end_dt"            : json.loads(str(result[0][1]).lower())[0]["end_dt"],
                "cur_step_count"    : json.loads(str(result[0][1]).lower())[0]["cur_step_count"],
                "goal_step_count"   : json.loads(str(result[0][1]).lower())[0]["goal_step_count"],
                "progress_rate"     : json.loads(str(result[0][1]).lower())[0]["progress_rate"],
                "end_yn"            : json.loads(str(result[0][1]).lower())[0]["end_yn"]   
            }
        # 등록 실패 - 기타
        elif result[0][0] == '99':
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 중복
        else:
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }


@Beacon.route('/selectUserGoal')
class selectUserGoal(Resource):

    def post(self):
        """사용자 목표 조회 (성공 : 01, 없음 : 02, 실패: 99)"""

        # POST 방식으로 수신
        user_id = request.json.get('user_id')
        vehicle_code = request.json.get('vehicle_code')

        user_id_str = str(user_id)
        vehicle_code_str = str(vehicle_code)

        cursor = conn.cursor()

        params = (user_id_str, vehicle_code_str)
        cursor.callproc('GET_USER_GOAL_INFO', params)

        result = [row for row in cursor]

        # cursor 정상적으로 종료 필요
        # Autocommit을 지원하지 않음
        # commit 전에 result에 결과값 맵핑 필수
        cursor.close()
        conn.commit()

        # 등록 성공
        if result[0][0] == '01' :
            return {
                "result"            : result[0][0],
                "message"           : "success",
                "user_id"           : user_id_str.lower(),
                "vehicle_code"      : vehicle_code_str.lower(),
                "start_dt"          : json.loads(str(result[0][1]).lower())[0]["start_dt"],
                "end_dt"            : json.loads(str(result[0][1]).lower())[0]["end_dt"],
                "cur_step_count"    : json.loads(str(result[0][1]).lower())[0]["cur_step_count"],
                "goal_step_count"   : json.loads(str(result[0][1]).lower())[0]["goal_step_count"],
                "progress_rate"     : json.loads(str(result[0][1]).lower())[0]["progress_rate"],
                "end_yn"            : json.loads(str(result[0][1]).lower())[0]["end_yn"]   
            }
        # 등록 실패 - 기타
        elif result[0][0] == '99':
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 조회 실패 - 없음
        else:
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str( result[0][1]).lower()
            }




# 7. GARAGE(차고) 관련 API
# └ regGarage           : 사용자 차고 입력 API
# └ selectGarage        : 사용자 차고 조회 API
@Beacon.route('/regGarage')
class regGarage(Resource):

    def post(self):
        """사용자 차고 입력 (성공 : 01, 중복 : 02, 실패: 99)"""

        # POST 방식으로 수신
        user_id = request.json.get('user_id')
        object_code = request.json.get('object_code')
        x_delta = request.json.get('x_delta')
        y_delta = request.json.get('y_delta')

        user_id_str = str(user_id)
        object_code_str = str(object_code)
        x_delta_str = str(x_delta)
        y_delta_str = str(y_delta)

        cursor = conn.cursor()

        params = (user_id_str, object_code_str, x_delta_str, y_delta_str)
        cursor.callproc('SET_USER_GARAGE_INFO', params)

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
        # 등록 실패 - 기타
        elif result[0][0] == '99':
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 중복
        else:
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str( result[0][1]).lower()
            }


@Beacon.route('/garageSelect')
class garageSelect(Resource):

    def post(self):
        """사용자 차고 입력 (성공 : 01, 없음 : 02, 실패: 99)"""

        # POST 방식으로 수신
        user_id = request.json.get('user_id')

        user_id_str = str(user_id)

        cursor = conn.cursor()

        params = (user_id_str, )
        cursor.callproc('GET_USER_GARAGE_INFO', params)

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
        # 등록 실패 - 기타
        elif result[0][0] == '99':
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 등록 실패 - 중복
        else:
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str( result[0][1]).lower()
            }

# 8. 건물(Building) 관련 API
# └ buildingSelect      : 건물 정보 조회
# └ buildingSelectAll      : 건물 정보 조회
@Beacon.route('/buildingSelect')
class buildingSelect(Resource):

    def post(self):
        """건물 호출 (성공 : 01, 없음 : 02, 실패: 99)"""

        # POST 방식으로 수신
        building_code = request.json.get('building_code')

        building_code_str = str(building_code)

        cursor = conn.cursor()

        params = (building_code_str, )
        cursor.callproc('GET_BUILDING_INFO', params)

        result = [row for row in cursor]

        # cursor 정상적으로 종료 필요
        # Autocommit을 지원하지 않음
        # commit 전에 result에 결과값 맵핑 필수
        cursor.close()
        conn.commit()

        result_array = result[0][1].split('|')

        # 성공
        if result[0][0] == '01' :
            return {
                "result"          : result[0][0],
                "message"         : "success",
                "building_code"   : building_code_str.lower(),
                # "result_data"     : json.loads(str(result[0][1]).lower())
                # 구분자 분리 및 배열 처리
                "result_data"     : result_array
            }
        # 실패 - 기타
        elif result[0][0] == '99':
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str(result[0][1]).lower()
            }
        # 조회 실패 - 없음
        else:
            return {
                "result"          : result[0][0],
                "message"         : "fail",
                "message_detail"  : str( result[0][1]).lower()
            }



@Beacon.route('/buildingSelectAll')
class buildingSelectAll(Resource):

    def post(self):
        """건물 전체 호출 (성공: 01, Data 없음: 02, 실패: 99)"""

        # POST 방식 및 요청값 없음
        cursor = conn.cursor()
        cursor.callproc('GET_BUILDING_INFO_ALL')

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


# 〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓
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

# 〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓
# 100. SEC API
# └ GGPI        : GGPI SEC 정보 수집 
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
import cfscrape
import cloudscraper


@Beacon.route('/GGPI/<flag>')
class GGPI(Resource):
    def get(self, flag):
        print("0")
        def crawling():
            print("00")
            #〓〓〓〓〓〓〓〓〓〓〓〓Target Config〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓
            scraper = cfscrape.create_scraper()
            url = 'https://www.sec.gov/Archives/edgar/data/0001847127'
            response = scraper.get(url)
            #〓〓〓〓〓〓〓〓〓〓〓〓Target Config〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓
            print("1")
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                # title = soup.select_one('#s_content > div.section > ul > li:nth-child(1) > dl > dt > a')
                # title = soup.select_one('#main-content > table > tbody > tr:nth-child(2) > td:nth-child(1) > a')
                title = soup.select_one('#main-content > table > tr > tr > td > a').text
                
                SEC_STR = str('0001847127')
                SEC_SUB_STR = str(title)
                print("2")
                cursor = conn_BOT.cursor()
                print("3")
                params = (SEC_STR, SEC_SUB_STR)
                cursor.callproc('SET_SEC_INFO', params)
    
                # result = [row for row in cursor]

                # cursor 정상적으로 종료 필요
                # Autocommit을 지원하지 않음
                # commit 전에 result에 결과값 맵핑 필수
                cursor.close()
                conn_BOT.commit()
            
            else : 
                print(response.status_code)

        sched = BackgroundScheduler(daemon=True) 

        sched.start()

        if flag == '1':
            sched.add_job(crawling, 'interval', seconds=2, id="SEC_1")
            # sched.remove_job("SEC_1")
            
            return "Job Activated!"

        elif flag == '2':
            sched.remove_all_jobs()
            sched.shutdown()
            
            return "Job Removed!"




@Beacon.route('/GGPI_2/<flag>')
class GGPI(Resource):
    def get(self, flag):
        print("0")




        def crawling():
            print("00")
            #〓〓〓〓〓〓〓〓〓〓〓〓Target Config〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓
            scraper = cloudscraper.create_scraper()
            # scraper = cfscrape.create_scraper()
            url = 'https://www.sec.gov/Archives/edgar/data/0001847127'

            headers = {'User-Agent': 'Mozilla/5.0'}
            response = scraper.get(url, headers=headers)
            #〓〓〓〓〓〓〓〓〓〓〓〓Target Config〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓
            print("1")


            cursor = conn_BOT.cursor()
            params = (response.status_code, '1')
            cursor.callproc('SET_SEC_INFO', params)


            cursor.close()
            conn_BOT.commit()


        sched = BackgroundScheduler(daemon=True) 

        sched.start()

        if flag == '1':
            sched.add_job(crawling, 'interval', seconds=2, id="SEC_1")
            # sched.remove_job("SEC_1")
            
            return "Job Activated!"

        elif flag == '2':
            sched.remove_all_jobs()
            sched.shutdown()
            
            return "Job Removed!"