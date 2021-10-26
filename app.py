from flask import Flask, request  # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
from Beacon import Beacon

# from "페이지명" import "namespace명"

app = Flask(__name__)   # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
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

api.add_namespace(Beacon, '/Beacon')   #외부 구현 클래스 import 후 특정 경로(Ex. todos)에 등록할 수 있도록 구현

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)