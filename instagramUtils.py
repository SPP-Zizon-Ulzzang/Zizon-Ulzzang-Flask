import logging
import os
import re

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import ClientLoginRequired
from googletrans import Translator

import CustomErrors


def remove_special_characters_using_regex(input_string):
    # 정규표현식으로 특수 문자 제거
    pattern = r"[^\w\s]"
    result_string = re.sub(pattern, "", input_string)
    return result_string


class InstagramUtils:
    """인스타그램 데이터 수집을 위한 유틸 클래스"""
    load_dotenv()

    # 로거 설정
    logger = logging.getLogger()

    # 인스타그램 로그인
    INSTA_ID = os.environ.get("INSTA_ID")
    INSTA_PW = os.environ.get("INSTA_PW")
    cl = Client()

    cl.delay_range = [1, 2]

    cl.login(INSTA_ID, INSTA_PW)
    cl.dump_settings("session.json")

    logger.info("Instagram Login %s" % INSTA_ID)
    print("login - ", INSTA_ID)

    def re_login(self):
        """
        재 로그인
        :return:
        """
        self.cl.login(self.INSTA_ID, self.INSTA_PW)
        self.cl.dump_settings("session.json")
        self.logger.info("Instagram Login %s" % self.INSTA_ID)

    def post_by_user(self, user_name):
        """
        사용자 이름을 통한 게시글 조회
        :param user_name:
        :return: text: [str]
        """
        try:
            user_info = self.cl.user_info_by_username(user_name)
            isPirvate = user_info.is_private
            isNoPost = user_info.media_count == 0

            if isPirvate:
                raise CustomErrors.PrivateAccountError("비공개 계정입니다.")
            if isNoPost:
                raise CustomErrors.NoPostError("게시물이 없습니다.")
        except ClientLoginRequired as e:
            raise e
        except CustomErrors.CustomError as e:
            raise e
        except Exception as e:
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

        all_text = remove_special_characters_using_regex(all_text)
        return [all_text.replace("\n", "")]
