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

# Beacon 등록 API - 2021.10.14
# 비콘아이디 메이저 마이너 아이디 인식되면 몇층인지 입력해서 api버내면 등록하는거로
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
class GetBeacon(Resource):

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


@Beacon.route('/REGISTER_MULTI')
class GetBeacon(Resource):

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

        # Process를 사용하면서 변수를 공유할시 사용 (List 혹은 Dict, Array, Value 등의 변수 공유 가능)
        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        # return_dict = ['1', '2', '3']

        lock = Lock()
        
        task_cb = multiprocessing.Process(target=fnRegister, args=(
                                                                user_name_str
                                                                , user_id_str
                                                                , company_code_str
                                                                , building_code_str
                                                                , return_dict
                                                                , lock
                                                                )
                                          )
        print('11')
        task_cb.start()
        print('22')
        task_cb.join()
        print('33')
        
        # print(task_cb)

        return {
            "RESULT"          : return_dict[0],
            "MESSAGE"         : return_dict[1],
            "MESSAGE_DETAIL"  : return_dict[2]
        }
 
def fnRegister(user_name_str, user_id_str, company_code_str, building_code_str, return_dict, lock):
        
        lock.acquire()

        try:
            cursor = conn.cursor()
            print('1')

            params = (user_name_str, user_id_str, company_code_str, building_code_str)
            print('2')
            cursor.callproc('SET_USER_INFO', params)
            print('3')
            result = [row for row in cursor]
            print('4')
            # cursor 정상적으로 종료 필요
            # Autocommit을 지원하지 않음
            # commit 전에 result에 결과값 맵핑 필수
            # cursor.close()
            conn.commit()
            print('5')

            # 등록 성공
            if result[0][0] == '01' :
                return_dict[0] = result[0][0]
                return_dict[1] = "SUCCESS"
                return_dict[2] = result[0][1]
            # 등록 실패 - 중복
            elif result[0][0] == '99':
                print('6')
                return_dict[0] = result[0][0]
                return_dict[1] = "FAIL"
                return_dict[2] = result[0][1]
            # 등록 실패 - 기타
            else:
                return_dict[0] = result[0][0]
                return_dict[1] = "FAIL"
                return_dict[2] = result[0][1]

        finally:
            lock.release()


@Beacon.route('/COMPANY')
class GetBeacon(Resource):

    def post(self):
        """COMPANY 기준정보 호출"""

        # POST 방식으로 수신
        company_code = request.json.get('company_code')
        # company_code_str = str(company_code)

        cursor = conn.cursor()

        params = (company_code)

        # print(len(params))
        null = ""
        
        if len(params) == 0 :
            cursor.callproc('GET_COMPANY_INFO', null)
        else:
            cursor.callproc('GET_COMPANY_INFO', params)

        result = [row for row in cursor]



        if len(result) == 0 :
            return {
                "Message"         : "Success",
                "RESULT_CNT"      : len(result)
            }
        else:
            return {
                "Message"         : "Success",
                "RESULT_CNT"      : len(result),
                "RESULT"          : result
            }

# beacons = {}

# @Beacon.route('/')
# class ConnectionBasic(Resource):
#     def get(self):
#         """MSSQL 연결 테스트"""

#         cursor = conn.cursor()
#         cursor.execute('SELECT * FROM company_code;')

#         # fetchone, fetchall, fetchmany
#         result = cursor.fetchall()

#         for row in result:
#             print(row, row[0], row[1])
#             # print(result["{0}"].format(i))

#         print(result[0])

        
#         # 연결 끊기
#         # conn.close()

#         # GET 요청시 리턴 값에 해당 하는 dict를 JSON 형태로 반환
#         return {"Message": "Success!"}

# @Beacon.route('/GET_BEACON_INFO/<string:beacon_id>')
# class TEST(Resource):

#     def get(self, beacon_id):
#         """TEST 용도"""

#         beacon_id_str = str(beacon_id)
#         cursor = conn.cursor()
#         params = (beacon_id_str, 'TEMP')
#         cursor.callproc('GET_BEACON_INFO', params)

#         result = [row for row in cursor]

#         if len(result) == 0 :
#             return {
#                 "Message"         : "Success",
#                 "RESULT_CNT"      : len(result)
#             }
#         else:
#             return {
#                 "Message"         : "Success",
#                 "RESULT_CNT"      : len(result),
#                 "RESULT"          : result[0],
#                 "beacon_id"       : result[0][0],
#                 "major_id"        : result[0][1],
#                 "minor_id"        : result[0][2],
#                 "building_code"   : result[0][3],
#                 "floor"           : result[0][4]
#             }


# @Beacon.route('/GET_BEACON_INFO')
# class GetBeacon(Resource):

#     def post(self):
#         """Beacons 마스터에서 Beacon_id와 일치하는 정보 고유값 1 건을 가지고 옵니다."""

#         # POST 방식으로 수신
#         beacon_id = request.json.get('beacon_id')
#         beacon_id_str = str(beacon_id)

#         cursor = conn.cursor()
#         params = (beacon_id_str, 'TEMP')
#         cursor.callproc('GET_BEACON_INFO', params)

#         result = [row for row in cursor]

#         if len(result) == 0 :
#             return {
#                 "Message"         : "Success",
#                 "RESULT_CNT"      : len(result)
#             }
#         else:
#             return {
#                 "Message"         : "Success",
#                 "RESULT_CNT"      : len(result),
#                 "RESULT"          : result[0],
#                 "beacon_id"       : result[0][0],
#                 "major_id"        : result[0][1],
#                 "minor_id"        : result[0][2],
#                 "building_code"   : result[0][3],
#                 "floor"           : result[0][4]
#             }
    
# @Beacon.route('/INSERT_BEACON_HISTORY')
# class PutBeacon(Resource):

#     def post(self):
#         """Beacons 통신 정보를 저장합니다."""

#         # POST 방식으로 수신
#         user_id = request.json.get('user_id')
#         activity_code = request.json.get('activity_code')

#         user_id_str = str(user_id)
#         activity_code_str = str(activity_code)

#         cursor = conn.cursor()

#         params = (user_id_str, activity_code_str)
#         cursor.callproc('INSERT_BEACON_HISTORY', params)

#         # Autocommit을 지원하지 않음
#         conn.commit()

#         return {
#             "Message"         : "Success"
#         }


#SQL 호출 예시
# cursor.execute('SELECT * FROM TEST;')

# 파라미터 셋팅 예시
# params = (1, 'str', pymssql.output(int,0), pymssql.output(str,''))
# respose = cursor.callproc('SP_WHO2', '')
# respose = cursor.callproc('TEST2', '')
# print(respose)  # -631

# # 튜플
# menu = ("돈까스", "치즈까스")
# print(menu[0], menu[1])

# sql = """\
# SET NOCOUNT ON;
# DECLARE @rv int;
# EXEC @rv = dbo.SP_LOCK;
# SELECT @rv;
# """

# sql = """\
# EXEC dbo.SP_LOCK;
# """

# sql = """\
# USE """ + database + """

# SELECT
# 	 p.spid
# 	 , p.blocked
# 	 , RTRIM(p.status) AS STATUS
# 	 , RTRIM(p.program_name) AS PROGRAM_NAME
# 	 , p.waittime
# 	 , RTRIM(p.lastwaittype) AS LASTWAITTYPE
# 	 , p.open_tran
# 	 , RTRIM(p.cmd) AS CMD
# 	 , RTRIM(p.nt_domain) AS NT_DOMAIN
# 	 , RTRIM(p.nt_username) AS NT_USERNAME
# 	 , p.net_address
# 	 , RTRIM(p.loginame) AS LOGINAME
# 	 , dest.text AS 'wait_txt'
# 	 , (
# 		 SELECT TOP 1 event_info
# 		 FROM SYS.sysprocesses AS p2
# 			  CROSS APPLY sys.dm_exec_input_buffer(p2.blocked, p2.request_id)
# 		 WHERE p2.blocked <> p.spid
# 		 ORDER BY p2.login_time ASC
# 	   ) AS 'blocked_txt'
# 	 , lt.name AS 'locked_tbl'
# FROM master.dbo.sysprocesses p
# 	 CROSS APPLY sys.dm_exec_sql_text(p.sql_handle) dest
# 	 LEFT OUTER JOIN (
# 						SELECT CONVERT(SMALLINT, req_spid) AS SPID, rsc_objid, ob.name
# 						FROM master.dbo.syslockinfo li
# 							 LEFT OUTER JOIN sys.objects ob ON li.rsc_objid = ob.object_id
# 						WHERE req_mode = '5' --LOCK 상태만 조회
# 					 ) lt ON p.spid = lt.spid
# WHERE (
# 		p.status LIKE 'run%'
# 		OR p.waittime > 0
# 		OR p.blocked <> 0
# 		OR open_tran <> 0
# 		OR EXISTS (
# 					SELECT *
# 					FROM master.dbo.sysprocesses p1
# 					WHERE p.spid = p1.blocked AND p1.spid <> p1.blocked
# 				  )
# 	  )
# 	  AND p.spid > 50 AND p.spid <> @@spid
# ORDER BY CASE WHEN p.status LIKE 'run%' THEN 0 ELSE 1 END, waittime DESC, open_tran DESC
  
# """

# cursor.execute(sql)
# return_value = cursor.fetchone()[0]
# print(cursor.rowcount)

# for i in range(cursor.rowcount):
#     spid, dbid, ObjId, IndId, Type, Resource, Mode, Status= cursor.fetchone()
#     print(spid, dbid, ObjId, IndId, Type, Resource, Mode, Status)


# print(return_value)  # -631

# # fetchone, fetchall, fetchmany
# result = cursor.fetchall()

# for row in result:
#     print(row, row[0], row[1])
#     # print(result["{0}"].format(i))

# # print(result[0])
# # print(result[1])
# # print(result[2])

# # # 연결 끊기
# conn.close()




# cursor = conn.cursor()
# cursor.execute('SELECT floor, beacon_id FROM beacon_info WHERE beacon_id = %s;', beacon_id_str)

# params = (1, 'str', pymssql.output(int,0), pymssql.output(str,''))

# # fetchone, fetchall, fetchmany
# result = cursor.fetchall()

# for row in result:
#     print(row, row[0], row[1])
#     # print(result["{0}"].format(i))

# print(result[0])

# 연결 끊기
# conn.close()