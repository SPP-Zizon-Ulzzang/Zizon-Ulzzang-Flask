import logging
import pickle

import numpy as np
from flask import Flask, jsonify, request, make_response
import warnings

from sklearn.preprocessing import LabelEncoder

from instagramUtils import InstagramUtils

from discord_bot import send_error_to_discord

import CustomErrors

warnings.filterwarnings('ignore')

app = Flask(__name__)

# 모델 불러오기
with open('saved_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Label Encoder 생성
label_encoder = LabelEncoder()

# 로거 생성
logger = logging.getLogger()

# mbti
mbti_names = [
    "ENFP",
    "ESFP",
    "INFJ",
    "ISFJ",
    "ISTP",
    "ENFJ",
    "ENTJ",
    "INTJ",
    "INFP",
    "ISFP",
    "ESTP",
    "INTP",
    "ESTJ",
    "ISTJ",
    "ENTP",
    "INTJ",
]
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(mbti_names)

IUtils = InstagramUtils()


def extract_text_instagram(user_name: str):
    """
    사용자의 인스타id로부터 게시글의 텍스트 추출
    :param user_name:
    :return: text: str
    """
    try:
        text = IUtils.post_by_user(user_name)

    except Exception as e:
        raise e

    if len(text) < 1:
        raise RuntimeError("비공개 계정 또는 텍스트가 존재하지 않습니다.")

    return text


def mbti_predict(text: str):
    """
    입력받은 텍스트로 부터 모델을 통한 mbti 예측 및 각 mbti별 확률 계산
    :param text:
    :return: mbti: str
    """
    # 모델을 통한 예측
    dec_func = model.decision_function(text)
    probabilities = np.round(np.exp(dec_func) / np.sum(np.exp(dec_func)) * 100, 2)

    max_prob_index = np.argmax(probabilities)

    # 가장 높은 확률의 mbti 출력
    max_mbti_class = label_encoder.classes_[max_prob_index]
    print(f"Highest probability : {max_mbti_class}")

    # 각 mbti별 확률
    all_predict_dict = {mbti: prob for mbti, prob in zip(label_encoder.classes_, probabilities[0])}
    top_five = dict(sorted(all_predict_dict.items(), key=lambda item: item[1], reverse=True)[:5])

    result_dict = {"mbti": max_mbti_class}
    result_dict.update({"prob": top_five})

    return result_dict


@app.route('/instagram', methods=['GET'])
def predict_by_instagram():
    """
    인스타그램을 통한 mbti예측
    :return:
    """
    # POST 요청에서 데이터 추출
    sns_url = request.args.get("snsUrl")

    print("sns_url: ", sns_url)
    logger.info("Instagram ID: %s" % sns_url)

    # 수집 데이터 기반으로 분류 실행
    try:
        text = extract_text_instagram(sns_url)
        result = mbti_predict(text)

    except CustomErrors.NoPostError as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 400)
        logger.info("error: %s" % message)
        return response
    except CustomErrors.NoAccountError as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 404)
        logger.info("error: %s" % message)
        return response
    except CustomErrors.PrivateAccountError as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 401)
        logger.info("error: %s" % message)
        return response
    except Exception as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 500)
        logger.error("error: %s" % message)
        send_error_to_discord(message)
        return response

    # 결과를 JSON 형식으로 반환
    return jsonify(result)


@app.route('/introduction', methods=['GET'])
def predict_by_introduction():
    """
    자기 소개를 기반으로 mbti 예측
    :return:
    """
    text = request.args.get('text')

    logger.info("Introduction: %s" % text)
    print("introduction: ", text)

    result = mbti_predict([text])

    return jsonify(result)


if __name__ == '__main__':
    app.run()
