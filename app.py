from flask import Flask, request, url_for, redirect, render_template, request, abort  # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import

import os
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user

from flask_security.utils import encode_string, encrypt_password

import flask_admin

from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, expose
from wtforms import PasswordField

# # log.py 참조
# import log 

# 디버깅 모드 (중단점)
# import pdb

from Beacon import Beacon
# from "페이지명" import "namespace명"

# Local : C:\Python\Lib\site-packages\sqlalchemy\orm\session.py 부분 재정의 필요 > 배포 필요
# Oper : /usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/session.py - vi 에디터로 수정 필요
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Create Flask application
# Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
app = Flask(__name__)

app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


# api = Api(app)          # Flask 객체에 Api 객체 등록
api = Api(
    app,
    version='2021.10.14',
    title="Beacon's API Server",
    description="Beacon's API Server!",
    terms_url="/",
    contact="mh.nam@hyundai-autoever.com",
    license="HAE"
)

#〓〓〓〓〓〓〓〓〓〓〓〓DBMS Config〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓  
import pymssql
import json

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

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
api.add_namespace(Beacon, '/Beacon')   #외부 구현 클래스 import 후 특정 경로(Ex. todos)에 등록할 수 있도록 구현

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# 비콘 테이블 모델 정의 : 테이블명 동일하게
# 수정을 위해 SEQ (고유값) 일괄 추가 및 Unique값으로 활용하기
class beacon_info(db.Model):
    seq = db.Column(db.String(100), primary_key=True)
    beacon_id = db.Column(db.String(100), nullable=False)
    major_id = db.Column(db.String(255), nullable=False)
    minor_id = db.Column(db.String(255), nullable=False)
    building_code = db.Column(db.String(255), nullable=False)
    floor = db.Column(db.Integer(), nullable=False)

class season_code(db.Model):
    seq = db.Column(db.Integer(), primary_key=True)
    season_code = db.Column(db.String(100), nullable=False)
    season_name = db.Column(db.String(255), nullable=False)
    start_dt = db.Column(db.String(100), nullable=False)
    end_dt = db.Column(db.String(100), nullable=False)
    active_yn = db.Column(db.String(1), nullable=False)

class building_code(db.Model):
    seq = db.Column(db.Integer(), primary_key=True)
    building_code = db.Column(db.String(100), nullable=False)
    building_name = db.Column(db.String(255), nullable=False)

class company_code(db.Model):
    seq = db.Column(db.Integer(), primary_key=True)
    company_code = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)

class point_code(db.Model):
    seq = db.Column(db.Integer(), primary_key=True)
    point_code = db.Column(db.String(100), nullable=False)
    point_name = db.Column(db.String(255), nullable=False)

class user_info(db.Model):
    seq = db.Column(db.Integer(), primary_key=True)
    company_code = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    building_code = db.Column(db.String(100), nullable=False)
    mail_addr = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    crtn_dt = db.Column(db.String(100))
    mody_dt = db.Column(db.String(100))


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


    # can_edit = True
    edit_modal = True
    create_modal = True    
    can_export = True
    can_view_details = True
    details_modal = True

class UserView(MyModelView):
    column_editable_list = ['email', 'first_name', 'last_name']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    #form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    form_overrides = {
        'password': PasswordField
    }

# 비콘 뷰 템플릿
class BeaconView(MyModelView):
    # column_display_pk = True
    column_editable_list = ('beacon_id', 'major_id', 'minor_id', 'building_code', 'floor')
    column_searchable_list = column_editable_list
    column_export_list  = column_editable_list
    # column_filters = column_editable_list
    # column_display_actions = True

class SeasonView(MyModelView):
    column_editable_list = ('season_code', 'season_name', 'start_dt', 'end_dt', 'active_yn')
    column_searchable_list = column_editable_list
    column_export_list  = column_editable_list

class BuildingView(MyModelView):
    column_editable_list = ('building_code', 'building_name')
    column_searchable_list = column_editable_list
    column_export_list  = column_editable_list
    
class CompanyView(MyModelView):
    column_editable_list = ('company_code', 'company_name')
    column_searchable_list = column_editable_list
    column_export_list  = column_editable_list

class PointView(MyModelView):
    column_editable_list = ('point_code', 'point_name')
    column_searchable_list = column_editable_list
    column_export_list  = column_editable_list

class UserView(MyModelView):
    column_editable_list = ('company_code', 'user_id', 'user_name', 'building_code', 'mail_addr', 'password')
    column_searchable_list = ('company_code', 'user_id', 'user_name', 'building_code', 'mail_addr', 'password', 'crtn_dt', 'mody_dt')
    column_export_list  = ('company_code', 'user_id', 'user_name', 'building_code', 'mail_addr', 'password', 'crtn_dt', 'mody_dt')



class CustomView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/custom_index.html')


# Flask views
@app.route('/')
def index():
    return render_template('index.html')

# Create admin
admin = flask_admin.Admin(
    app,
    'Beacon''s Admin Dashboard',
    base_template='my_master.html',
    template_mode='bootstrap4',
)

# Add model views
# admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
# admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
# admin.add_view(CustomView(name="Custom view", endpoint='custom', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))

# 비콘 관련 모델 뷰 정의
# admin.add_view("모델 뷰 명칭"("모델 뷰", db.session, ))
admin.add_view(BeaconView(beacon_info, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Beacons"))
admin.add_view(SeasonView(season_code, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Seasons"))
admin.add_view(BuildingView(building_code, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Buildings"))
admin.add_view(CompanyView(company_code, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Companys"))
admin.add_view(PointView(point_code, db.session, menu_icon_type='fa', menu_icon_value='fa-connectdevelop', name="Points"))
admin.add_view(UserView(user_info, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

# @app.errorhandler(404)
# def page_not_found(error):
#     app.logger.error('Page_not_found Access')
#     return "There is no web page. Please enter the URL correctly.", 404
 
# @app.before_first_request
# def before_first_request():
#     print("Flask API Open")
#     # 즉 프린트문을 통해 어느 시점에서 첫요청이 일어나는지 확인
 
 
# @app.before_request
# def before_request():
#     # print("HTTP 요청이 들어올 때마다 실행")
#     # 라우팅 코드 직전에 실행
#     log.logInput(request, "BEFORE")
 
 
# @app.after_request
# def after_request(response):
#     # print("HTTP 요청 처리가 끝나고 브라우저에 응답하기 전에 실행")
#     # 해당 요청이 발생하면 프린트문으로 확인하고, 응답 또한 보내줌.
#     # 라우팅 코드 직후에
#     log.logOutput(response, "└ AFTER")
#     return response

# 99. BOT API
# └ randomCall      : 리스트 호출 (HTML 사용)
# └ randomCallJson  : 리스트 호출 (Vue3) 사용)
# └ checkResult     : 오답 정리   (HTML 사용)
@app.route('/randomCall')
def randomCall():
    """정답 호출"""
    # http://localhost/randomCall

    #BOT 스키마에 연결
    cursor = conn_BOT.cursor()

    cursor.callproc('GET_RANDOM_SENTENCE_NEW')

    result = [row for row in cursor]

    cursor.close()

    return render_template('randomSentence.html'
                            , random_0 = result[0][0],  answer_0 = result[0][1]
                            , random_1 = result[1][0],  answer_1 = result[1][1]
                            , random_2 = result[2][0],  answer_2 = result[2][1]
                            , random_3 = result[3][0],  answer_3 = result[3][1]
                            , random_4 = result[4][0],  answer_4 = result[4][1]
                          )

@app.route('/front/randomCallJson')
def randomCallJson():
    """정답 호출"""
    # http://localhost/randomCallJson

    #BOT 스키마에 연결
    cursor = conn_BOT.cursor()

    cursor.callproc('GET_RANDOM_SENTENCE_NEW_2')

    result = [row for row in cursor]

    cursor.close()

    return {    
        "result_data"   : json.loads(str(result[0][1]))
    }

@app.route('/front/checkResult', methods=['POST']) 
def checkResult():
    """오답 정리"""
    # http://localhost/checkResult

    # POST 방식으로 수신
    seq_sub = request.json.get('SEQ_SUB')

    seq_sub_str = str(seq_sub)

    #BOT 스키마에 연결
    cursor = conn_BOT.cursor()

    params = (seq_sub_str, )

    cursor.callproc('SET_SEQ_SUB', params)

    result = [row for row in cursor]

    # cursor 정상적으로 종료 필요
    # Autocommit을 지원하지 않음
    # commit 전에 result에 결과값 맵핑 필수
    cursor.close()
    conn_BOT.commit()

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
    
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    
    # app.logger.info("test") 
    # app.logger.debug("debug test") 
    # app.logger.error("error test")

    app.run(debug=True, host='0.0.0.0', port=80)