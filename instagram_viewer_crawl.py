
import re
from googletrans import Translator
import requests
from bs4 import BeautifulSoup

def remove_special_characters_using_regex(input_string):
    # 정규표현식으로 특수 문자 제거
    pattern = r"[^\w\s]"
    result_string = re.sub(pattern, "", input_string)
    return result_string


def translate_text(original_text):
    # 텍스트 영어로 번역

    # 번역기 생성
    translator = Translator()

    # 번역 (번역전 언어 감지 -> 번역될 언어는 자동으로 영어로 설정됨)
    translated_text = translator.translate(original_text).text

    return translated_text

def instagram_viewer_crawling(username):
    link = "https://www.inststalk.com/user/" + username
    request = requests.get(link)
    html = request.text
    soup = BeautifulSoup(html, 'html.parser')

    post_num = len(soup.find_all(attrs={'class':'description'}))

    all_text = ""
    for x in range(0,post_num):
        post = soup.select(".description")[x].get_text()
        all_text += post

    all_text = remove_special_characters_using_regex(all_text).replace("\n", "")

    # googletrans 글자 5천자 넘어가면 발생하는 에러 해결
    if len(all_text) > 5000:
            all_text = all_text[:4900]

    translated_text = translate_text(all_text)

    print("원본 : ", all_text)
    print("번역결과 : ", translated_text)

    return [translated_text]
