import pickle

from flask import Flask, jsonify, request, make_response
import warnings
from instagramUtils import InstagramUtils as IUtils
import CustomErrors

warnings.filterwarnings('ignore')

app = Flask(__name__)

# 모델 불러오기
with open('saved_model.pkl', 'rb') as file:
    model = pickle.load(file)
util = IUtils()


def extract_text_instagram(user_name: str):
    try:
        text = util.post_by_user(user_name)
    except Exception as e:
        raise e

    print("====================")
    print("text: ", text)

    if len(text) < 1:
        raise RuntimeError("비공개 계정 또는 텍스트가 존재하지 않습니다.")

    return text


def mbti_predict(text: str):
    # 모델을 통한 예측
    predicted_labels = model.predict(text)

    print("predicted label: ", predicted_labels)

    return predicted_labels[0]


@app.route('/instagram', methods=['GET'])
def predict_by_instagram():
    # POST 요청에서 데이터 추출
    sns_url = request.args.get("snsUrl")

    print("sns_url: ", sns_url)

    # url을 통한 크롤링 후 데이터를 기반으로 분류 실행
    try:
        text = extract_text_instagram(sns_url)
        result = mbti_predict(text)
    except CustomErrors.NoPostError as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 400)
        return response
    except CustomErrors.NoAccountError as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 404)
        return response
    except CustomErrors.PrivateAccountError as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 401)
        return response
    except Exception as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 500)
        return response

    response = {
        "mbti": str(result)
    }
    # 결과를 JSON 형식으로 반환
    return jsonify(response)


if __name__ == '__main__':
    app.run()
