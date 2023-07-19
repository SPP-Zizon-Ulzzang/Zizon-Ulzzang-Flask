import pickle

from flask import Flask, jsonify, request
import warnings
from instagramUtils import InstagramUtils as IUtils
import instagram_crawl as crawler
warnings.filterwarnings('ignore')

app = Flask(__name__)

# 모델 불러오기
with open('saved_model.pkl', 'rb') as file:
    model = pickle.load(file)
util = IUtils()


def run_algorithm(url):
    print(url)

    text = util.post_by_user(url)

    # 모델을 통한 예측
    predicted_labels = model.predict(text)

    print("predicted label: ", predicted_labels)

    return predicted_labels[0]


@app.route('/instagram', methods=['GET'])
def predict():
    # POST 요청에서 데이터 추출
    snsUrl = request.args.get("snsUrl")

    # url을 통한 크롤링 후 데이터를 기반으로 분류 실행
    # try:
    result = run_algorithm(snsUrl)
    # except Exception as ex:
    #     print(ex)
    #     response = {
    #         "mbti": "error"
    #     }
    #     return jsonify(response)

    response = {
        "mbti": str(result)
    }
    # 결과를 JSON 형식으로 반환
    return jsonify(response)


if __name__ == '__main__':
    app.run()
