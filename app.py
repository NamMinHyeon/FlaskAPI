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

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
api.add_namespace(Beacon, '/Beacon')   #외부 구현 클래스 import 후 특정 경로(Ex. todos)에 등록할 수 있도록 구현

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# 비콘 테이블 모델 정의 : 테이블명 동일하게
class beacon_info(db.Model):
    # 수정을 위해 SEQ (고유값) 추가하여 키값으로 활용하기
    seq = db.Column(db.String(100), primary_key=True)
    beacon_id = db.Column(db.String(100), nullable=False)
    major_id = db.Column(db.String(255), nullable=False)
    minor_id = db.Column(db.String(255), nullable=False)
    building_code = db.Column(db.String(255), nullable=False)
    floor = db.Column(db.Integer(), nullable=False)


class season_code(db.Model):
    # 수정을 위해 SEQ (고유값) 추가하여 키값으로 활용하기
    seq = db.Column(db.Integer(), primary_key=True)
    season_code = db.Column(db.String(100), nullable=False)
    season_name = db.Column(db.String(255), nullable=False)
    start_dt = db.Column(db.String(100), nullable=False)
    end_dt = db.Column(db.String(100), nullable=False)
    active_yn = db.Column(db.String(1), nullable=False)




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
    # column_display_pk = True
    column_editable_list = ('season_code', 'season_name', 'start_dt', 'end_dt', 'active_yn')
    column_searchable_list = column_editable_list
    column_export_list  = column_editable_list
    # column_filters = column_editable_list
    # column_display_actions = True


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
admin.add_view(BeaconView(beacon_info, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Beacons"))
admin.add_view(SeasonView(season_code, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Seasons"))

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

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)