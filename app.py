import pickle

from flask import Flask, jsonify, request, make_response
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
    # text = util.post_by_user(url)
    text = util.post_by_user(url)

    print("====================")
    print("text: ", text)

    if len(text)<1:
        raise RuntimeError("비공개 계정 또는 텍스트가 존재하지 않습니다.")

    # 모델을 통한 예측
    predicted_labels = model.predict(text)

    print("predicted label: ", predicted_labels)

    return predicted_labels[0]


@app.route('/instagram', methods=['GET'])
def predict():
    # POST 요청에서 데이터 추출
    sns_url = request.args.get("snsUrl")

    print("sns_url: ",sns_url)

    # url을 통한 크롤링 후 데이터를 기반으로 분류 실행
    try:
        result = run_algorithm(sns_url)
    except RuntimeError as e:
        message = e.args
        response = make_response(message, 400)
        return response
    except Exception as e:
        print(e.args)
        message = "크롤링 중 오류가 발생했습니다."
        response = make_response(message, 500)
        return response

    response = {
        "mbti": str(result)
    }
    # 결과를 JSON 형식으로 반환
    return jsonify(response)


if __name__ == '__main__':
    app.run()
