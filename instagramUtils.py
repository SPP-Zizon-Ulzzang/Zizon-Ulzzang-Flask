import datetime
import logging
import os
import re

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import ClientLoginRequired, LoginRequired
from googletrans import Translator

from discord_bot import send_error_to_discord

import CustomErrors


def remove_special_characters_using_regex(input_string):
    # 정규표현식으로 특수 문자 제거
    pattern = r"[^\w\s]"
    result_string = re.sub(pattern, "", input_string)
    return result_string


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


class InstagramUtils:
    """인스타그램 데이터 수집을 위한 유틸 클래스"""
    load_dotenv()

    # 로거 설정
    logger = logging.getLogger()

    cl = Client()

    # 인스타그램 ID, PW
    INSTA_ID = os.environ.get("INSTA_ID")
    INSTA_PW = os.environ.get("INSTA_PW")
    NEXT_INSTA_ID = os.environ.get("NEXT_INSTA_ID")
    NEXT_INSTA_PW = os.environ.get("NEXT_INSTA_PW")

    def __init__(self):
        # 행동 사이 딜레이 설정
        self.cl.delay_range = [1, 2]

        try:
            self.login_user(self.INSTA_ID, self.INSTA_PW)
        except Exception as e:
            send_error_to_discord(
                str(datetime.datetime.now()) + str(e))

    def login_user(self, insta_id, insta_pw):
        """
        인스타그램 로그인
        :return:
        """
        session = self.cl.load_settings("session.json")

        login_via_session = False
        login_via_pw = False

        if session:
            try:
                self.cl.set_settings(session)
                self.cl.login(insta_id, insta_pw)

                # check if session is valid
                try:
                    self.cl.get_timeline_feed()
                except LoginRequired:
                    self.logger.info("Session is invalid, need to login via username and password")

                    old_session = self.cl.get_settings()

                    # use the same device uuids across logins
                    self.cl.set_settings({})
                    self.cl.set_uuids(old_session["uuids"])

                    self.cl.login(insta_id, insta_pw)
                login_via_session = True
            except Exception as e:
                self.logger.info("Couldn't login user using session information: %s" % e)
                send_error_to_discord(
                    str(datetime.datetime.now()) + "Couldn't login user using session information: " + str(e))

        if not login_via_session:
            try:
                self.logger.info("Attempting to login via username and password. username: %s" % insta_id)
                if self.cl.login(insta_id, insta_pw):
                    login_via_pw = True
            except Exception as e:
                self.logger.info("Couldn't login user using username and password: %s" % e)
                send_error_to_discord(
                    str(datetime.datetime.now()) + "Couldn't login user using username and password: " + str(e))

        if not login_via_pw and not login_via_session:
            raise Exception("Couldn't login user with either password or session")

        print("Instagram Login", insta_id, insta_pw)
        self.logger.info("Instagram Login %s" % insta_id)
        send_error_to_discord(str(datetime.datetime.now()) + "Instagram Login - " + str(insta_id))

    def post_by_user(self, user_name):
        """
        사용자 이름을 통한 게시글 조회
        :param user_name:
        :return: text: [str]
        """
        try:
            self.cl.get_timeline_feed()  # 피드 새로고침 후 예외 발생 시 재 로그인
        except (ClientLoginRequired, LoginRequired):
            self.cl.relogin()
        except Exception as e:
            self.logger.error(e)
            send_error_to_discord(str(datetime.datetime.now())+str(e))

        try:
            user_info = self.cl.user_info_by_username(user_name)
            isPirvate = user_info.is_private
            isNoPost = user_info.media_count == 0

            if isPirvate:
                raise CustomErrors.PrivateAccountError("비공개 계정입니다.")
            if isNoPost:
                raise CustomErrors.NoPostError("게시물이 없습니다.")
        except CustomErrors.CustomError as e:
            raise e
        except Exception as e:
            self.logger.error(e)
            raise CustomErrors.NoAccountError("존재하지 않는 계정입니다.")

        # 인스타 게시물 수 by username(id)
        media_count = self.cl.user_info_by_username(user_name).media_count
        media_count = 30 if media_count > 30 else media_count

        # user_name으로 userid(int) 가져오기
        user_id = int(self.cl.user_id_from_username(user_name))

        # 게시물 추출
        all_text = ""

        posts = self.cl.user_medias(user_id, media_count)
        for post in posts:
            all_text += post.caption_text

        # 특수기호 및 개행문자 제거
        all_text = remove_special_characters_using_regex(all_text).replace("\n", "")

        # 비 영문 게시글 영어로 번역
        translated_text = translate_text(all_text)

        print("원본 : ", all_text)
        print("번역결과 : ", translated_text)

        return [translated_text]
