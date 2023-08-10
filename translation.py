from googletrans import Translator


def translate_text(original_text):
    """
    텍스트 영어로 번역
    :param original_text:
    :return:
    """

    # 번역기 생성
    translator = Translator()

    # 번역 (번역전 언어 감지 -> 번역될 언어는 자동으로 영어로 설정됨)
    translated_text = translator.translate(original_text).text

    return translated_text
