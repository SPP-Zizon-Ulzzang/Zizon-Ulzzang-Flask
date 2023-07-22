import logging
import pickle

from flask import Flask, jsonify, request, make_response
import warnings

from instagrapi.exceptions import LoginRequired

from instagramUtils import InstagramUtils as IUtils
import CustomErrors

warnings.filterwarnings('ignore')

app = Flask(__name__)

# 모델 불러오기
with open('saved_model.pkl', 'rb') as file:
    model = pickle.load(file)

# 인스타그램 유틸 인스턴스 생성
util = IUtils()

# 로거 생성
logger = logging.getLogger()


def extract_text_instagram(user_name: str):
    """
    사용자의 인스타id로부터 게시글의 텍스트 추출
    :param user_name:
    :return: text: str
    """
    try:
        text = util.post_by_user(user_name)
    except Exception as e:
        raise e

    print("====================")
    print("text: ", text)
    logger.info("text: %s" % text)

    if len(text) < 1:
        raise RuntimeError("비공개 계정 또는 텍스트가 존재하지 않습니다.")

    return text


def mbti_predict(text: str):
    """
    입력받은 텍스트로 부터 모델을 통한 mbti 예측
    :param text:
    :return: mbti: str
    """
    # 모델을 통한 예측
    predicted_labels = model.predict(text)

    print("predicted label: ", predicted_labels)

    return predicted_labels[0]


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

    # 세션 확인
    try:
        util.cl.get_timeline_feed()
    except LoginRequired:
        logger.info("Session is invalid, need to login via username and password")

        old_session = util.cl.get_settings()

        util.cl.set_settings({})
        util.cl.set_uuids(old_session["uuids"])

        util.re_login()

    # 수집 데이터 기반으로 분류 실행
    try:
        text = extract_text_instagram(sns_url)
        result = mbti_predict(text)

    except CustomErrors.NoPostError as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 400)
        logger.error("error: %s" % message)
        return response
    except CustomErrors.NoAccountError as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 404)
        logger.error("error: %s" % message)
        return response
    except CustomErrors.PrivateAccountError as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 401)
        logger.error("error: %s" % message)
        return response
    except Exception as e:
        print("error: ", e.args)
        message = str(e.args[0])
        response = make_response(message, 500)
        logger.error("error: %s" % message)
        return response

    response = {
        "mbti": str(result)
    }
    # 결과를 JSON 형식으로 반환
    return jsonify(response)


@app.route('/introduction', methods=['GET'])
def predict_by_introduction():
    """
    자기 소개를 기반으로 mbti 옟 ㄱ
    :return:
    """
    text = request.args.get('text')

    logger.info("Introduction: %s" % text)
    print("introduction: ", text)

    mbti = mbti_predict([text])

    response = {
        "mbti": str(mbti)
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run()
