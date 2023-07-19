import os

from dotenv import load_dotenv
from instagrapi import Client

def instagram_login():
    load_dotenv()

    INSTA_ID = os.environ.get("INSTA_ID")
    INSTA_PW = os.environ.get("INSTA_PW")

    cl = Client()
    # 인스타그램 로그인
    cl.login(INSTA_ID, INSTA_PW)

    return cl
class InstagramUtils:
    cl = Client()
    def __int__(self):
        load_dotenv()

        INSTA_ID = os.environ.get("INSTA_ID")
        INSTA_PW = os.environ.get("INSTA_PW")

        # 인스타그램 로그인
        self.cl.login(INSTA_ID, INSTA_PW)

    def post_by_user(self, userName):
        # 인스타 게시물 수 by username(id)
        media_count = self.cl.user_info_by_username(userName).media_count
        media_count = 100 if media_count>100 else media_count

        # username으로 userid(int) 가져오기
        user_id = int(self.cl.user_id_from_username(userName))

        # 게시물 추출
        all_text = ""

        posts = self.cl.user_medias(user_id, media_count)
        for post in posts:
            all_text += post.caption_text

        print("===========================")
        print(all_text)

        return [all_text]


    def post_by_postUrl(self, url):
        # 게시물 텍스트 추출
        code = self.cl.media_pk_from_url(url)
        caption_text = self.cl.media_info(code).caption_text

        return [caption_text]