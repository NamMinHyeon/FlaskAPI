from app import app  # Flask 의 app Import
# from "페이지명" import "namespace명"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
    # app.run(debug=True, host='52.78.173.135', port=80)