import os

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import ClientLoginRequired

import CustomErrors

class InstagramUtils:
    load_dotenv()

    INSTA_ID = os.environ.get("INSTA_ID")
    INSTA_PW = os.environ.get("INSTA_PW")
    cl = Client()
    cl.login(INSTA_ID, INSTA_PW)
    print("login - ", INSTA_ID)

    def post_by_user(self, user_name):
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

        return [all_text]

    def post_by_post_url(self, url):
        # 게시물 텍스트 추출
        code = self.cl.media_pk_from_url(url)
        caption_text = self.cl.media_info(code).caption_text

        return [caption_text]
